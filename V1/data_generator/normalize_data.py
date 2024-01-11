import asyncio
import sys
from pathlib import Path
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from numpy import array
from sklearn.decomposition import PCA
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import MinMaxScaler, StandardScaler
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
        self.data: list = []
        self.studies: list = []
        self.normalized_data = []
        self.unnormalized_data = []
        self.path = Path(os.getcwd()).absolute()
        self.min_max = MinMaxScaler(feature_range=(0, 1))
        self.min_max_list = []
        self.standard_scaler = StandardScaler()
        self.scaler_list = []
        self.normalizer = SKNormalizer()

        self.gen = Generator(ticker=ticker, force_generate=force_generate)
        self.fib: list = []
        self.keltner: list = []
        self.days_map = {'1d': 180,
                         '1wk': 900,
                         '1mo': 3600,
                         '5m': 30,
                         '15m': 40,
                         '30m': 50,
                         '60m': 75}
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

    async def mysql_read_data(self, ticker, date=None, out=1, force_generate=False, skip_db=False, interval='1d',
                              opt_fib_vals=[],n_steps=20):
        try:
            self.cnx = self.db_con.cursor(buffered=True)
            self.cnx.autocommit = True
            # If string, convert to datetime.datetime                
            valid_datetime = datetime.datetime.now()
            if date is None:
                # Verify date before proceeding 
                holidays = USFederalHolidayCalendar().holidays(start=valid_datetime - datetime.timedelta(days=self.days_map[interval]),
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
        except Exception as e:
            print(f"[ERROR] Failed to set dates back while retrieving db data.\r\nException: {e}")
        try:
            print("[INFO] Generating data with dates.")
            vals = await self.gen.generate_data_with_dates(
                initial_date - datetime.timedelta(days=self.days_map[interval]),initial_date,
                force_generate=force_generate, out=out, skip_db=skip_db, interval=interval, ticker=ticker,
                opt_fib_vals=opt_fib_vals,
                n_steps=n_steps)
            for val in vals:  # Vals returns list of tuples...
                studies = val[1]
                data = val[0]
                fib = val[2]
                keltner = val[3]
                self.studies.append(studies)
                self.data.append(data)
                self.fib.append(fib)
                self.keltner.append(keltner)
            del vals
        except Exception as e:
            print(
                f'[ERROR] Failed to retrieve data points for {ticker} from {(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")} to {initial_date.strftime("%Y-%m-%d")}!\n',
                str(e))
            raise AssertionError
        except:
            print(
                f'[ERROR] Failed to retrieve data points for {ticker} from {(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")} to {initial_date.strftime("%Y-%m-%d")}!\n')
            raise AssertionError
        self.cnx.close()
        return

    def reset_data(self):
        del self.studies, self.data, self.fib, self.keltner
        self.studies = []
        self.data = []
        self.fib = []
        self.keltner = []
        self.scaler_list = []
        self.min_max_list = []

    def generate_dates(self, interval: str = None):
        # Get a random date for generation based on min/max date
        d2 = datetime.datetime.strptime(datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p'), '%m/%d/%Y %I:%M %p')
        d1 = datetime.datetime.strptime('1/1/2000 1:00 AM',
                                        '%m/%d/%Y %I:%M %p') if interval == '1d' or interval == '1m' or interval == '1wk' else \
            datetime.datetime.now() - datetime.timedelta(
                days=730) if interval == '30m' or interval == '60m' or interval == '1h' or interval == '4h' else \
                datetime.datetime.now() - datetime.timedelta(days=50)
        # get time diff then get time in seconds
        delta = d2 - d1
        # print(delta.days,delta.seconds)
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        # append seconds to get a start date
        random_second = random.randrange(int_delta)
        date = d1 + datetime.timedelta(seconds=random_second)
        return date

    '''
        utilize mysql to retrieve data and study data for later usage...
    '''

    async def read_data(self, ticker, rand_dates=False, force_generate=False,  out=1, skip_db=False, interval='1d', opt_fib_vals=[],n_steps=20):
        if rand_dates:  # Only used when generating model...
            date = self.generate_dates(interval)
            required_days = self.days_map[interval]
            attempts = 3
            while attempts > 0 and (date + datetime.timedelta(days=required_days)) > datetime.datetime.now():
                #TODO Attempt to retrieve data for dates here to confirm enough data.
                date = self.generate_dates(interval)
                attempts = attempts - 1
                if attempts == 0:
                    raise Exception("[ERROR] Failed to get dates for 3 different timeframes.  Either insufficient "
                                    "data and/or delisted.")
            print(f"[INFO] Gathering data from date {date - datetime.timedelta(days=required_days)} to {date} ")
        else:
            date = None
        try:
            print("[INFO] Reading db data.")
            await self.mysql_read_data(ticker, date=date, out=out,
                                                         skip_db=skip_db, force_generate=force_generate,
                                       interval=interval, opt_fib_vals=opt_fib_vals,n_steps=n_steps)
        except Exception as e:
            print(f'\n[ERROR] Failed to read data!\r\nException: {e}')
            raise Exception(e)
        for data in self.data:
            try:
                data = data.drop(['Adj Close'], axis=1)
            except:
                pass
            try:
                data = data.drop(['Date'], axis=1)
            except:
                pass
            try:
                data = data.drop(['index'], axis=1)
                data = data.drop(['level_0'], axis=1)
            except:
                pass

    def convert_derivatives(self, out: int = 1):
        data_list = self.data.copy()
        for idx, data in enumerate(data_list):
            data = data.iloc[:5]
            try:
                data = data.drop(columns={'Date'},axis=1)
            except:
                pass
            try:
                data = data.drop(columns={'index'},axis=1)
            except:
                pass
            data = data.astype(np.float_)
            try:
                self.studies[idx] = self.studies[idx].astype(np.float_).reset_index()
            except:
                print('[INFO] Couldn\'t convert emas to type <float>')
            try:
                self.keltner[idx] = self.keltner[idx].astype(np.float_).reset_index()
            except:
                print('[INFO] Couldn\'t convert keltner to type <float>')
            try:
                self.fib[idx] = self.fib[idx].astype(np.float_).reset_index()
            except:
                print('[INFO] Couldn\'t convert fibonacci sequence to type <float>')
            try:
                self.fib[idx] = self.fib[idx].drop(['index'], axis=1)
            except:
                pass
            try:
                self.unnormalized_data.append(pd.DataFrame((), columns=['Close EMA14 Distance', 'Close EMA30 Distance',
                                                                      'Close Fib1 Distance', 'Close Fib2 Distance',
                                                                      'Num Consec Candle Dir',
                                                                      'Upper Keltner Close Diff',
                                                                      'Lower Keltner Close Diff',
                                                                      'Open',
                                                                      'Close'] if out == 1 else []))
            except Exception as e:
                raise Exception(f"[ERROR] Failed to set set columns for calculating data.\r\nException:{e}")
            if out == 1:  # Do legacy model data generation for 14 days worth of stuff
                last_close = data['Close'].iloc[-1]
                last_3_high = data['High'].iloc[-3:].mean()
                last_3_low = data['Low'].iloc[-3:].mean()
                i = 0
                j = 0
                k = 0
                try:
                    if self.fib[idx]['0.273'].iloc[-1].values[0] < self.fib[idx]['0.283'].iloc[-1].values[0]:  # get fib direction
                        direction = "+"
                    else:
                        direction = "-"
                except:
                    if self.fib[idx]['0.273'].iloc[-1] < self.fib[idx]['0.283'].iloc[-1]:  # get fib direction
                        direction = "+"
                    else:
                        direction = "-"
                try:
                    save_point = 0
                    sole_fib_col = self.fib[idx].transpose().iloc[:,-1]
                    i = self.fib[idx].transpose().iloc[(sole_fib_col - last_close).abs().argsort()[1],-1]
                    j = self.fib[idx].transpose().iloc[(sole_fib_col - last_close).abs().argsort()[2],-1]
                    k = self.fib[idx].transpose().iloc[(sole_fib_col - last_close).abs().argsort()[3],-1]

                except Exception as e:
                    print(f'[ERROR] Failed to iterate through fibonacci to find key fib points.\r\nException: {e}')
                    raise Exception(e)
                next1_fib = j
                next2_fib = k
                base_fib1 = i
                if next2_fib == 0:
                    next2_fib = next1_fib
                    next1_fib = save_point
                for index, row in data.iterrows():
                    try:
                        if index <= 1:
                            last_3_high = round(data['High'].iloc[index], 2)
                            last_3_low = round(data['Low'].iloc[index], 2)
                        elif index < 3:  # If not sufficient amount of days surpassed, do this
                            last_3_high = round(data['High'].iloc[:index].mean(), 2)
                            last_3_low = round(data['Low'].iloc[:index].mean(), 2)
                        else:
                            last_3_high = round(data['High'].iloc[index - 3:index].mean(), 2)
                            last_3_low = round(data['Low'].iloc[index - 3:index].mean(), 2)
                        self.unnormalized_data[idx].loc[index, "Upper Kelt"] = round(self.keltner[idx].at[index, "upper"], 2)
                        self.unnormalized_data[idx].loc[index, "Lower Kelt"] = round(self.keltner[idx].at[index, "lower"], 2)
                        self.unnormalized_data[idx].loc[index, "Middle Kelt"] = round(self.keltner[idx].at[index, "middle"], 2)
                        self.unnormalized_data[idx].loc[index, "EMA 14"] = round(self.studies[idx].at[index, 'ema14'], 2)
                        self.unnormalized_data[idx].loc[index, "EMA 30"] = round(self.studies[idx].at[index, 'ema30'], 2)
                        self.unnormalized_data[idx].loc[index, "Base Fib"] = round(base_fib1, 2)
                        self.unnormalized_data[idx].loc[index, "Next1 Fib"] = round(next1_fib, 2)
                        self.unnormalized_data[idx].loc[index, "Next2 Fib"] = round(next2_fib, 2)
                        self.unnormalized_data[idx].loc[index, "Open"] = round(data.at[index, "Open"], 2)
                        self.unnormalized_data[idx].loc[index, "High"] = round(data.at[index, "High"], 2)
                        self.unnormalized_data[idx].loc[index, "Low"] = round(data.at[index, "Low"], 2)
                        self.unnormalized_data[idx].loc[index, "Close"] = round(data.at[index, "Close"], 2)
                        self.unnormalized_data[idx].loc[index, "Last3High"] = round(last_3_high, 2)
                        self.unnormalized_data[idx].loc[index, "Last3Low"] = round(last_3_low, 2)
                        # print(self.unnormalized_data)
                    except Exception as e:
                        print(
                            f'[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.unnormalized_data}\r\nException: {e}')
                        raise AssertionError(
                            f'{str(e)}\n[ERROR] Failed normalization!\nDirection: "{direction}"\nCurrent normalized data:\n\t{self.unnormalized_data}\n')
            self.unnormalized_data[idx] = self.unnormalized_data[idx].transpose()
        return 0

    '''
        Normalize:  Use Scalar to normalize given data
    '''

    def normalize(self, out: int = 1):
        unnorm_data_list = self.unnormalized_data.copy()
        for idx, data in enumerate(unnorm_data_list):
            data = data.iloc[:5]
            try:
                if 3 <= out <= 4:
                    # print(f"[INFO] Out is set to {out}.  Standard scaler fit_transform in progress.")
                    self.scaler_list.append(self.standard_scaler.fit_transform(self.unnormalized_data[idx]))
                else:
                    # print(f"[INFO] Out is {out}.  MinMax scaler fit_transform in progress.")
                    self.scaler_list.append(self.min_max.fit_transform(self.unnormalized_data[idx]))
                self.normalized_data.append(pd.DataFrame(self.scaler_list[idx],
                                                    index=['Close EMA14 Distance',
                                                           'Close EMA30 Distance',
                                                           'Close Fib1 Distance',
                                                           'Close Fib2 Distance',
                                                           'Num Consec Candle Dir',
                                                           'Upper Keltner Close Diff',
                                                           'Lower Keltner Close Diff',
                                                           'Open',
                                                           'Close'] if out == 1 else []
                                                                                                            ))
                # print(self.normalized_data,self.unnormalized_data)
            except Exception as e:
                print(f'[ERROR] Failed to normalize data points!\r\nException: {e}')
                print(self.unnormalized_data[idx])
                raise Exception(e)
        return 0

    '''
    Do PCA on vectors
    '''

    def pca(self):
        self.pca = PCA(n_components=1)
        try:
            self.pca_normalized_data = pd.DataFrame(self.pca.fit_transform(self.normalized_data))
            print(self.pca_normalized_data)
        except Exception as e:
            print(f"[ERROR] Failed to fit transform on normalized data!\r\nException: {e}")
            raise Exception(e)
        # # Use for debugging num components needed
        # plt.rcParams["figure.figsize"] = (12, 6)
        # fig, ax = plt.subplots()
        # xi = np.arange(1, 6, step=1)
        # y = np.cumsum(pca.explained_variance_ratio_)
        # plt.ylim(0.0, 1.1)
        # plt.plot(xi, y, marker='o', linestyle='--', color='b')
        # plt.xlabel('Number of Components')
        # plt.xticks(np.arange(0, 11, step=1))  # change from 0-based array index to 1-based human-readable label
        # plt.ylabel('Cumulative variance (%)')
        # plt.title('The number of components needed to explain variance')
        # plt.axhline(y=0.95, color='r', linestyle='-')
        # plt.text(0.5, 0.85, '95% cut-off threshold', color='red', fontsize=16)
        # ax.grid(axis='x')
        # plt.show()

        print(f"[INFO] Explained variance ratio: {self.pca.explained_variance_ratio_}")
        print(f"[INFO] Singular values: {self.pca.singular_values_}")
        return self.pca

    def feature_selection(self, x, y):
        # configure to select all features
        fs = SelectKBest(score_func=f_regression, k='all')
        # learn relationship from training data
        fs.fit(self.pca)
        # transform train input data
        X_train_fs = fs.transform(self.pca)
        for i in range(len(fs.scores_)):
            print('Feature %d: %f' % (i, fs.scores_[i]))
        # plot the scores
        plt.bar([i for i in range(len(fs.scores_))], fs.scores_)
        plt.show()

    '''
        Unnormalize data
    '''

    # def unnormalize(self, data, out: int = 1, has_actuals=False):
    #     if 2 <= out <= 4:
    #         trainPredict_dataset_like = np.zeros(shape=(14, 6 if has_actuals else 5))
    #         # print(trainPredict_dataset_like.iloc[5, -1])
    #         trainPredict_dataset_like[5, -1] = data.iloc[0, 0]  # Open
    #         trainPredict_dataset_like[6, -1] = data.iloc[1, 0]  # High
    #         trainPredict_dataset_like[7, -1] = data.iloc[2, 0]  # Low
    #         trainPredict_dataset_like[8, -1] = data.iloc[3, 0]  # Close
    #         scaler = self.standard_scaler.inverse_transform(trainPredict_dataset_like)[:, -1]  # Keep modified part only
    #     else:
    #         scaler = self.min_max.fit(self.unnormalized_data)
    #     tmp_data = pd.DataFrame(columns=['Close EMA14 Distance', 'Close EMA30 Distance',
    #                                      'Close Fib1 Distance', 'Close Fib2 Distance', 'Num Consec Candle Dir',
    #                                      'Upper Keltner Close Diff', 'Lower Keltner Close Diff',
    #                                      'Open',
    #                                      'Close'] if out == 1 else \
    #         ['Last2Volume Cur Volume Diff', 'Open Upper Kelt Diff',
    #          'Open Lower Kelt Diff', 'High Upper Kelt Diff',
    #          'High Lower Kelt Diff', 'Low Upper Kelt Diff',
    #          'Low Lower Kelt Diff', 'Close Upper Kelt Diff',
    #          'Close Lower Kelt Diff', 'EMA 14 30 Diff',
    #          'Base Fib High Diff', 'Base Fib Low Diff',
    #          'Next1 Fib High Diff', 'Next1 Fib Low Diff',
    #          'Next2 Fib High Diff', 'Next2 Fib Low Diff',
    #          'Open', 'High', 'Low', 'Close',
    #          'Last3High Base Fib', 'Last3Low Base Fib',
    #          'Last3High Next1 Fib', 'Last3Low Next1 Fib',
    #          'Last3High Next2 Fib', 'Last3Low Next2 Fib'] if out == 2 else \
    #             ['Upper Kelt',
    #              'Lower Kelt', 'Middle Kelt', 'EMA 14', 'EMA 30',
    #              'Open', 'High', 'Low', 'Close',
    #              'Last3High', 'Last3Low'] if out == 3 else ['Upper Kelt',
    #                                                         'Lower Kelt', 'Middle Kelt', 'EMA 14', 'EMA 30',
    #                                                         'Open', 'High', 'Low', 'Close', 'Base Fib',
    #                                                         'Next1 Fib', 'Next2 Fib',
    #                                                         'Last3High', 'Last3Low'] if out == 4 else [])
    #     # Set data manually to preserve order
    #     if 2 <= out <= 4:
    #         tmp_data.loc[0, 'Open'] = scaler[5]
    #         tmp_data.loc[0, 'High'] = scaler[6]
    #         tmp_data.loc[0, 'Low'] = scaler[7]
    #         tmp_data.loc[0, 'Close'] = scaler[8]
    #     elif out == 1:
    #         tmp_data.loc[0, 'Open'] = data['Open']
    #     # if 3 <= out <= 4: # Add high/low
    #     #     tmp_data['High'] = (data['High'] * self.w['High']) if out != 4 else data['High']
    #     #     tmp_data['Low'] = (data['Low'] * self.w['Low']) if out != 4 else data['Low']
    #     #     tmp_data['Open'] = (tmp_data['Open'] * self.w['Open']) if out != 4 else data['Open']
    #     #     tmp_data['Close'] = (tmp_data['Close'] * self.w['Close']) if out != 4 else data['Close']
    #     return tmp_data.transpose()
# norm = Normalizer()
# norm.read_data("2016-03-18","CCL")
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()
