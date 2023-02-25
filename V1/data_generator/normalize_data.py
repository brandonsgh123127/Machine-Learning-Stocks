import asyncio
import sys
from pathlib import Path
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer as SKNormalizer
import mysql.connector
from mysql.connector import errorcode
import xml.etree.ElementTree as ET
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
import random
from V1.data_generator._data_generator import Generator

'''
Class that takes in studies and stock data, then transforms the data into a new dataframe.

This frame then gets normalized and outputted.
'''


class Normalizer():
    def __init__(self, ticker=None, force_generate=False):
        self.data = pd.DataFrame()
        self.studies = pd.DataFrame(columns=['ema14', 'ema30'])
        self.normalized_data = pd.DataFrame()
        self.unnormalized_data = pd.DataFrame()
        self.path = Path(os.getcwd()).absolute()
        self.min_max = MinMaxScaler(feature_range=(0,1))
        self.normalizer = SKNormalizer()
        self.gen = Generator(ticker=ticker, force_generate=force_generate)
        self.studies = None
        self.data = None
        self.fib = None
        self.keltner = None
        '''
        Utilize a config file to establish a mysql connection to the database
        '''
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
                raise mysql.connector.custom_error_exception
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                raise mysql.connector.custom_error_exception
            else:
                print(err)
                raise Exception
        self.cnx = self.db_con.cursor(buffered=True)
        self.cnx.autocommit = True

    # Helper function used for appending new elements to a dataframe element via lambda call
    @staticmethod
    def append_data(struct: pd.DataFrame, label: str, val):
        struct = struct.append({label: val}, ignore_index=True)
        return struct

    '''
        Utilize mysql to gather data.  Gathers stock data from table.
    '''

    async def mysql_read_data(self, ticker, date=None, out=1, force_generate=False, skip_db=False,interval='1d', opt_fib_vals=[]):
        try:
            self.cnx = self.db_con.cursor(buffered=True)
            self.cnx.autocommit = True
            # If string, convert to datetime.datetime                
            valid_datetime = datetime.datetime.now()
            if date is None:
                # Verify date before proceeding 
                holidays = USFederalHolidayCalendar().holidays(start=valid_datetime - datetime.timedelta(days=40),
                                                               end=valid_datetime).to_pydatetime()
                valid_date = valid_datetime.date()
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
                initial_date = valid_datetime
            else:
                initial_date = date
            await self.gen.set_ticker(ticker)
            vals = await self.gen.generate_data_with_dates(initial_date - datetime.timedelta(days=150 if '1d' in interval else\
                                    300 if '1wk' in interval else\
                                    600 if '1mo' in interval else\
                                    30 if interval =='5m' else\
                                    40 if '15m' in interval else\
                                    50 if '30m' in interval else\
                                    75 if '60m' in interval else 40), initial_date,
                                                     force_generate=force_generate, out=out,skip_db=skip_db, interval=interval,ticker=ticker, opt_fib_vals=opt_fib_vals)
            self.studies = vals[1]
            self.data = vals[0]
            self.fib = vals[2]
            self.keltner = vals[3]
            del vals
        except Exception as e:
            print(
                f'[ERROR] Failed to retrieve data points for {ticker} from {initial_date.strftime("%Y-%m-%d")} to {(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}!\n',
                str(e))
            raise AssertionError
        except:
            print(
                f'[ERROR] Failed to retrieve data points for {ticker} from {initial_date.strftime("%Y-%m-%d")} to {(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}!\n')
            raise AssertionError
        self.cnx.close()
        return

    def reset_data(self):
        del self.studies,self.data,self.fib,self.keltner
        self.studies = None
        self.data = None
        self.fib = None
        self.keltner = None

    '''
        utilize mysql to retrieve data and study data for later usage...
    '''

    def read_data(self, ticker, rand_dates=False, out=1, skip_db=False, interval='1d', opt_fib_vals=[]):
        if rand_dates:
            # Get a random date for generation based on min/max date
            d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p'), '%m/%d/%Y %I:%M %p')
            d1 = datetime.datetime.strptime('1/1/2007 1:00 AM', '%m/%d/%Y %I:%M %p') if interval == '1d' or interval == '1m' or interval == '1wk' else\
                datetime.datetime.now() - datetime.timedelta(days=730) if interval == '30m' or interval == '60m' or interval == '1h' or interval == '4h' else \
                    datetime.datetime.now() - datetime.timedelta(days=50)
            # get time diff then get time in seconds
            delta = d2 - d1
            # print(delta.days,delta.seconds)
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            # append seconds to get a start date
            random_second = random.randrange(int_delta)
            date = d1 + datetime.timedelta(seconds=random_second)
        else:
            date = None
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.mysql_read_data(ticker, date=date, out=out,
                                                         skip_db=skip_db,interval=interval,opt_fib_vals=opt_fib_vals))
        except Exception as e:
            print('[ERROR] Failed to read data!\n', str(e))
            raise RuntimeError(f'[ERROR] Failed to read data!',e)
        try:
            self.data = self.data.drop(['Adj Close'], axis=1)
        except:
            pass
        try:
            self.data = self.data.drop(['Date'], axis=1)
        except:
            pass
        try:
            self.data = self.data.drop(['index'], axis=1)
            self.data = self.data.drop(['level_0'], axis=1)
        except:
            pass
        pd.set_option("display.max.columns", None)

    def convert_derivatives(self, out : int =1):
        data = self.data
        try:
            data = data.drop(columns={'Date'})
        except:
            pass
        try:
            data = data.drop(columns={'index'})
        except:
            pass
        data = data.astype(np.float_)
        self.studies = self.studies.astype(np.float_)
        try:
            self.keltner = self.keltner.astype(np.float_)
        except:
            print('[INFO] Couldn\'t convert keltner to type <float>')
        try:
            self.fib = self.fib.astype(np.float_)
        except:
            print('[INFO] Couldn\'t convert fibonacci sequence to type <float>')
        self.normalized_data = pd.DataFrame((), columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                                         'Close Fib1 Distance','Close Fib2 Distance', 'Num Consec Candle Dir',
                                                         'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
                                                         'Open',
                                                         'Close'] if out==1 else\
                                                ['Last2Volume Cur Volume Diff','Open Upper Kelt Diff',
                                                 'Open Lower Kelt Diff','High Upper Kelt Diff',
                                                 'High Lower Kelt Diff','Low Upper Kelt Diff',
                                                 'Low Lower Kelt Diff','Close Upper Kelt Diff',
                                                 'Close Lower Kelt Diff','EMA 14 30 Diff',
                                                 'Base Fib High Diff','Base Fib Low Diff',
                                                 'Next1 Fib High Diff','Next1 Fib Low Diff',
                                                 'Next2 Fib High Diff','Next2 Fib Low Diff',
                                                 'Open','High','Low','Close',
                                                 'Last3High Base Fib','Last3Low Base Fib',
                                                 'Last3High Next1 Fib','Last3Low Next1 Fib',
                                                 'Last3High Next2 Fib','Last3Low Next2 Fib']if out ==2 else \
                                                ['Upper Kelt',
                                                'Lower Kelt','Middle Kelt','EMA 14','EMA 30',
                                                'Base Fib', 'Next1 Fib', 'Next2 Fib',
                                                'Open','High','Low','Close',
                                                'Last3High','Last3Low'] if out == 3 or out == 4 else [])
        if out == 1: # Do legacy model data generation for 14 days worth of stuff
            target_fib1 = None
            target_fib2 = None
            last_3 = data['Close'].iloc[-3:]
            last_3_avg_close = last_3.mean()
            i = 0
            j = 0
            direction = ''
            if self.fib['0.273'].iloc[-1] < self.fib['0.283'].iloc[-1]: # get fib direction
                direction = "+"
            else:
                direction = "-"
            for index,item in self.fib.items():
                if direction == "+": # Check if avg is greater than fib val, record
                    if last_3_avg_close > item.iloc[-1]:
                        i = item.iloc[-1]
                    else:
                        j = item.iloc[-1]
                        break
                else:
                    if last_3_avg_close < item.iloc[-1]:
                        i = item.iloc[-1]
                    else:
                        j = item.iloc[-1]
                        break
            target_fib2 = j
            target_fib1 = i
            for index, row in data.iterrows():
                try:
                    if index == 0:
                        self.normalized_data.loc[index, "Open"] = 0
                        self.normalized_data.loc[index, "Close"] = 0
                        self.normalized_data.loc[index, "Close EMA14 Distance"] = data.at[index, "Close"] - self.studies.at[index, 'ema14']
                        self.normalized_data.loc[index, "Close EMA30 Distance"] = data.at[index, "Close"] - self.studies.at[index, 'ema30']
                        # get upwards/downwards dir for for-loop
                        dir = '-'
                        if row['Open'] < row['Close']:  # If green day
                            dir = '+'
                        count_consec_candles = 0
                        if dir == '-':
                            if row['Open'] > row['Close']:  # Green day
                                count_consec_candles = count_consec_candles + 1
                        else:
                            if row['Open'] < row['Close']:  # Red day
                                count_consec_candles = count_consec_candles + 1
                        self.normalized_data.loc[
                            0, "Num Consec Candle Dir"] = count_consec_candles  # Idea is that the more consecutive, more confident
                        self.normalized_data.loc[index, "Close Fib1 Distance"] = data.at[index, "Close"] - target_fib1
                        self.normalized_data.loc[index, "Close Fib2 Distance"] = data.at[index, "Close"] - target_fib2
                        self.normalized_data.loc[index, "Upper Keltner Close Diff"] = (
                                data.at[index, 'Close'] - self.keltner.at[index, "upper"])
                        self.normalized_data.loc[index, "Lower Keltner Close Diff"] = (
                                data.at[index, 'Close'] - self.keltner.at[index, "lower"])
                    else:
                        self.normalized_data.loc[index, "Close"] = ((data.at[index, "Close"] - data.at[
                                                                            index - 1, "Close"]))
                        self.normalized_data.loc[index, "Open"] = ((data.at[index, "Open"] - data.at[
                                                                          index - 1, "Open"]))
                        if dir == '-':
                            if row['Open'] > row['Close']:  # Green day
                                count_consec_candles = count_consec_candles + 1
                            else:
                                count_consec_candles = 0
                        else:
                            if row['Open'] < row['Close']:  # Red day
                                count_consec_candles = count_consec_candles + 1
                            else:
                                count_consec_candles = 0
                        # get upwards/downwards dir for for-loop
                        dir = '-'
                        if row['Open'] < row['Close']:  # If green day
                            dir = '+'
                        self.normalized_data.loc[
                            index, "Num Consec Candle Dir"] = count_consec_candles  # Idea is that the more consecutive, more confident
                        self.normalized_data.loc[index, "Close Fib1 Distance"] = data.at[index, "Close"] - target_fib1
                        self.normalized_data.loc[index, "Close Fib2 Distance"] = data.at[index, "Close"] - target_fib2
                        self.normalized_data.loc[index, "Upper Keltner Close Diff"] = (
                                self.keltner.at[index, "upper"] - data.at[index, 'Close'])
                        self.normalized_data.loc[index, "Lower Keltner Close Diff"] = (
                                self.keltner.at[index, "lower"] - data.at[index, 'Close'])
                        self.normalized_data.loc[index, "Close EMA14 Distance"] = data.at[index, "Close"] - self.studies.at[index, 'ema14']
                        self.normalized_data.loc[index, "Close EMA30 Distance"] = data.at[index, "Close"] - self.studies.at[index, 'ema30']
                except Exception as e:
                    raise AssertionError(f'[ERROR] Failed normalization!\nCurrent Data: \n{self.data}\nCurrent normalized data:\n{self.normalized_data}')
        elif out == 2: # New model - 3 days worth of generation for 26 cols...
            third_last = data.iloc[-1]
            last_3_high = data['High'].iloc[-3:].mean()
            last_3_low = data['Low'].iloc[-3:].mean()
            i = 0
            j = 0
            k = 0
            if self.fib['0.273'].iloc[-1] < self.fib['0.283'].iloc[-1]: # get fib direction
                direction = "+"
            else:
                direction = "-"
            try:
                save_point = 0
                for index,item in self.fib.items():
                    if direction == "+": # Check if avg is greater than fib val, record
                        if third_last['Close'] > item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_high < item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
                    else: # Negative direction
                        if third_last['Close'] < item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_low > item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(fname, exc_type, exc_obj, exc_tb.tb_lineno)
                print(f'[ERROR] Failed to iterate through fibonacci to find key fib points...\n{str(e)}')
            next1_fib = j
            next2_fib = k
            base_fib1 = i
            if next2_fib == 0:
                next2_fib = next1_fib
                next1_fib = save_point
            for index, row in data.iterrows():
                try:
                    if index <= 1:
                        last_3_high = data['High'].iloc[index]
                        last_3_low = data['Low'].iloc[index]
                        last_2_volume = data['Volume'].iloc[index]
                        self.normalized_data.loc[index, "Last2Volume Cur Volume Diff"] = last_2_volume
                    elif index < 3: # If not sufficient amount of days surpassed, do this
                        last_3_high = data['High'].iloc[:index].mean()
                        last_3_low = data['Low'].iloc[:index].mean()
                        last_2_volume = data['Volume'].iloc[:index].mean()
                        self.normalized_data.loc[index, "Last2Volume Cur Volume Diff"] = last_2_volume
                    else:
                        last_3_high = data['High'].iloc[index-3:index].mean()
                        last_3_low = data['Low'].iloc[index-3:index].mean()
                        last_2_volume = data['Volume'].iloc[index-3:index].mean()
                    self.normalized_data.loc[index, "Last2Volume Cur Volume Diff"] = last_2_volume
                    self.normalized_data.loc[index, "Open Upper Kelt Diff"] = data.at[index, "Open"] - self.keltner.at[index, "upper"]
                    self.normalized_data.loc[index, "Open Lower Kelt Diff"] = data.at[index, "Open"] - self.keltner.at[index, "lower"]
                    self.normalized_data.loc[index, "High Upper Kelt Diff"] = data.at[index, "High"] - self.keltner.at[index, "upper"]
                    self.normalized_data.loc[index, "High Lower Kelt Diff"] = data.at[index, "High"] - self.keltner.at[index, "lower"]
                    self.normalized_data.loc[index, "Low Upper Kelt Diff"] = data.at[index, "Low"] - self.keltner.at[index, "upper"]
                    self.normalized_data.loc[index, "Low Lower Kelt Diff"] = data.at[index, "Low"] - self.keltner.at[index, "lower"]
                    self.normalized_data.loc[index, "Close Upper Kelt Diff"] = data.at[index, "Close"] - self.keltner.at[index, "upper"]
                    self.normalized_data.loc[index, "Close Lower Kelt Diff"] = data.at[index, "Close"] - self.keltner.at[index, "lower"]
                    self.normalized_data.loc[index, "EMA 14 30 Diff"] = self.studies.at[index, 'ema14'] - self.studies.at[index, 'ema30']
                    self.normalized_data.loc[index, "Base Fib High Diff"] = base_fib1 - data.at[index, "High"] if direction == "-" else data.at[index, "High"] - base_fib1
                    self.normalized_data.loc[index, "Base Fib Low Diff"] = base_fib1 - data.at[index, "Low"] if direction == "-" else data.at[index, "Low"] - base_fib1
                    self.normalized_data.loc[index, "Next1 Fib High Diff"] = next1_fib - data.at[index, "High"] if direction == "+" else data.at[index, "High"] - next1_fib
                    self.normalized_data.loc[index, "Next1 Fib Low Diff"] = next1_fib - data.at[index, "Low"] if direction == "+" else data.at[index, "Low"] - next1_fib
                    self.normalized_data.loc[index, "Next2 Fib High Diff"] = next2_fib - data.at[index, "High"] if direction == "+" else data.at[index, "High"] - next2_fib
                    self.normalized_data.loc[index, "Next2 Fib Low Diff"] = next2_fib - data.at[index, "Low"] if direction == "+" else data.at[index, "Low"] - next2_fib
                    self.normalized_data.loc[index, "Open"] = data.at[index, "Open"]
                    self.normalized_data.loc[index, "High"] = data.at[index, "High"]
                    self.normalized_data.loc[index, "Low"] = data.at[index, "Low"]
                    self.normalized_data.loc[index, "Close"] = data.at[index, "Close"]
                    self.normalized_data.loc[index, "Last3High Base Fib"] = last_3_high - base_fib1
                    self.normalized_data.loc[index, "Last3Low Base Fib"] = last_3_low - next1_fib
                    self.normalized_data.loc[index, "Last3High Next1 Fib"] = last_3_high - next1_fib
                    self.normalized_data.loc[index, "Last3Low Next1 Fib"] = last_3_low - next1_fib
                    self.normalized_data.loc[index, "Last3High Next2 Fib"] = last_3_high - next2_fib
                    self.normalized_data.loc[index, "Last3Low Next2 Fib"] = last_3_low - next2_fib
                except Exception as e:
                    print(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
                    raise AssertionError(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
        elif out == 3:
            third_last = data.iloc[-1]
            last_3_high = data['High'].iloc[-3:].mean()
            last_3_low = data['Low'].iloc[-3:].mean()
            i = 0
            j = 0
            k = 0
            if self.fib['0.273'].iloc[-1] < self.fib['0.283'].iloc[-1]: # get fib direction
                direction = "+"
            else:
                direction = "-"
            try:
                save_point = 0
                for index,item in self.fib.items():
                    if direction == "+": # Check if avg is greater than fib val, record
                        if third_last['Close'] > item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_high < item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
                    else: # Negative direction
                        if third_last['Close'] < item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_low > item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(fname, exc_type, exc_obj, exc_tb.tb_lineno)
                print(f'[ERROR] Failed to iterate through fibonacci to find key fib points...\n{str(e)}')
            next1_fib = j
            next2_fib = k
            base_fib1 = i
            if next2_fib == 0:
                next2_fib = next1_fib
                next1_fib = save_point
            for index, row in data.iterrows():
                try:
                    if index <= 1:
                        last_3_high = data['High'].iloc[index]
                        last_3_low = data['Low'].iloc[index]
                        self.normalized_data.loc[index, "Open"] = 0
                        self.normalized_data.loc[index, "High"] = 0
                        self.normalized_data.loc[index, "Low"] = 0
                        self.normalized_data.loc[index, "Close"] = 0
                    elif index < 3: # If not sufficient amount of days surpassed, do this
                        last_3_high = data['High'].iloc[:index].mean()
                        last_3_low = data['Low'].iloc[:index].mean()
                        self.normalized_data.loc[index, "Open"] = data.at[index, "Open"] - data.at[index - 1, "Open"]
                        self.normalized_data.loc[index, "High"] = data.at[index, "High"] - data.at[index - 1, "High"]
                        self.normalized_data.loc[index, "Low"] = data.at[index, "Low"] - data.at[index - 1, "Low"]
                        self.normalized_data.loc[index, "Close"] = data.at[index, "Close"] - data.at[index - 1, "Close"]
                    else:
                        last_3_high = data['High'].iloc[index-3:index].mean()
                        last_3_low = data['Low'].iloc[index-3:index].mean()
                        self.normalized_data.loc[index, "Open"] = data.at[index, "Open"] - data.at[index - 1, "Open"]
                        self.normalized_data.loc[index, "High"] = data.at[index, "High"] - data.at[index - 1, "High"]
                        self.normalized_data.loc[index, "Low"] = data.at[index, "Low"] - data.at[index - 1, "Low"]
                        self.normalized_data.loc[index, "Close"] = data.at[index, "Close"] - data.at[index - 1, "Close"]
                    self.normalized_data.loc[index, "Upper Kelt"] = self.keltner.at[index, "upper"] - data.at[index,"High"]
                    self.normalized_data.loc[index, "Lower Kelt"] = self.keltner.at[index, "lower"] - data.at[index,"Low"]
                    self.normalized_data.loc[index, "Middle Kelt"] = self.keltner.at[index, "middle"] - data.at[index,"Close"]
                    self.normalized_data.loc[index, "EMA 14"] = self.studies.at[index, 'ema14'] - data.at[index,"Open"]
                    self.normalized_data.loc[index, "EMA 30"] = self.studies.at[index, 'ema30'] - data.at[index,"Close"]
                    self.normalized_data.loc[index, "Base Fib"] = abs(base_fib1 - data.at[index,"Close"])
                    self.normalized_data.loc[index, "Next1 Fib"] = abs(next1_fib - data.at[index,"Close"])
                    self.normalized_data.loc[index, "Next2 Fib"] = abs(next2_fib - data.at[index,"Close"])
                    self.normalized_data.loc[index, "Last3High"] = last_3_high - data.at[index,"High"]
                    self.normalized_data.loc[index, "Last3Low"] = last_3_low - data.at[index,"Low"]
                    #print(self.normalized_data)
                except Exception as e:
                    print(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
                    raise AssertionError(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
        elif out == 4:
            third_last = data.iloc[-1]
            last_3_high = data['High'].iloc[-3:].mean()
            last_3_low = data['Low'].iloc[-3:].mean()
            i = 0
            j = 0
            k = 0
            if self.fib['0.273'].iloc[-1] < self.fib['0.283'].iloc[-1]: # get fib direction
                direction = "+"
            else:
                direction = "-"
            try:
                save_point = 0
                for index,item in self.fib.items():
                    if direction == "+": # Check if avg is greater than fib val, record
                        if third_last['Close'] > item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_high < item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
                    else: # Negative direction
                        if third_last['Close'] < item.iloc[-1]: # we want to signify a base when the close is above fib val
                            i = item.iloc[-1]
                        else:
                            if j != 0: # If j is populated, set k
                                k = item.iloc[-1]
                                break
                            elif last_3_low > item.iloc[-1]: # First indication of this will set j - after will set k then break
                                j = item.iloc[-1]
                            else:
                                save_point = item.iloc[-1]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(fname, exc_type, exc_obj, exc_tb.tb_lineno)
                print(f'[ERROR] Failed to iterate through fibonacci to find key fib points...\n{str(e)}')
            next1_fib = j
            next2_fib = k
            base_fib1 = i
            if next2_fib == 0:
                next2_fib = next1_fib
                next1_fib = save_point
            for index, row in data.iterrows():
                try:
                    if index <= 1:
                        last_3_high = data['High'].iloc[index]
                        last_3_low = data['Low'].iloc[index]
                    elif index < 3: # If not sufficient amount of days surpassed, do this
                        last_3_high = data['High'].iloc[:index].mean()
                        last_3_low = data['Low'].iloc[:index].mean()
                    else:
                        last_3_high = data['High'].iloc[index-3:index].mean()
                        last_3_low = data['Low'].iloc[index-3:index].mean()
                    self.normalized_data.loc[index, "Upper Kelt"] = self.keltner.at[index, "upper"]
                    self.normalized_data.loc[index, "Lower Kelt"] = self.keltner.at[index, "lower"]
                    self.normalized_data.loc[index, "Middle Kelt"] = self.keltner.at[index, "middle"]
                    self.normalized_data.loc[index, "EMA 14"] = self.studies.at[index, 'ema14']
                    self.normalized_data.loc[index, "EMA 30"] = self.studies.at[index, 'ema30']
                    self.normalized_data.loc[index, "Base Fib"] = base_fib1
                    self.normalized_data.loc[index, "Next1 Fib"] = next1_fib
                    self.normalized_data.loc[index, "Next2 Fib"] = next2_fib
                    self.normalized_data.loc[index, "Open"] = data.at[index, "Open"]
                    self.normalized_data.loc[index, "High"] = data.at[index, "High"]
                    self.normalized_data.loc[index, "Low"] = data.at[index, "Low"]
                    self.normalized_data.loc[index, "Close"] = data.at[index, "Close"]
                    self.normalized_data.loc[index, "Last3High"] = last_3_high
                    self.normalized_data.loc[index, "Last3Low"] = last_3_low
                    #print(self.normalized_data)
                except Exception as e:
                    print(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
                    raise AssertionError(f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.normalized_data}\nException: {str(e)}')
        return 0

    '''
        Normalize:  Use Scalar to normalize given data
    '''

    def normalize(self, out: int = 1):
        self.unnormalized_data = self.normalized_data
        try:
            if 3 <= out <= 4:
                scaler = self.normalizer.fit(self.unnormalized_data)
                # Get w values for row normalization in order to reverse matrices
                self.w = {}
                self.w['Upper Kelt'] = np.sqrt(sum(self.unnormalized_data['Upper Kelt'].to_numpy() ** 2))
                self.w['Lower Kelt'] = np.sqrt(sum(self.unnormalized_data['Lower Kelt'].to_numpy() ** 2))
                self.w['Middle Kelt'] = np.sqrt(sum(self.unnormalized_data['Middle Kelt'].to_numpy() ** 2))
                self.w['EMA 14'] = np.sqrt(sum(self.unnormalized_data['EMA 14'].to_numpy() ** 2))
                self.w['EMA 30'] = np.sqrt(sum(self.unnormalized_data['EMA 30'].to_numpy() ** 2))
                self.w['Base Fib'] = np.sqrt(sum(self.unnormalized_data['Base Fib'].to_numpy() ** 2))
                self.w['Next1 Fib'] = np.sqrt(sum(self.unnormalized_data['Next1 Fib'].to_numpy() ** 2))
                self.w['Next2 Fib'] = np.sqrt(sum(self.unnormalized_data['Next2 Fib'].to_numpy() ** 2))
                self.w['Open'] = np.sqrt(sum(self.unnormalized_data['Open'].to_numpy() ** 2))
                self.w['High'] = np.sqrt(sum(self.unnormalized_data['High'].to_numpy() ** 2))
                self.w['Low'] = np.sqrt(sum(self.unnormalized_data['Low'].to_numpy() ** 2))
                self.w['Close'] = np.sqrt(sum(self.unnormalized_data['Close'].to_numpy() ** 2))
                self.w['Last3High'] = np.sqrt(sum(self.unnormalized_data['Last3High'].to_numpy() ** 2))
                self.w['Last3Low'] = np.sqrt(sum(self.unnormalized_data['Last3Low'].to_numpy() ** 2))
            else:
                scaler = self.min_max.fit(self.unnormalized_data)
            self.normalized_data = pd.DataFrame(scaler.fit_transform(self.unnormalized_data) if out != 4 else self.unnormalized_data.to_numpy(),
                                                columns=['Close EMA14 Distance',
                                                         'Close EMA30 Distance',
                                                         'Close Fib1 Distance',
                                                         'Close Fib2 Distance',
                                                         'Num Consec Candle Dir',
                                                         'Upper Keltner Close Diff',
                                                         'Lower Keltner Close Diff',
                                                         'Open',
                                                         'Close'] if out==1 else\
                                                ['Last2Volume Cur Volume Diff','Open Upper Kelt Diff',
                                                 'Open Lower Kelt Diff','High Upper Kelt Diff',
                                                 'High Lower Kelt Diff','Low Upper Kelt Diff',
                                                 'Low Lower Kelt Diff','Close Upper Kelt Diff',
                                                 'Close Lower Kelt Diff','EMA 14 30 Diff',
                                                 'Base Fib High Diff','Base Fib Low Diff',
                                                 'Next1 Fib High Diff','Next1 Fib Low Diff',
                                                 'Next2 Fib High Diff','Next2 Fib Low Diff',
                                                 'Open','High','Low','Close',
                                                 'Last3High Base Fib','Last3Low Base Fib',
                                                 'Last3High Next1 Fib','Last3Low Next1 Fib',
                                                 'Last3High Next2 Fib','Last3Low Next2 Fib']if out ==2 else \
                                                    ['Upper Kelt',
                                                     'Lower Kelt', 'Middle Kelt', 'EMA 14', 'EMA 30',
                                                     'Base Fib', 'Next1 Fib', 'Next2 Fib',
                                                     'Open', 'High', 'Low', 'Close',
                                                     'Last3High', 'Last3Low'] if out == 3 or out == 4 else [])
            self.normalized_data = self.normalized_data[-15 if out == 1 else -6 if 2 <= out <= 4 else 0:]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('[ERROR] Failed to normalize!\n', str(e))
            return 1
        return 0

    '''
        Unnormalize data
    '''

    def unnormalize(self, data, out: int = 1):
        if out == 4:
            pass
        elif out == 3:
            scaler = self.normalizer.fit(self.unnormalized_data)
        else:
            scaler = self.min_max.fit(self.unnormalized_data)
        tmp_data = pd.DataFrame(columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                         'Close Fib1 Distance', 'Close Fib2 Distance', 'Num Consec Candle Dir',
                                         'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
                                         'Open',
                                         'Close'] if out == 1 else \
                                    ['Last2Volume Cur Volume Diff', 'Open Upper Kelt Diff',
                                     'Open Lower Kelt Diff', 'High Upper Kelt Diff',
                                     'High Lower Kelt Diff', 'Low Upper Kelt Diff',
                                     'Low Lower Kelt Diff', 'Close Upper Kelt Diff',
                                     'Close Lower Kelt Diff', 'EMA 14 30 Diff',
                                     'Base Fib High Diff', 'Base Fib Low Diff',
                                     'Next1 Fib High Diff', 'Next1 Fib Low Diff',
                                     'Next2 Fib High Diff', 'Next2 Fib Low Diff',
                                     'Open', 'High', 'Low', 'Close',
                                     'Last3High Base Fib', 'Last3Low Base Fib',
                                     'Last3High Next1 Fib', 'Last3Low Next1 Fib',
                                     'Last3High Next2 Fib', 'Last3Low Next2 Fib'] if out == 2 else \
                                        ['Upper Kelt',
                                         'Lower Kelt', 'Middle Kelt', 'EMA 14', 'EMA 30',
                                         'Base Fib', 'Next1 Fib', 'Next2 Fib',
                                         'Open', 'High', 'Low', 'Close',
                                         'Last3High', 'Last3Low'] if out == 3 or out == 4 else [])
        # Set data manually to preserve order
        try:
            tmp_data['Open'] = data['Open']
        except:
            pass
        tmp_data['Close'] = data['Close']
        if 2 <= out <= 4: # Add high/low
            tmp_data['High'] = (data['High'] * self.w['High']) if out != 4 else data['High']
            tmp_data['Low'] = (data['Low'] * self.w['Low']) if out != 4 else data['Low']
            tmp_data['Open'] = (tmp_data['Open'] * self.w['Open']) if out != 4 else data['Open']
            tmp_data['Close'] = (tmp_data['Close'] * self.w['Close']) if out != 4 else data['Close']
        return pd.DataFrame(scaler.inverse_transform((tmp_data.to_numpy())) if out != 3 and out != 4 else tmp_data.to_numpy(), columns=['Close EMA14 Distance',
                                                                                      'Close EMA30 Distance',
                                                                                      'Close Fib1 Distance',
                                                                                      'Close Fib2 Distance',
                                                                                      'Num Consec Candle Dir',
                                                                                      'Upper Keltner Close Diff',
                                                                                      'Lower Keltner Close Diff',
                                                                                      'Open',
                                                                                      'Close'] if out == 1 else \
                                    ['Last2Volume Cur Volume Diff', 'Open Upper Kelt Diff',
                                     'Open Lower Kelt Diff', 'High Upper Kelt Diff',
                                     'High Lower Kelt Diff', 'Low Upper Kelt Diff',
                                     'Low Lower Kelt Diff', 'Close Upper Kelt Diff',
                                     'Close Lower Kelt Diff', 'EMA 14 30 Diff',
                                     'Base Fib High Diff', 'Base Fib Low Diff',
                                     'Next1 Fib High Diff', 'Next1 Fib Low Diff',
                                     'Next2 Fib High Diff', 'Next2 Fib Low Diff',
                                     'Open', 'High', 'Low', 'Close',
                                     'Last3High Base Fib', 'Last3Low Base Fib',
                                     'Last3High Next1 Fib', 'Last3Low Next1 Fib',
                                     'Last3High Next2 Fib', 'Last3Low Next2 Fib'] if out == 2 else \
                                        ['Upper Kelt',
                                         'Lower Kelt', 'Middle Kelt', 'EMA 14', 'EMA 30',
                                         'Base Fib', 'Next1 Fib', 'Next2 Fib',
                                         'Open', 'High', 'Low', 'Close',
                                         'Last3High', 'Last3Low'] if out == 3 or out == 4 else [])

# norm = Normalizer()
# norm.read_data("2016-03-18","CCL")
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()
