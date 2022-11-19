import asyncio
from typing import Optional

from yahoo_fin.stock_info import get_data
import yfinance as yf
from yahoo_fin.options import get_options_chain
import datetime
from pandas_datareader import data as pdr
import twitter
import requests
import random
import os, sys
import threading
import mysql.connector
import time
import xml.etree.ElementTree as ET
from mysql.connector import errorcode
import binascii
from pathlib import Path
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

'''CORE CLASS IMPLEMENTATION--

    Gather class allows for basic functions within other modules, these functions are:
    date retrieval
    stock retrieval
    news retrieval through twitter api
    
'''


class Gather:
    MAX_DATE = datetime.datetime.now().date()
    MIN_DATE = datetime.datetime(2013, 1, 1).date()
    MIN_RANGE = 75  # at least 7 days generated
    MAX_RANGE = 100  # at most 1 month to look at trend
    DAYS_IN_MONTH = {1: 31,
                     2: 28,
                     3: 31,
                     4: 30,
                     5: 31,
                     6: 30,
                     7: 31,
                     8: 31,
                     9: 30,
                     10: 31,
                     11: 30,
                     12: 31}
    search_url = "https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json"

    def __repr__(self):
        return 'stock_data.gather_data object <%s>' % ",".join(self.indicator)

    def __init__(self, indicator=None):
        # Local API Key for twitter account
        self.api = twitter.Api(consumer_key="wQ6ZquVju93IHqNNW0I4xn4ii",
                               consumer_secret="PorwKI2n1VpHznwyC38HV8a9xoDMWko4mOIDFfv2q7dQsFn2uY",
                               access_token_key="1104618795115651072-O3LSWBFVEPENGiTnXqf7cTtNgmNqUF",
                               access_token_secret="by7SUTtNPOYgAws0yliwk9YdiWIloSdv8kYX0YKic28UE",
                               sleep_on_rate_limit="true")
        self.indicator = indicator
        self.data: pdr.DataReader = None
        self.date_set = ()
        self.bearer = "AAAAAAAAAAAAAAAAAAAAAJdONwEAAAAAzi2H1WrnhmAddAQKwveAfRN1DAY%3DdSFsj3bTRnDqqMxNmnxEKTG6O6UN3t3VMtnC0Y7xaGxqAF1QVq"
        self.headers = {"Authorization": "Bearer {0}".format(self.bearer), "content-type": "application/json",
                        'Accept-encoding': 'gzip',
                        'User-Agent': 'twitterdev-search-tweets-python/'}
        self.new_uuid_gen = None
        self.path = Path(os.getcwd()).absolute()
        tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(self.path))
        root = tree.getroot()
        # Connect
        try:
            self.db_con = mysql.connector.connect(
                host="127.0.0.1",
                user=root[0].text,
                password=root[1].text,
                raise_on_warnings=True,
                database='stocks',
                charset='latin1'
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        # Make second connection use for multiple connection threads
        try:
            self.db_con2 = mysql.connector.connect(
                host="127.0.0.1",
                user=root[0].text,
                password=root[1].text,
                raise_on_warnings=True,
                database='stocks',
                charset='latin1'
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        self.cnx = self.db_con.cursor(buffered=True)
        # self.cnx.execute('SHOW TABLES FROM stocks;')

    def set_indicator(self, indicator):
        with threading.Lock():
            self.indicator = indicator

    def get_indicator(self):
        with threading.Lock():
            return self.indicator
            # retrieve pandas_datareader object of datetime

    async def set_data_from_range(self, start_date: datetime.datetime, end_date: datetime.datetime, _force_generate=False,
                            skip_db=False, interval: str = '1d',ticker: Optional[str] = "", update_self = True):
        # Date range utilized for query...
        date_range = [d.strftime('%Y-%m-%d') for d in pd.date_range(start_date, end_date)]  # start/end date list
        is_utilizing_yfinance: bool = False if '1d' in interval or '1wk' in interval or '1m' in interval or '1y' in interval else True

        if not skip_db:
            holidays = USFederalHolidayCalendar().holidays(start=f'{start_date.year}-01-01',
                                                           end=f'{end_date.year}-12-31').to_pydatetime()
            # For each date, verify data is in the specified range by removing any unnecessary dates first
            for date in date_range:
                datetime_date = datetime.datetime.strptime(date, '%Y-%m-%d')
                if datetime_date.weekday() == 5 or datetime_date in holidays:
                    date_range.remove(date)
            # Second iteration needed to delete Sunday dates for some unknown reason...
            for d in date_range:
                datetime_date = datetime.datetime.strptime(d, '%Y-%m-%d')
                if datetime_date.weekday() == 6:
                    date_range.remove(d)
            # iterate through each data row and verify data is in place before continuing...
            new_data = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj. Close'])
            self.cnx = self.db_con.cursor()
            self.cnx.autocommit = True
            check_cache_studies_db_stmt=''
            if '1d' in interval:
                # Before inserting data, check cached data, verify if there is data there...
                check_cache_studies_db_stmt = """SELECT `stocks`.`dailydata`.`date`,`stocks`.`dailydata`.`open`,
                `stocks`.`dailydata`.`high`,`stocks`.`dailydata`.`low`,
                `stocks`.`dailydata`.`close`,`stocks`.`dailydata`.`adj-close`
                 FROM stocks.`dailydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                 ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`dailydata`.`date` >= DATE(%(sdate)s)
                   AND `stocks`.`dailydata`.`date` <= DATE(%(edate)s)
                   ORDER BY stocks.`dailydata`.`date` ASC
                    """
            elif '1wk' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`weeklydata`.`date`,`stocks`.`weeklydata`.`open`,
                `stocks`.`weeklydata`.`high`,`stocks`.`weeklydata`.`low`,
                `stocks`.`weeklydata`.`close`,`stocks`.`weeklydata`.`adj-close`
                 FROM stocks.`weeklydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                 ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`weeklydata`.`date` >= DATE(%(sdate)s)
                   AND `stocks`.`weeklydata`.`date` <= DATE(%(edate)s)
                   ORDER BY stocks.`weeklydata`.`date` ASC
                    """
            elif '1m' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`monthlydata`.`date`,`stocks`.`monthlydata`.`open`,
                `stocks`.`monthlydata`.`high`,`stocks`.`monthlydata`.`low`,
                `stocks`.`monthlydata`.`close`,`stocks`.`monthlydata`.`adj-close`
                 FROM stocks.`monthlydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                 ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`monthlydata`.`date` >= DATE(%(sdate)s)
                   AND `stocks`.`monthlydata`.`date` <= DATE(%(edate)s)
                   ORDER BY stocks.`monthlydata`.`date` ASC
                    """
            elif '1y' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`yearlydata`.`date`,`stocks`.`yearlydata`.`open`,
                `stocks`.`yearlydata`.`high`,`stocks`.`yearlydata`.`low`,
                `stocks`.`yearlydata`.`close`,`stocks`.`yearlydata`.`adj-close`
                 FROM stocks.`yearlydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                 ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`yearlydata`.`date` >= DATE(%(sdate)s)
                   AND `stocks`.`yearlydata`.`date` <= DATE(%(edate)s)
                   ORDER BY stocks.`yearlydata`.`date` ASC
                    """
            else:
                is_utilizing_yfinance = True
                check_cache_studies_db_stmt = f"""SELECT `stocks`.`{interval}data`.`date`,`stocks`.`{interval}data`.`open`,
                `stocks`.`{interval}data`.`high`,`stocks`.`{interval}data`.`low`,
                `stocks`.`{interval}data`.`close`,`stocks`.`{interval}data`.`adj-close`
                 FROM stocks.`{interval}data` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                 ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`{interval}data`.`date` >= DATE(%(sdate)s)
                   AND `stocks`.`{interval}data`.`date` <= DATE(%(edate)s)
                   ORDER BY stocks.`{interval}data`.`date` ASC
                    """

            try:
                check_cache_studies_db_result = self.cnx.execute(check_cache_studies_db_stmt,
                                                                 {'stock': self.indicator.upper() if not ticker else ticker.upper(),
                                                                  'sdate': start_date.strftime('%Y-%m-%d'),
                                                                  'edate': end_date.strftime('%Y-%m-%d')},
                                                                 multi=True)
                # Retrieve date, verify it is in date range, remove from date range
                for result in check_cache_studies_db_result:
                    result = result.fetchall()
                    for res in result:
                        # Convert datetime to str
                        date = datetime.date.strftime(res[0], "%Y-%m-%d")

                        if date is None:
                            print(
                                f'[INFO] No prior data found for {self.indicator.upper()if not ticker else ticker.upper()} from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}... Generating data...!\n',
                                flush=True)
                        else:
                            new_data = new_data.append({'Date': date, 'Open': float(res[1]), 'High': float(res[2]),
                                                        'Low': float(res[3]), 'Close': float(res[4]),
                                                        'Adj. Close': float(res[5]) if not is_utilizing_yfinance else float(res[4])}, ignore_index=True)
                            # check if date is there, if not fail this
                            if date in date_range:
                                date_range.remove(date)
                            else:
                                continue
            except mysql.connector.errors.IntegrityError:  # should not happen
                self.cnx.close()
                pass
            except Exception as e:
                print('[ERROR] Failed to check cached data!\n', str(e))
                self.cnx.close()
                raise mysql.connector.errors.DatabaseError()
        if len(date_range) == 0 and not _force_generate and not skip_db:  # If all dates are satisfied, set data
            if update_self:
                self.data = new_data
                try:
                    self.data['Date'] = pd.to_datetime(self.data['Date'])
                except:
                    print('[INFO] Could not convert Date col to datetime')
            else:
                data = new_data
                try:
                    data['Date'] = pd.to_datetime(data['Date'])
                except:
                    print('[INFO] Could not convert Date col to datetime')

        #
        #
        # Actually gather data
        # if query is not met
        #
        #
        else:
            # if not _force_generate:
            with threading.Lock():
                try:
                    self.cnx.close()
                except:
                    pass
                self.cnx = self.db_con.cursor(buffered=True)
                self.cnx.autocommit = True
                if update_self:
                    self.data = None
                try:
                    if is_utilizing_yfinance:
                        ticker_obj = yf.Ticker(self.indicator.upper() if not ticker else ticker.upper())
                        if update_self:
                            self.data = ticker_obj.history(interval=interval,
                                                           start=((start_date - datetime.timedelta(hours=3)).strftime(
                                                               '%Y-%m-%d') if interval == '5m' else
                                                                   (start_date - datetime.timedelta(hours=18)).strftime(
                                                                      '%Y-%m-%d') if '15m' in interval else
                                                                    (start_date - datetime.timedelta(days=2)).strftime(
                                                                      '%Y-%m-%d') if '30m' in interval else (start_date - datetime.timedelta(
                                                                      days=5)).strftime(
                                                                      '%Y-%m-%d')),
                                                           end=(end_date + datetime.timedelta(days=6)).strftime(
                                                               '%Y-%m-%d'))
                        else:
                            data = ticker_obj.history(interval=interval,
                                                      start=((start_date - datetime.timedelta(hours=3)).strftime(
                                                          '%Y-%m-%d') if interval == '5m' else
                                                             (start_date - datetime.timedelta(hours=18)).strftime(
                                                                 '%Y-%m-%d') if '15m' in interval else
                                                             (start_date - datetime.timedelta(days=2)).strftime(
                                                                 '%Y-%m-%d') if '30m' in interval else (
                                                                         start_date - datetime.timedelta(
                                                                     days=5)).strftime(
                                                                 '%Y-%m-%d')),
                                                      end=(end_date + datetime.timedelta(days=6)).strftime('%Y-%m-%d'))

                    else:
                        if update_self:
                            self.data = get_data(self.indicator.upper() if not ticker else ticker.upper(), start_date=start_date.strftime("%Y-%m-%d"),
                                         end_date=(end_date + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                                         interval=interval)
                        else:
                            data = get_data(self.indicator.upper() if not ticker else ticker.upper(), start_date=start_date.strftime("%Y-%m-%d"),
                                         end_date=(end_date + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                                         interval=interval)

                except AssertionError as a:
                    raise AssertionError(
                        f'[ERROR] Failed to gather data for specified range.  This is most likely due to stock not existing at this point!\nError:\n{str(a)}')
                except Exception as e:
                    retries = 1
                    max_retries = 4
                    while retries <= max_retries:
                        print(
                            f'[WARN] Failed to gather data for {self.indicator.upper() if not ticker else ticker.upper()}! {retries}/{max_retries} Retr(ies)...\n\tException: {e}')
                        retries = retries + 1
                        time.sleep(2 * (retries / 1.33))
                        try:
                            if is_utilizing_yfinance:
                                ticker_obj = yf.Ticker(self.indicator.upper() if not ticker else ticker.upper())
                                if update_self:
                                    self.data = ticker_obj.history(interval=interval,
                                                                   start=((start_date - datetime.timedelta(
                                                                       hours=3)).strftime(
                                                                       '%Y-%m-%d') if interval == '5m' else
                                                                          (start_date - datetime.timedelta(
                                                                              hours=18)).strftime(
                                                                              '%Y-%m-%d') if '15m' in interval else
                                                                          (start_date - datetime.timedelta(
                                                                              days=2)).strftime(
                                                                              '%Y-%m-%d') if '30m' in interval else (
                                                                              start_date - datetime.timedelta(
                                                                              days=4)).strftime(
                                                                          '%Y-%m-%d') if '60m' in interval else(
                                                                                      start_date - datetime.timedelta(
                                                                                  days=5)).strftime(
                                                                              '%Y-%m-%d')),
                                                                   end=(end_date + datetime.timedelta(days=6)).strftime(
                                                                       '%Y-%m-%d'))
                                else:
                                    data = ticker_obj.history(interval=interval,
                                                              start=(
                                                                  (start_date - datetime.timedelta(hours=3)).strftime(
                                                                      '%Y-%m-%d') if interval == '5m' else
                                                                  (start_date - datetime.timedelta(hours=18)).strftime(
                                                                      '%Y-%m-%d') if '15m' in interval else
                                                                  (start_date - datetime.timedelta(days=2)).strftime(
                                                                      '%Y-%m-%d') if '30m' in interval else (
                                                                              start_date - datetime.timedelta(
                                                                          days=4)).strftime(
                                                                      '%Y-%m-%d') if '60m' in interval else
                                                                  (start_date - datetime.timedelta(days=2)).strftime(
                                                                      '%Y-%m-%d')),
                                                              end=(end_date + datetime.timedelta(days=6)).strftime(
                                                                  '%Y-%m-%d'))

                            else:
                                if update_self:
                                    self.data = get_data(self.indicator.upper() if not ticker else ticker.upper(), start_date=start_date.strftime("%Y-%m-%d"),
                                                     end_date=(end_date + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                                                     interval=interval)
                                else:
                                    data = get_data(self.indicator.upper() if not ticker else ticker.upper(),
                                                         start_date=start_date.strftime("%Y-%m-%d"),
                                                         end_date=(end_date + datetime.timedelta(days=6)).strftime(
                                                             "%Y-%m-%d"),
                                                         interval=interval)

                            break
                        except AssertionError as a:
                            raise Exception(
                                f'[ERROR] Failed to gather data for specified range.  This is most likely due to stock not existing at this point!\nError:\n{str(a)}')
                        except KeyError as ke:
                            raise Exception(f'[ERROR] specific key could not be retrieved in order to complete request for {self.indicator}'+
                                            f' from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}!\n{str(ke)}')
                    if retries > max_retries:
                        print('[ERROR] Failed to gather data!',flush=True)
                        raise Exception()
                    else:
                        pass
                if update_self:
                    if type(self.data) is pd.DataFrame and self.data.empty:
                        print(f'[ERROR] Data returned for {self.indicator if not ticker else ticker.upper()} is empty!')
                        return 1
                else:
                    if type(data) is pd.DataFrame and data.empty:
                        print(f'[ERROR] Data returned for {self.indicator if not ticker else ticker.upper()} is empty!')
                        return 1

                if not skip_db:
                    # Retrieve query from database, confirm that stock is in database, else make new query
                    select_stmt = "SELECT `id` FROM stocks.stock WHERE stock like %(stock)s"
                    resultado = self.cnx.execute(select_stmt, {'stock': self.indicator if not ticker else ticker.upper()}, multi=True)
                    for result in resultado:
                        # print(len(result.fetchall()))
                        # Query new stock, id
                        res = result.fetchall()
                        if len(res) == 0:
                            insert_stmt = """INSERT INTO stocks.stock (id, stock) 
                                        VALUES (AES_ENCRYPT(%(stock)s, %(stock)s),%(stock)s)"""
                            try:
                                insert_resultado = self.cnx.execute(insert_stmt, {'stock': f'{self.indicator.upper() if not ticker else ticker.upper()}'},
                                                                    multi=True)
                                self.db_con.commit()
                            except mysql.connector.errors.IntegrityError as e:
                                print('[ERROR] Integrity Error.')
                                pass
                            except Exception as e:
                                print(f'[ERROR] Failed to insert stock named {self.indicator.upper() if not ticker else ticker.upper()} into database!\n',
                                      str(e))
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
                        else:
                            for r in res:
                                self.new_uuid_gen = binascii.b2a_hex(str.encode(str(r[0]), "utf8"))
                try:
                    if update_self:
                        self.data['Date'] or self.data['Datetime']
                    else:
                        data['Date'] or data['Datetime']
                except KeyError or NotImplementedError:
                    try:
                        if update_self:
                            self.data['Date'] = self.data.index
                            self.data = self.data.reset_index()
                        else:
                            data['Date'] = data.index
                            data = data.reset_index()
                    except Exception as e:
                        print('[Error] Failed to add \'Date\' column into data!\n{}'.format(str(e)))
                # Rename rows back to original state
                try:
                    if update_self:
                        self.data = self.data.transpose().drop(['ticker'])
                    else:
                        data = data.transpose().drop(['ticker'])
                except:
                    pass
                if update_self:
                    self.data = self.data.transpose().rename(
                    columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "adjclose": "Adj Close",
                             "volume": "Volume"})
                else:
                    data = data.transpose().rename(
                    columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "adjclose": "Adj Close",
                             "volume": "Volume"})

                try:
                    if not is_utilizing_yfinance:
                        if update_self:
                            self.data['Date'] = pd.to_datetime(self.data['Date'])
                        else:
                            data['Date'] = pd.to_datetime(data['Date'])
                    else:
                        if update_self:
                            self.data = self.data.rename(columns={'Datetime':'Date'})
                            self.data = self.data.drop(['Datetime'],axis=0).transpose()
                            self.data['Adj Close'] = self.data.loc[:, 'Close']
                            if self.data.iloc[-1]['Date'] == self.data.iloc[-2]['Date']:
                                print('[INFO] Duplicate date detected... Removing right after gather.')
                                self.data = self.data.drop(self.data.index[-1])
                            # Remove latest data point if hour is 4PM EST
                            try:
                                contains_16 = self.data.iloc[-1]['Date'].hour == 16
                                if contains_16:
                                    print('[INFO] Date with 16:00 in time... Removing right after gather.')
                                    self.data = self.data.drop(self.data.index[-1])
                            except Exception as e:
                                print(e)
                        else:
                            data = data.rename(columns={'Datetime':'Date'})
                            data = data.drop(['Datetime'],axis=0).transpose()
                            data['Adj Close'] = data.loc[:, 'Close']
                            if data.iloc[-1]['Date'] == data.iloc[-2]['Date']:
                                print('[INFO] Duplicate date detected... Removing right after gather.')
                                data = data.drop(data.index[-1])
                            # Remove latest data point if hour is 4PM EST
                            try:
                                contains_16 = data.iloc[-1]['Date'].hour == 16
                                if contains_16:
                                    print('[INFO] Date with 16:00 in time... Removing right after gather.')
                                    data = data.drop(data.index[-1])
                            except Exception as e:
                                print(e)
                    if update_self:
                        # Remove element if not 1d and value is NaN
                        try:
                            contains_nan = self.data['Open'].isnull().values.any()
                            if contains_nan:
                                nan_row = self.data[self.data['Open'].isnull()].index.values.astype(int)[0]
                                print('[INFO] Date contains NaN value... Removing right after gather.')
                                self.data = self.data.drop([nan_row])
                        except Exception as e:
                            print(e)
                    else:
                        # Remove element if not 1d and value is NaN
                        try:
                            contains_nan = data['Open'].isnull().values.any()
                            if contains_nan:
                                nan_row = data[data['Open'].isnull()].index.values.astype(int)[0]
                                print('[INFO] Date contains NaN value... Removing right after gather.')
                                data = data.drop([nan_row])
                        except Exception as e:
                            print(e)



                except Exception as e:
                    print('[INFO] Could not convert Date col to datetime', str(e))
                if is_utilizing_yfinance:
                    if update_self:
                        try:
                            self.data = self.data.drop(['Dividends'],axis=1)
                        except Exception:
                            pass
                        try:
                            self.data = self.data.drop(['index'],axis=1)
                        except:
                            pass
                        try:
                            self.data = self.data.drop(['Stock Splits'],axis=1)
                        except:
                            pass
                    else:
                        try:
                            data = data.drop(['Dividends'],axis=1)
                        except Exception:
                            pass
                        try:
                            data = data.drop(['index'],axis=1)
                        except:
                            pass
                        try:
                            data = data.drop(['Stock Splits'],axis=1)
                        except:
                            pass
                if not skip_db:
                    # Append dates to database
                    for index, row in self.data.iterrows() if update_self else data.iterrows():
                        if '1d' in interval:
                            insert_date_stmt = """REPLACE INTO `stocks`.`dailydata` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                            VALUES (AES_ENCRYPT(%(data_id)s, %(stock)s), AES_ENCRYPT(%(stock)s, %(stock)s),
                            DATE(%(Date)s),%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                        elif '1wk' in interval:
                            insert_date_stmt = """REPLACE INTO `stocks`.`weeklydata` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                            VALUES (AES_ENCRYPT(%(data_id)s, %(stock)s), AES_ENCRYPT(%(stock)s, %(stock)s),
                            DATE(%(Date)s),%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                        elif '1m' in interval:
                            insert_date_stmt = """REPLACE INTO `stocks`.`monthlydata` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                            VALUES (AES_ENCRYPT(%(data_id)s, %(stock)s), AES_ENCRYPT(%(stock)s, %(stock)s),
                            DATE(%(Date)s),%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                        elif '1y' in interval:
                            insert_date_stmt = """REPLACE INTO `stocks`.`yearlydata` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                            VALUES (AES_ENCRYPT(%(data_id)s, %(stock)s), AES_ENCRYPT(%(stock)s, %(stock)s),
                            DATE(%(Date)s),%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                        else:
                            insert_date_stmt = f"""REPLACE INTO `stocks`.`{interval}data` (`data-id`, `stock-id`, `date`,`open`,high,low,`close`,`adj-close`) 
                            VALUES (AES_ENCRYPT(%(data_id)s, %(stock)s), AES_ENCRYPT(%(stock)s, %(stock)s),
                            %(Date)s,%(Open)s,%(High)s,%(Low)s,%(Close)s,%(Adj Close)s)"""
                        try:
                            # print(row.name)
                            if is_utilizing_yfinance:
                                insert_date_resultado = self.cnx.execute(insert_date_stmt, {
                                    'data_id': f'{self.indicator if not ticker else ticker.upper()}{row["Date"].strftime("%Y-%m-%d %H:%M:%S")}',
                                    'stock': f'{self.indicator.upper() if not ticker else ticker.upper()}',
                                    'Date': row['Date'].strftime("%Y-%m-%d %H:%M:%S"),
                                    'Open': row['Open'],
                                    'High': row['High'],
                                    'Low': row['Low'],
                                    'Close': row['Close'],
                                    'Adj Close': row['Adj Close']}, multi=True)
                            else:
                                insert_date_resultado = self.cnx.execute(insert_date_stmt, {
                                    'data_id': f'{self.indicator if not ticker else ticker.upper()}{row["Date"].strftime("%Y-%m-%d")}',
                                    'stock': f'{self.indicator.upper() if not ticker else ticker.upper()}',
                                    'Date': row['Date'].strftime("%Y-%m-%d"),
                                    'Open': row['Open'],
                                    'High': row['High'],
                                    'Low': row['Low'],
                                    'Close': row['Close'],
                                    'Adj Close': row['Adj Close']}, multi=True)

                        except mysql.connector.errors.IntegrityError as e:
                            pass
                        except Exception as e:
                            # print(self.data)
                            print(
                                f'[ERROR] Failed to insert date for {self.indicator if not ticker else ticker.upper()} into database!\nDebug Info:{row}\n',
                                str(e))
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                        try:
                            self.db_con.commit()
                        except Exception as e:
                            print('[Error] Could not commit changes for insert day data!\nReason:\n', str(e))
        try:
            self.cnx.close()
        except:
            pass
        return self.data if update_self else data

    def get_option_data(self, date: datetime.date = None):
        with threading.Lock():
            try:
                # sys.stdout = open(os.devnull, 'w')
                options = get_options_chain(self.indicator, date.strftime('%Y-%m-%d'))
                """
                ['Contract Name', 'Last Trade Date', 'Strike', 'Last Price', 'Bid',
       'Ask', 'Change', '% Change', 'Volume', 'Open Interest',
       'Implied Volatility']
                """
                put_opts = options['puts']
                call_opts = options['calls']
                put_strike_prices = put_opts['Strike'].to_numpy()
                put_contract_name = put_opts['Contract Name'].to_numpy()
                call_strike_prices = call_opts['Strike'].to_numpy()
                call_contract_name = call_opts['Contract Name'].to_numpy()
                put_bid = put_opts['Last Price'].to_numpy()
                call_bid = call_opts['Last Price'].to_numpy()
                price_dict = {}  # used to store only 1 time values, just in case

                # Gather all available options within 4 percent of the current price of the stock
                for idx, strike in enumerate(call_strike_prices):
                    # If close value deducted 4 percent is less than the value
                    # and close value added 4 percent is greater than value
                    if (self.data['Close'].iloc[-1] - self.data['Close'].iloc[-1] * 0.04) < strike and (
                            self.data['Close'].iloc[-1] + self.data['Close'].iloc[-1] * 0.04) > strike:
                        price_dict[f'{strike}'] = ((put_contract_name[idx], strike, put_bid[idx]),)
                # Gather all available options within 4 percent of the current price of the stock
                for idx, strike in enumerate(call_strike_prices):
                    # If close value deducted 4 percent is less than the value
                    # and close value added 4 percent is greater than value
                    if (self.data['Close'].iloc[-1] - self.data['Close'].iloc[-1] * 0.04) < strike and (
                            self.data['Close'].iloc[-1] + self.data['Close'].iloc[-1] * 0.04) > strike:
                        try:
                            price_dict[f'{strike}'] = price_dict[f'{strike}'] + (
                                (call_contract_name[idx], strike, call_bid[idx]),)
                        except:
                            price_dict[f'{strike}'] = ((call_contract_name[idx], strike, call_bid[idx]),)
                print(price_dict.values())
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(str(e))
                time.sleep(2)  # Sleep since API does not want to communicate
        return 0

    # Generate random date for data generation
    def gen_random_dates(self):
        with threading.Lock():
            # Get a random date for generation based on min/max date
            d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p'), '%m/%d/%Y %I:%M %p')
            d1 = datetime.datetime.strptime('1/1/2007 1:00 AM', '%m/%d/%Y %I:%M %p')
            # get time diff then get time in seconds
            delta = d2 - d1
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            # append seconds to get a start date
            random_second = random.randrange(int_delta)
            start = d1 + datetime.timedelta(seconds=random_second)
            end = start + datetime.timedelta(days=390)
            self.date_set = (start, end)
            return self.date_set

    def get_date_difference(self, date1: datetime.datetime = None, date2: datetime.datetime = None) -> object:
        with threading.Lock():
            if date1 is None:
                return (self.date_set[0] - self.date_set[1]).days
            else:
                return (date2 - date1).days

    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self, query):
        response = requests.post(self.search_url, json=query, headers=self.headers)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    d = Gather()
    loop.run_until_complete(d.set_data_from_range(start_date=datetime.datetime.utcnow().date() - datetime.timedelta(days=3),end_date=datetime.datetime.utcnow().date(),_force_generate=False,interval='15m',ticker='spy'))
    print(d.data)
# d.get_option_data(datetime.date(year=2021,month=11,day=12))
