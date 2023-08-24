import queue
from pathlib import Path
import os
from typing import Optional

import pandas as pd
from numpy import array

from V1.data_gather.news_scraper import News_Scraper
from V1.data_gather.studies import Studies
import random
from V1.threading_impl.Thread_Pool import Thread_Pool
import threading
import time
import datetime
import sys
import asyncio

'''
    This class allows for unification of data, studies and news for future machine learning training.
    data formatting 
'''


class Generator():
    def __init__(self, ticker=None, path=None, force_generate=False):
        # print(ticker)
        self.studies = Studies(ticker, force_generate=force_generate)
        self.news = News_Scraper(ticker)
        self.thread_pool = Thread_Pool(amount_of_threads=2)
        self.ticker = None
        self.tasks = queue.Queue()
        if ticker is not None:
            self.ticker = ticker
        if path is not None:
            self.path = path
        else:
            self.path = Path(os.getcwd()).absolute()

    async def generate_data(self):
        # studies.__init__()
        with threading.Lock():
            studies = Studies(self.ticker)
            dates = studies.gen_random_dates()
            # Loop until valid data populates
            try:
                if await studies.set_data_from_range(studies.date_set[0], studies.date_set[1],
                                                     _force_generate=True) != 0 or studies.data.isnull().values.any() or len(
                    studies.data) < 16:
                    print(f'[ERROR] Failed to generate data for {self.ticker}')
                    return 1
            except RuntimeError:
                print('[ERROR] Runtime Error when generating data!')
                pass

        try:
            try:
                studies.data = studies.data.drop(['Volume'], axis=1)
            except:
                pass
            # studies.set_data_from_range(dates[0],dates[1])
            self.studies.set_force_generate(True)
            studies.apply_ema("14", self.studies.get_date_difference(dates[0], dates[1]))
            # studies.set_data_from_range(dates[0],dates[1])
            studies.apply_ema("30", self.studies.get_date_difference(dates[0], dates[1]))
            # studies.set_data_from_range(dates[0],dates[1])
        except Exception as e:
            print(f'{str(e)}\n[ERROR] Failed to generate ema studies for {self.ticker}!\n')
            return
        try:
            studies.apply_fibonacci()
            studies.keltner_channels(20, 2.0, None)
        except Exception as e:
            print(f'{str(e)}\n[ERROR] Failed to generate fib/keltner studies for {self.ticker}!\n')
            return
        del studies

        # Generates the P/L and percent of current day

    async def generate_quick_data(self, ticker: str = None, force_generation=False) -> str:
        if ticker is not None:
            self.ticker = ticker
        # When UTC time is past 9AM EST, we would like to stay until UTC goes to the next day
        market_hour = 14 < datetime.datetime.utcnow().hour < 24
        if market_hour:
            start = datetime.datetime.utcnow() - datetime.timedelta(
                days=1)
            end = datetime.datetime.utcnow()
        else:
            start = datetime.datetime.utcnow() - datetime.timedelta(
                days=2)
            end = datetime.datetime.utcnow()
            # If morning time before market open, do last 2 days
            if end.date().weekday() == 1 and datetime.datetime.utcnow().hour < 14:
                end = end - datetime.timedelta(days=1)
                start = start - datetime.timedelta(days=1)
        print(
            f'[INFO] Generating data for {ticker} from {start.strftime("%Y%m%d%H%M")} to {end.strftime("%Y%m%d%H%M")}')
        self.studies.set_force_generate(force_generation)
        print(f"[INFO] Setting data depending on weekday.  Weekday is currently {end.date().weekday()}")
        if end.date().weekday() == 5:  # Saturday
            data = await self.studies.set_data_from_range(start - datetime.timedelta(days=1),
                                                          end, _force_generate=force_generation, ticker=ticker,
                                                          update_self=False)
        elif end.date().weekday() == 6:  # Sunday
            data = await self.studies.set_data_from_range(start - datetime.timedelta(days=2),
                                                          end, _force_generate=force_generation, ticker=ticker,
                                                          update_self=False)
        elif end.date().weekday() == 0:  # monday
            data = await self.studies.set_data_from_range(start - datetime.timedelta(days=3),
                                                          end, _force_generate=force_generation, ticker=ticker,
                                                          update_self=False)
        else:
            data = await self.studies.set_data_from_range(start,
                                                          end, _force_generate=force_generation, ticker=ticker,
                                                          update_self=False)
        if data is None:
            print(f"[ERROR] Couldn't generate data for {ticker}.")
            return 'n/a     n/a'
        try:
            return f'{round(data[["Close"]].iloc[-2:].diff().iloc[1].to_list()[0], 3)}     {round(data[["Close"]].iloc[-2:].pct_change().iloc[1].to_list()[0] * 100, 3)}%'
        except Exception as e:
            print(str(e), f'\n[ERROR] Failed to gather quick data for {ticker}...\n')
            return 'n/a     n/a'

    # split a univariate sequence into samples
    def split_sequence(self, sequence, n_steps):
        X = list()
        for i in range(len(sequence)):
            # find the end of this pattern
            end_ix = i + n_steps
            # check if we are beyond the sequence
            if end_ix > len(sequence) - 1:
                break
            # gather input and output parts of the pattern
            seq_x = sequence[i:end_ix + 1]
            X.append(seq_x)
            # y.append(seq_y)
        return array(X)

    async def generate_data_with_dates(self, date1=None, date2=None, has_actuals=False, force_generate=False,
                                       out=1, skip_db=False, interval='1d', ticker: Optional[str] = None,
                                       opt_fib_vals: list = []):
        split_data: list = []
        split_studies: list = []
        try:
            print("[INFO] Gathering Stock Data.")
            studies = Studies(self.ticker if not ticker else ticker, force_generate=force_generate)
            data_task = studies.set_data_from_range(date1, date2, force_generate, skip_db=skip_db, interval=interval,
                                                   ticker=ticker,has_actuals=has_actuals)
            await data_task
            push_data_to_db_task = studies.push_data_to_db(skip_db=skip_db, interval=interval,
                                                           ticker=ticker, data=studies.data)
            self.tasks.put(push_data_to_db_task) # Push to queue so we can await in the background
            await self.tasks.get()
            # studies.data = studies.data.reset_index()
        except Exception as e:
            print(f'[ERROR] Failed to generate stock data!\r\nException: {e}')
            raise Exception(e)
        # TODO change this such that external functions pass in this value
        n_steps = 20
        data_timesteps_np = self.split_sequence(studies.data.to_numpy(), n_steps=n_steps)
        # Produced tuple of x,y
        for n in range(0, n_steps):
            data_timesteps_df = pd.DataFrame({'Date': data_timesteps_np[n][:, 0],
                                              'Open': data_timesteps_np[n][:, 1],
                                              'High': data_timesteps_np[n][:, 2],
                                              'Low': data_timesteps_np[n][:, 3],
                                              'Close': data_timesteps_np[n][:, 4],
                                              })
            split_data.append(data_timesteps_df)
            split_studies.append(Studies(self.ticker if not ticker else ticker, force_generate=force_generate))
        # Loop until valid data populates
        try:
            studies.data = studies.data.drop(['Volume'], axis=1)
        except:
            pass

        # print(studies.data)
        # For each split data, gather data
        tuple_out: list = []
        for idx, data in enumerate(split_data):
            split_studies[idx].data = data
            # Set data to current split data
            try:
                await split_studies[idx].apply_ema("14", skip_db=skip_db, interval=interval)
            except Exception as e:
                print(f'{str(e)}\n[ERROR] Failed to generate `EMA 14` for {self.ticker if not ticker else ticker}!')
                raise Exception(e)
            try:
                await split_studies[idx].apply_ema("30", skip_db=skip_db, interval=interval)
            except Exception as e:
                print(f'{str(e)}\n[ERROR] Failed to generate `EMA 30` for {self.ticker if not ticker else ticker}!')
                raise Exception(e)
            try:
                await split_studies[idx].apply_fibonacci(skip_db=skip_db, interval=interval, opt_fib_vals=opt_fib_vals)
            except Exception as e:
                print(
                    f'{str(e)}\n[ERROR] Failed to generate `Fibonacci Extensions` for {self.ticker if not ticker else ticker}!')
                raise Exception(e)
            try:
                await split_studies[idx].keltner_channels(20, 2.0, None, skip_db=skip_db, interval=interval)
                # Final join
            except Exception as e:
                print(
                    f'{str(e)}\n[ERROR] Failed to generate `Keltner Channel` for {self.ticker if not ticker else ticker}!')
                raise Exception(e)
            tmp_tuple = (split_studies[idx].data, split_studies[idx].applied_studies,
                         split_studies[idx].fibonacci_extension, split_studies[idx].keltner)
            tuple_out.append(tmp_tuple)  # list of tuplle outputs
        return tuple_out

    def get_ticker(self):
        return self.ticker

    async def set_ticker(self, ticker):
        self.studies.set_indicator(ticker)
        self.news.set_indicator(ticker)
        self.ticker = ticker


def choose_random_ticker(csv_file):
    with open(csv_file) as f:
        ticker = random.choice(f.readlines())
        ticker = ticker[0:ticker.find(',')]
        print(ticker)
        return ticker


def main():
    MAX_TICKERS = 300
    MAX_ITERS = 2
    path = Path(os.getcwd()).absolute()
    for i in range(MAX_TICKERS):
        ticker = choose_random_ticker(f'{path}/data/watchlist/default.csv')
        generator = Generator(ticker, path)

        # Generate data        
        for j in range(MAX_ITERS):
            rc = generator.generate_data()
            while rc == 1:
                rc = generator.generate_data()
                time.sleep(j * (i / (MAX_ITERS / 1.5)) + 0.5)
            time.sleep(j * (i / (MAX_ITERS / 2)) + 1)
        del generator


if __name__ == '__main__':
    main()
    # generator = Generator("SPY",None)
    # print(generator.generate_quick_data())
