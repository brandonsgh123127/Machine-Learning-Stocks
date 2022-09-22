import queue

import keras
from V1.data_generator._data_generator import Generator
from pathlib import Path
import os
# import matplotlib.pyplot as plt
from V1.machine_learning.neural_network import load, Network
from V1.machine_learning.neural_network_divergence import load as load_divergence
from V1.data_generator.display_data import Display
import datetime
import threading
import sys
import gc
from V1.threading_impl.Thread_Pool import Thread_Pool
from pandas.tseries.holiday import USFederalHolidayCalendar
import asyncio
from concurrent.futures import ThreadPoolExecutor

class launcher:
    def __init__(self, skip_display: bool = False):
        self._type = None
        if not skip_display:
            self.dis: Display = Display()
        self.skip_display = skip_display
        self.listLock = threading.Lock()
        self.saved_predictions: queue.Queue = queue.SimpleQueue()
        self.listLock = threading.Lock()
        self._executor = ThreadPoolExecutor(4)

    async def display_model(self, nn: keras.models.Model = None, name: str = "relu_multilayer_l2", _has_actuals: bool = False, ticker: str = "spy",
                      color: str = "blue", force_generation=False, unnormalized_data=False, row=0, col=1,
                      data=None, is_divergence=False,
                      skip_threshold: float = 0.05,
                      interval: str = '1d'):
        # Call machine learning model
        if not is_divergence:
            ldata = load(nn,f'{ticker.upper()}', has_actuals=_has_actuals, name=f'{name}',
                         force_generation=force_generation, device_opt='/device:GPU:0', rand_date=False, data=data,
                         interval=interval)
        else:
            ldata = load_divergence(f'{ticker.upper()}', has_actuals=_has_actuals, name=f'{name}',
                                    force_generation=force_generation, device_opt='/device:GPU:0', rand_date=False,
                                    data=data, interval=interval)
        # if skipping display, return only predicted value and last val, as that is what we care about.
        if self.skip_display:
            predict_close = ldata[0]['Close'].iloc[0]
            if isinstance(data, tuple):  # if tuple, take 1st df and get close
                self.saved_predictions.put((ticker, predict_close, data[0]['Close'].iloc[-1]))
                return ticker, predict_close, data[0]['Close'].iloc[-1]
            else:
                self.saved_predictions.put((ticker, predict_close, data['Close'].iloc[-1]))
                return ticker, predict_close, data.iloc[-1]
        # read data for loading into display portion
        with self.listLock:
            self.dis.read_studies_data(ldata[0], ldata[1], ldata[3], ldata[4], ldata[5])
        # display data
        if not _has_actuals:  # if prediction, proceed
            if not unnormalized_data:
                with self.listLock:
                    if not is_divergence:
                        self.dis.display_predict_only(color=f'{color}', row=row, col=col)
                    else:
                        self.dis.display_predict_only(color=f'{color}', row=row, col=col, is_divergence=is_divergence)
            else:
                with self.listLock:
                    self.dis.display_box(ldata[2], has_actuals=_has_actuals) # Display with fib
                    self.dis.display_box(ldata[2], row=1, col=0, has_actuals=_has_actuals, without_fib=True)#Display without fib
                    self.dis.display_box(ldata[2], row=1, col=1, has_actuals=_has_actuals, without_fib=False,only_fib=True)#Display only fib
        else:
            if unnormalized_data:
                with self.listLock:
                    self.dis.display_box(ldata[2], has_actuals=_has_actuals) # display with fib
                    self.dis.display_box(ldata[2], row=1, col=0, has_actuals=_has_actuals, without_fib=True)#Display without fib
                    self.dis.display_box(ldata[2], row=1, col=1, has_actuals=_has_actuals, without_fib=False,only_fib=True)#Display only fib
            else:
                with self.listLock:
                    if not is_divergence:
                        self.dis.display_line(color=f'{color}', row=row, col=col)
                    else:
                        self.dis.display_line(color=f'{color}', row=row, col=col, is_divergence=is_divergence)
        return ticker, ldata[0], ldata[1]


data_gen = Generator()


async def main(nn_dict: dict = {}, ticker: str = "SPY", has_actuals: bool = True, force_generate=False, interval='Daily'):
    listLock = threading.Lock()
    loop = asyncio.get_event_loop()

    launch = launcher()
    if ticker is not None:
        ticker = ticker
    else:
        raise ValueError("Failed to find ticker name!")
    path = Path(os.getcwd()).absolute()

    gen = Generator(ticker.upper(), path, force_generate)
    # if current trading day, set prediction for tomorrow in date name
    dates = []
    # Confirm end date is valid 
    valid_datetime = datetime.datetime.utcnow()
    holidays = USFederalHolidayCalendar().holidays(start=valid_datetime,
                                                   end=(valid_datetime - datetime.timedelta(days=7))).to_pydatetime()
    valid_date = valid_datetime.date()
    if (
            datetime.datetime.utcnow().hour <= 14 and datetime.datetime.utcnow().minute < 30):  # if current time is before 9:30 AM EST, go back a day
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))

    if valid_date in holidays and 0 <= valid_date.weekday() <= 4:  # week day holiday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday() == 5:  # if saturday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday() == 6:  # if sunday
        valid_datetime = (valid_datetime - datetime.timedelta(days=2))
        valid_date = (valid_date - datetime.timedelta(days=2))
    if valid_date in holidays:
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    e_date = valid_date

    n_interval = '1d' if interval == 'Daily' else '1wk' if interval == 'Weekly' else '1mo' if interval == 'Monthly' else '1y' if interval == 'Yearly' else interval

    if '1d' in n_interval:
        dates = (e_date - datetime.timedelta(days=75), e_date)  # month worth of data
    elif '1wk' in n_interval:
        # change end date to a monday before
        cur_day = abs(e_date.weekday())
        if cur_day != 0:
            e_date = e_date - datetime.timedelta(days=cur_day + 2)
        # change begin date to a monday
        begin_date = e_date - datetime.timedelta(days=250)
        begin_day = abs(begin_date.weekday())
        if begin_day != 0:
            begin_date = begin_date - datetime.timedelta(days=begin_day)
        dates = (begin_date, e_date)  # ~5 months
    elif '1mo' in n_interval:
        dates = ((e_date - datetime.timedelta(days=600)).replace(day=1), e_date.replace(day=1))  # ~20 months
    elif '1y' not in n_interval:
        dates = (e_date - datetime.timedelta(days=75), e_date)  # month worth of data

    _has_actuals = has_actuals

    # Generate Data for usage in display_model
    data_task = await loop.run_in_executor(launch._executor,gen.generate_data_with_dates,dates[0], dates[1], False, force_generate, False, n_interval)
    data = await asyncio.gather(data_task)
    data = data[0]

    # BOX PLOT CALL
    box_plot_task = await loop.run_in_executor(launch._executor,launch.display_model,nn_dict["relu_1layer_l2"],"relu_1layer_l2", has_actuals, ticker, 'green', force_generate, True, 0, 0, data, False, 0.05,
                         n_interval)

    #
    # Model_Out_2 LABEL
    if _has_actuals:
        task1 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_2layer_0regularization"],"relu_2layer_0regularization", _has_actuals, ticker, 'green', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
        task2 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_1layer_l2"],"relu_1layer_l2", _has_actuals, ticker, 'black', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
        task3 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_2layer_l1l2"],"relu_2layer_l1l2", _has_actuals, ticker, 'magenta', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
    else:
        task1 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_2layer_0regularization"],"relu_2layer_0regularization", _has_actuals, ticker, 'green', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
        task2 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_1layer_l2"],"relu_1layer_l2", _has_actuals, ticker, 'black', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
        task3 = await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_2layer_l1l2"],"relu_2layer_l1l2", _has_actuals, ticker, 'magenta', force_generate, False, 0, 1, data, False,
                    0.05, n_interval)
    gc.collect()
    await asyncio.gather(box_plot_task, task1, task2, task3)
    launch.dis.fig.canvas.draw()  # draw image before returning
    return launch.dis.fig, launch.dis.axes

async def get_preview_prices(ticker: str, force_generation=False):
    loop = asyncio.get_event_loop()
    try:
        res = loop.run_until_complete(data_gen.generate_quick_data,ticker, force_generation)

        return res
    except Exception as e:
        print(f'[ERROR] No data generated for {ticker}!  Continuing...')
        return 'nan     nan'


async def find_all_big_moves(nn_dict: dict, tickers: list, force_generation=False, _has_actuals: bool = False, percent: float = 0.02,
                       interval: str = 'Daily') -> list:
    thread_pool = Thread_Pool(amount_of_threads=2)
    listLock = threading.Lock()

    launch = launcher(skip_display=True)

    # Confirm end date is valid
    valid_datetime = datetime.datetime.utcnow()
    holidays = USFederalHolidayCalendar().holidays(start=valid_datetime,
                                                   end=(valid_datetime - datetime.timedelta(days=7))).to_pydatetime()
    valid_date = valid_datetime.date()
    if (
            datetime.datetime.utcnow().hour <= 14 and datetime.datetime.utcnow().minute < 30):  # if current time is before 9:30 AM EST, go back a day
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))

    if valid_date in holidays and 0 <= valid_date.weekday() <= 4:  # week day holiday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday() == 5:  # if saturday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday() == 6:  # if sunday
        valid_datetime = (valid_datetime - datetime.timedelta(days=2))
        valid_date = (valid_date - datetime.timedelta(days=2))
    if valid_date in holidays:
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    e_date = valid_date

    n_interval = '1d' if interval == 'Daily' else '1wk' if interval == 'Weekly' else\
        '1mo' if interval == 'Monthly' else\
            '1y' if interval == 'Yearly' else interval

    if '1d' in n_interval:
        dates = (e_date - datetime.timedelta(days=75), e_date)  # month worth of data
    elif '1wk' in n_interval:
        cur_day = abs(e_date.weekday())
        if cur_day != 0:
            e_date = e_date - datetime.timedelta(days=cur_day + 2)

        # change begin date to a monday
        begin_date = e_date - datetime.timedelta(days=250)
        begin_day = abs(begin_date.weekday())
        if begin_day != 0:
            begin_date = begin_date - datetime.timedelta(days=begin_day)

        dates = (begin_date, e_date)  # ~5 months
    elif '1mo' in n_interval:
        dates = ((e_date - datetime.timedelta(days=600)).replace(day=1), e_date.replace(day=1))  # ~20 months
    elif '1y' not in n_interval:
        dates = (e_date - datetime.timedelta(days=75), e_date)  # months worth of data
    path = Path(os.getcwd()).absolute()
    gen = Generator(None, path, force_generation)
    loop = asyncio.get_running_loop()
    task_list = []
    for ticker in tickers:
        try:
            gen.set_ticker(ticker)
            data_task = await loop.run_in_executor(launch._executor,gen.generate_data_with_dates,dates[0], dates[1], False, force_generation, True, n_interval)
            data = loop.run_until_complete(asyncio.gather(data_task))[0]
            # print(data,flush=True)
            task_list.append(await loop.run_in_executor(launch._executor,launch.display_model,
                    nn_dict["relu_2layer_l1l2"],"relu_2layer_l1l2", _has_actuals, ticker, 'green', force_generation, False, 0, 1, data, False,
                    percent, n_interval))
        except Exception as e:
            print(f'[ERROR] Could not generate an NN dataset for {ticker}!  Continuing...', flush=True)
    loop.run_until_complete(asyncio.gather(*task_list))
    saved_predictions: list = []
    launch.saved_predictions.join()
    for prediction in launch.saved_predictions:
        prior_close: int = prediction[2]
        if abs(((prior_close + prediction[1]) / prior_close) - 1) >= percent:
            saved_predictions.append(prediction)
    # After gathering all models, return
    return saved_predictions


if __name__ == "__main__":
    _type = sys.argv[1]
    _has_actuals = sys.argv[3] == 'True'
    _force_generate = sys.argv[4] == 'True'
    loop = asyncio.new_event_loop()
    neural_net = Network(0, 0)
    names: list = ['relu_1layer_l2', 'relu_2layer_0regularization', 'relu_2layer_l1l2', 'relu_2layer_l1l2']
    nn_list: list = [neural_net.load_model(name=name) for name in names]
    nn_dict: dict = {'relu_1layer_l2': nn_list[0],
                          'relu_2layer_0regularization': nn_list[1],
                          'relu_2layer_l1l2': nn_list[2],
                          'relu_2layer_l1l2': nn_list[3]}

    loop.run_until_complete(main(nn_dict=nn_dict,ticker=sys.argv[2], has_actuals=_has_actuals, force_generate=_force_generate,interval='15m'))