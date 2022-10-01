import asyncio
from pathlib import Path
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
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

    async def mysql_read_data(self, ticker, date=None, force_generate=False, skip_db=False,interval='1d'):
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
                                    125 if '1wk' in interval else\
                                    600 if '1mo' in interval else\
                                    30 if interval =='5m' else\
                                    40 if '15m' in interval else\
                                    59 if '30m' in interval else\
                                    120 if '60m' in interval else 40), initial_date,
                                                     force_generate=force_generate, skip_db=skip_db, interval=interval,ticker=ticker)
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

    def read_data(self, ticker, rand_dates=False, skip_db=False, interval='1d'):
        if rand_dates:
            # Get a random date for generation based on min/max date
            d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p'), '%m/%d/%Y %I:%M %p')
            d1 = datetime.datetime.strptime('1/1/2007 1:00 AM', '%m/%d/%Y %I:%M %p')
            # get time diff then get time in seconds
            delta = d2 - d1
            int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
            # append seconds to get a start date
            random_second = random.randrange(int_delta)
            date = d1 + datetime.timedelta(seconds=random_second)
        else:
            date = None
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.mysql_read_data(ticker, date=date, skip_db=skip_db,interval=interval))
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

    def convert_derivatives(self, out=8):
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
                                                         'Close'])
        target_fib1 = None
        target_fib2 = None
        last_3 = data['Close']
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
                raise AssertionError(f'[ERROR] Failed normalization!  Current normalized data:\n{self.normalized_data}')
        return 0

    '''
        Gather the divergence data for further use
    '''

    def convert_divergence(self):
        data = self.data
        try:
            data = self.data.drop(columns={'Date'})
        except:
            pass
        data = data.astype(np.float_)
        self.studies = self.studies.astype(np.float_)
        self.normalized_data = pd.DataFrame((), columns=['Open', 'Close', 'Range', 'Euclidean Open', 'Euclidean Close',
                                                         'Open EMA14 Diff', 'Open EMA30 Diff', 'Close EMA14 Diff',
                                                         'Close EMA30 Diff', 'EMA14 EMA30 Diff'])
        self.normalized_data["Open"] = data["Open"]
        self.normalized_data["Close"] = data["Close"]
        self.normalized_data["Range"] = data["Open"]
        self.normalized_data["Euclidean Open"] = data["Open"]
        self.normalized_data["Euclidean Close"] = data["Close"]
        self.normalized_data["Open EMA14 Diff"] = self.studies["ema14"]
        self.normalized_data["Open EMA30 Diff"] = self.studies["ema30"]
        self.normalized_data["Close EMA14 Diff"] = self.studies["ema14"]
        self.normalized_data["Close EMA30 Diff"] = self.studies["ema30"]
        self.normalized_data["EMA14 EMA30 Diff"] = self.studies["ema14"]

        for index, row in data.iterrows():
            try:
                if index == 0:
                    self.normalized_data.loc[index, "Open"] = 0
                    self.normalized_data.loc[index, "Close"] = 0
                    self.normalized_data.loc[index, "Range"] = abs(data.at[index, "Close"] - data.at[index, "Open"])
                    self.normalized_data.loc[index, "Euclidean Open"] = np.power(np.power(((data.at[index, "Open"] -
                                                                                            self.studies.at[
                                                                                                index, "ema14"]) + (
                                                                                                   data.at[
                                                                                                       index, "Open"] -
                                                                                                   self.studies.at[
                                                                                                       index, "ema30"])),
                                                                                          2), 1 / 2)
                    self.normalized_data.loc[index, "Euclidean Close"] = np.power(np.power(((data.at[index, "Close"] -
                                                                                             self.studies.at[
                                                                                                 index, "ema14"]) + (
                                                                                                    data.at[
                                                                                                        index, "Close"] -
                                                                                                    self.studies.at[
                                                                                                        index, "ema30"])),
                                                                                           2), 1 / 2)
                    self.normalized_data.loc[index, "Open EMA14 Diff"] = (data.at[index, "Open"] - self.studies.at[
                        index, 'ema14']) / data.at[index, "Open"]
                    self.normalized_data.loc[index, "Open EMA30 Diff"] = (data.at[index, "Open"] - self.studies.at[
                        index, 'ema30']) / data.at[index, "Open"]
                    self.normalized_data.loc[index, "Close EMA14 Diff"] = (data.at[index, "Close"] - self.studies.at[
                        index, 'ema14']) / data.at[index, "Close"]
                    self.normalized_data.loc[index, "Close EMA30 Diff"] = (data.at[index, "Close"] - self.studies.at[
                        index, 'ema30']) / data.at[index, "Close"]
                    self.normalized_data.loc[index, "EMA14 EMA30 Diff"] = (self.studies.at[index, "ema14"] -
                                                                           self.studies.at[index, 'ema30']) / \
                                                                          self.studies.at[index, "ema14"]

                else:
                    self.normalized_data.loc[index, "Close"] = (data.at[index, "Close"] - data.at[index - 1, "Close"])
                    self.normalized_data.loc[index, "Open"] = (data.at[index, "Open"] - data.at[index - 1, "Open"])
                    self.normalized_data.loc[index, "Range"] = abs(data.at[index, "Close"] - data.at[index, "Open"])
                    self.normalized_data.loc[index, "Euclidean Open"] = np.power(np.power(((data.at[index, "Open"] -
                                                                                            self.studies.at[
                                                                                                index, "ema14"]) + (
                                                                                                   data.at[
                                                                                                       index, "Open"] -
                                                                                                   self.studies.at[
                                                                                                       index, "ema30"])),
                                                                                          2), 1 / 2)
                    self.normalized_data.loc[index, "Euclidean Close"] = np.power(np.power(((data.at[index, "Close"] -
                                                                                             self.studies.at[
                                                                                                 index, "ema14"]) + (
                                                                                                    data.at[
                                                                                                        index, "Close"] -
                                                                                                    self.studies.at[
                                                                                                        index, "ema30"])),
                                                                                           2), 1 / 2)
                    self.normalized_data.loc[index, "Open EMA14 Diff"] = (data.at[index, "Open"] - self.studies.at[
                        index, 'ema14']) / data.at[index, "Open"]
                    self.normalized_data.loc[index, "Open EMA30 Diff"] = (data.at[index, "Open"] - self.studies.at[
                        index, 'ema30']) / data.at[index, "Open"]
                    self.normalized_data.loc[index, "Close EMA14 Diff"] = (data.at[index, "Close"] - self.studies.at[
                        index, 'ema14']) / data.at[index, "Close"]
                    self.normalized_data.loc[index, "Close EMA30 Diff"] = (data.at[index, "Close"] - self.studies.at[
                        index, 'ema30']) / data.at[index, "Close"]
                    self.normalized_data.loc[index, "EMA14 EMA30 Diff"] = (self.studies.at[index, "ema14"] -
                                                                           self.studies.at[index, 'ema30']) / \
                                                                          self.studies.at[index, "ema14"]
            except:
                raise AssertionError("[ERROR] Failed divergence!  Current normalized data:\n", self.normalized_data)
        return 0

    '''
        Normalize:  Use Scalar to normalize given data
    '''

    def normalize(self, out: int = 8):
        self.normalized_data = self.normalized_data[-15:]
        self.unnormalized_data = self.normalized_data
        try:

            scaler = self.min_max.fit(self.unnormalized_data)
            self.normalized_data = pd.DataFrame(scaler.fit_transform(self.unnormalized_data), columns=['Close EMA14 Distance',
                                                                                                     'Close EMA30 Distance',
                                                                                                     'Close Fib1 Distance',
                                                                                                     'Close Fib2 Distance',
                                                                                                     'Num Consec Candle Dir',
                                                                                                     'Upper Keltner Close Diff',
                                                                                                     'Lower Keltner Close Diff',
                                                                                                     'Open',
                                                                                                     'Close'])
            if out == 2:
                self.normalized_data = self.normalized_data.drop(
                    columns=['Close Fib1 Distance', 'Num Consec Candle Dir'])
        except Exception as e:
            print('[ERROR] Failed to normalize!\n', str(e))
            return 1
        return 0

    '''
        Normalize data for the divergence data
    '''

    def normalize_divergence(self, out: int = 8):
        self.normalized_data = self.normalized_data[-15:]
        self.unnormalized_data = self.normalized_data
        try:
            scaler = self.min_max.fit(self.unnormalized_data)
            if out == 8:
                self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),
                                                    columns=['Open', 'Close', 'Range', 'Euclidean Open',
                                                             'Euclidean Close', 'Open EMA14 Diff', 'Open EMA30 Diff',
                                                             'Close EMA14 Diff',
                                                             'Close EMA30 Diff',
                                                             'EMA14 EMA30 Diff'])  # NORMALIZED DATA STORED IN NP ARRAY
            elif out == 2:
                self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),
                                                    columns=['Close'])  # NORMALIZED DATA STORED IN NP ARRAY
        except Exception as e:
            print('[ERROR] Failed to normalize!\nException:\n', str(e))
            return 1
        return 0

    '''
        Unnormalize data
    '''

    def unnormalize(self, data):
        scaler = self.min_max.fit(self.unnormalized_data)
        tmp_data = pd.DataFrame(columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                         'Close Fib1 Distance', 'Close Fib2 Distance', 'Num Consec Candle Dir',
                                         'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
                                         'Open',
                                         'Close'])
        # Set data manually to preserve order
        try:
            tmp_data['Open'] = data['Open']
        except:
            pass
        tmp_data['Close'] = data['Close']
        return pd.DataFrame(scaler.inverse_transform((tmp_data.to_numpy())), columns=['Close EMA14 Distance',
                                                                                      'Close EMA30 Distance',
                                                                                      'Close Fib1 Distance',
                                                                                      'Close Fib2 Distance',
                                                                                      'Num Consec Candle Dir',
                                                                                      'Upper Keltner Close Diff',
                                                                                      'Lower Keltner Close Diff',
                                                                                      'Open',
                                                                                      'Close'])

    '''
        Unnormalize the divergence data
    '''

    def unnormalize_divergence(self, data):
        scaler = self.min_max.fit(self.unnormalized_data)
        if len(data.columns) == 10:
            return pd.DataFrame(scaler.inverse_transform((data.to_numpy())),
                                columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                         'Close Fib1 Distance', 'Close Fib2 Distance', 'Num Consec Candle Dir',
                                         'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
                                         'Open',
                                         'Close'])  # NORMALIZED DATA STORED IN NP ARRAY
        elif len(data.columns) == 3:
            tmp_data = pd.DataFrame(
                columns=['Euclidean Open', 'Euclidean Close', 'Open EMA14 Diff', 'Open EMA30 Diff', 'Close EMA14 Diff',
                         'Close EMA30 Diff', 'EMA14 EMA30 Diff'])
            new_data = pd.concat([data, tmp_data], axis=1)
            # print(new_data)
            return pd.DataFrame(scaler.inverse_transform((new_data.to_numpy())),
                                columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                         'Close Fib1 Distance', 'Close Fib2 Distance', 'Num Consec Candle Dir',
                                         'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
                                         'Open',
                                         'Close'])  # NORMALIZED DATA STORED IN NP ARRAY

# norm = Normalizer()
# norm.read_data("2016-03-18","CCL")
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()
