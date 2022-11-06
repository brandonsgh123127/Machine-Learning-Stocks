import os
import shutil
import random
from datetime import datetime, timedelta

import pandas as pd
from keras import regularizers, layers, initializers, optimizers, callbacks
from numpy import reshape, asarray, float_, stack
from tensorflow import device
from tensorflow.python.keras import Input
from tensorflow.python.keras.models import Model

from V1.machine_learning.model import NN_Model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import sys
from V1.data_generator.generate_sample import Sample
from pathlib import Path
import threading
from V1.machine_learning.neural_framework import Neural_Framework
from pandas.tseries.holiday import USFederalHolidayCalendar
from mysql.connector import errorcode
import mysql.connector
import xml.etree.ElementTree as ET
from V1.threading_impl.Thread_Pool import Thread_Pool
import asyncio

class Network(Neural_Framework):
    def __init__(self, epochs: int, batch_size: int):
        super().__init__(epochs, batch_size)
        self.sampler: Sample = None
    # Used for generation of data via the start
    def generate_sample(self, _has_actuals=False, rand_date=None, interval = '1d',opt_fib_vals = []):
        path = Path(os.getcwd()).absolute()
        self.sampler.reset_data()
        self.sampler.set_ticker(
            self.choose_random_ticker(Neural_Framework, csv_file=f'{path}/data/watchlist/default.csv'))
        try:
            if self.model_choice <= 6:
                self.sampler.generate_sample(_has_actuals=_has_actuals, out=8, rand_date=rand_date, skip_db=True,interval=interval,opt_fib_vals=opt_fib_vals)
            else:
                self.sampler.generate_sample(_has_actuals=_has_actuals, out=8, rand_date=rand_date, skip_db=True,interval=interval,opt_fib_vals=opt_fib_vals)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('[Error] Failed batch!\n Exception: ', str(e))
            return 1
        except Exception as e:
            print(str(e))
            return 1
        try:
            self.sampler.data = self.sampler.data.drop(['High', 'Low'], axis=1)
        except:
            pass
        return 0

    def run_model(self, nn: NN_Model = None, rand_date=False,interval='1d'):
        self.sampler = Sample()
        models = {}
        try:
            os.mkdir(f"./logs")
        except:
            pass
        try:
            os.mkdir(f"./logs/{self.model_name}")
        except:
            pass
        # Retrieve all necessary data into training data
        for i in range(1, self.EPOCHS):
            print(f'\n\n\nEPOCH {i} -- {self.model_choice}')
            train = []
            train_targets = []
            BATCHES = self.BATCHES
            j = 1
            while j <= BATCHES:
                try:
                    self.generate_sample(True, rand_date, interval)
                except Exception as e:
                    print('[ERROR] Failed to generate sample\n', str(e))
                    continue
                try:
                    if self.model_choice < 4:
                        train.append(reshape(self.sampler.normalized_data.iloc[:-1].to_numpy(), (1, 126)))
                    else:
                        train.append(reshape(self.sampler.normalized_data.iloc[:-1].to_numpy(), (1, 126)))
                    # print(len(self.sampler.normalized_data),self.sampler.normalized_data.iloc[-15:])
                    tmp = self.sampler.normalized_data.iloc[-1:]
                    tmp = pd.concat([pd.DataFrame([tmp['Close'].to_numpy()])])
                    train_targets.append(reshape(tmp.to_numpy(), (1, 1)))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)

                    print('[ERROR] Failed to specify train_target value!\n Exception: ', str(e))
                    continue
                except:
                    print('[ERROR] Unknown error has occurred while training!')
                    continue
                j = j + 1
            train = asarray(train).astype(float_)
            train_targets = asarray(train_targets).astype(float_)
            # Profile a range of batches, e.g. from 2 to 5.
            tensorboard_callback = callbacks.TensorBoard(
                log_dir=f'./logs/{self.model_name}', profile_batch=(2, 5))
            # Use fit for generating with ease.  Validation data included for analysis of loss
            stacked_train=stack(train)
            stacked_train_targets=stack(train_targets)
            disp = nn.model.fit(x=stacked_train, y=stacked_train_targets, batch_size=75, epochs=1,
                          validation_split=0.177,
                          callbacks=[tensorboard_callback])
            del train,train_targets, stacked_train,stacked_train_targets
            models[i] = disp.history
            nn.save_model()

        return models

listLock = threading.Lock()


def check_db_cache(cnx: mysql.connector.connect = None, ticker: str = None, has_actuals: bool = False,
                   name: str = "relu_1layer", force_generation: bool = False, interval='1d'):
    # Before inserting data, check cached data, verify if there is data there...
    from_date_id = None
    to_date_id = None
    stock_id = None

    # First, get to date id
    check_cache_tdata_db_stmt = ''
    is_utilizing_yfinance = False
    # Retrieve the stock-id, and data-point id in a single select statement
    if '1d' in interval:
        check_cache_tdata_db_stmt = """SELECT `stocks`.`dailydata`.`data-id`,
         `stocks`.`dailydata`.`stock-id` FROM `stocks`.`dailydata` USE INDEX (`id-and-date`)
        INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`dailydata`.`stock-id`
         AND `stocks`.`dailydata`.`date`= DATE(%(date)s)
             """
    elif '1wk' in interval:
        check_cache_tdata_db_stmt = """SELECT `stocks`.`weeklydata`.`data-id`,
             `stocks`.`weeklydata`.`stock-id` FROM `stocks`.`weeklydata` USE INDEX (`id-and-date`)
            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`weeklydata`.`stock-id`
             AND `stocks`.`weeklydata`.`date`= DATE(%(date)s)
             """
    elif '1m' in interval:
        check_cache_tdata_db_stmt = """SELECT `stocks`.`monthlydata`.`data-id`,
         `stocks`.`monthlydata`.`stock-id` FROM `stocks`.`monthlydata` USE INDEX (`id-and-date`)
        INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`monthlydata`.`stock-id`
         AND `stocks`.`monthlydata`.`date`= DATE(%(date)s)
             """
    elif '1y' in interval:
        check_cache_tdata_db_stmt = """SELECT `stocks`.`yearlydata`.`data-id`,
             `stocks`.`yearlydata`.`stock-id` FROM `stocks`.`yearlydata` USE INDEX (`id-and-date`)
            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`yearlydata`.`stock-id`
             AND `stocks`.`yearlydata`.`date`= DATE(%(date)s)
             """
    else:
        is_utilizing_yfinance = True
        check_cache_tdata_db_stmt = f"""SELECT `stocks`.`{interval}data`.`data-id`,
             `stocks`.`{interval}data`.`stock-id` FROM `stocks`.`{interval}data` USE INDEX (`id-and-date`)
            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`{interval}data`.`stock-id`
             AND `stocks`.`{interval}data`.`date`= %(date)s
             """

    # check if currently weekend/holiday
    valid_datetime = datetime.utcnow()
    holidays = USFederalHolidayCalendar().holidays(start=valid_datetime,
                                                   end=(valid_datetime + datetime.timedelta(days=7))).to_pydatetime()
    valid_date = valid_datetime.date()
    if '1wk' not in interval and '1mo' not in interval:
        if (
                datetime.utcnow().hour <= 14 and datetime.utcnow().minute < 30):  # if current time is before 9:30 AM EST, go back a day
            valid_datetime = (valid_datetime - timedelta(days=1))
            valid_date = (valid_date - timedelta(days=1))
        if valid_date in holidays and 0 <= valid_date.weekday() <= 4:  # week day holiday
            valid_datetime = (valid_datetime - timedelta(days=1))
            valid_date = (valid_date - timedelta(days=1))
        if valid_date.weekday() == 5:  # if saturday
            valid_datetime = (valid_datetime - timedelta(days=1))
            valid_date = (valid_date - timedelta(days=1))
        if valid_date.weekday() == 6:  # if sunday
            valid_datetime = (valid_datetime - timedelta(days=2))
            valid_date = (valid_date - timedelta(days=2))
        if valid_date in holidays:
            valid_datetime = (valid_datetime - timedelta(days=1))
            valid_date = (valid_date - timedelta(days=1))
        if has_actuals:  # go back a day
            valid_datetime = (valid_datetime - timedelta(days=1))
            valid_date = (valid_date - timedelta(days=1))
            if valid_date.weekday() == 5:  # if saturday
                valid_datetime = (valid_datetime - timedelta(days=1))
                valid_date = (valid_date - timedelta(days=1))
            if valid_date.weekday() == 6:  # if sunday
                valid_datetime = (valid_datetime - timedelta(days=2))
                valid_date = (valid_date - timedelta(days=2))
            if valid_date in holidays:
                valid_datetime = (valid_datetime - timedelta(days=1))
                valid_date = (valid_date - timedelta(days=1))
        if is_utilizing_yfinance:  # This means this is a minute/HR/Days interval.  We'll need to set the time as part of the interval
            if 'h' in interval:
                valid_datetime = valid_datetime.replace(minute=0, second=0, microsecond=0)
            elif 'm' in interval:
                min_value = interval.replace('m', '')
                valid_datetime = valid_datetime.replace(
                    minute=int(min_value) * int(valid_datetime.minute // int(min_value)), second=0, microsecond=0)
            elif 'd' in interval:
                valid_datetime = valid_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    elif '1wk' in interval:
        begin_day = abs(valid_date.weekday())
        if begin_day != 0:
            valid_date = valid_date - timedelta(days=begin_day)
            valid_datetime = valid_datetime - timedelta(days=begin_day)
    elif '1mo' in interval:
        valid_datetime = (valid_datetime.replace(day=1))
        valid_date = (valid_date.replace(day=1))
    # print(valid_datetime,flush=True)
    retrieve_tdata_result = cnx.execute(check_cache_tdata_db_stmt, {'stock': f'{ticker.upper()}',
                                                                    'date': valid_datetime.strftime('%Y-%m-%d')},
                                        multi=True)
    for retrieve_result in retrieve_tdata_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            print(f'[INFO] Couldn\'t retrieve data_id for {ticker} for date {valid_datetime.strftime("%Y-%m-%d")}. Retrieving only stock_id.')
            check_stockid_db_stmt = """SELECT `stocks`.`stock`.`id` 
             FROM stocks.`stock` USE INDEX (`stockid`) WHERE
               `stocks`.`stock`.`stock` = %(stock)s
                """
            result = cnx.execute(check_stockid_db_stmt, {'stock': f'{ticker.upper()}'
                                                         }, multi=True)

            for retrieve_result in retrieve_tdata_result:
                id_res = retrieve_result.fetchall()
                if len(id_res) == 0:
                    print('[ERROR] No stock id found! Breaking!!')
                    raise Exception('[ERROR] Could not find stock id!')
                else:
                    stock_id = id_res[0][0].decode('latin1')
                    print('[INFO] Retrieved stock ID')

            break
        else:
            stock_id = id_res[0][1].decode('latin1')
            to_date_id = id_res[0][0].decode('latin1')

    if '1wk' in interval:
        valid_datetime = valid_datetime - datetime.timedelta(days=250)
        valid_date = valid_date - datetime.timedelta(days=250)
        begin_day = abs(valid_date.weekday())
        if begin_day != 0:
            valid_date = valid_date - datetime.timedelta(days=begin_day)
            valid_datetime = valid_datetime - datetime.timedelta(days=begin_day)
    elif '1mo' in interval:
        valid_datetime = (valid_datetime - datetime.timedelta(days=600))
        valid_date = (valid_date - datetime.timedelta(days=600))
        valid_datetime = (valid_datetime.replace(day=1))
        valid_date = (valid_date.replace(day=1))

    # Check nn-data table after retrieval of from-date and to-date id's
    if '1d' in interval:
        check_cache_fdata_db_stmt = """SELECT `stocks`.`dailydata`.`data-id` 
         FROM stocks.`dailydata` USE INDEX (`stockid-and-date`)
         WHERE stocks.`dailydata`.`stock-id` = %(stock-id)s
           AND stocks.`dailydata`.`date` = DATE(%(date)s)
            """
    elif '1wk' in interval:
        check_cache_fdata_db_stmt = """SELECT `stocks`.`weeklydata`.`data-id` 
         FROM stocks.`weeklydata` USE INDEX (`stockid-and-date`)
         WHERE stocks.`weeklydata`.`stock-id` = %(stock-id)s
           AND stocks.`weeklydata`.`date` = DATE(%(date)s)
            """
    elif '1m' in interval:
        check_cache_fdata_db_stmt = """SELECT `stocks`.`monthlydata`.`data-id` 
         FROM stocks.`monthlydata` USE INDEX (`stockid-and-date`)
         WHERE stocks.`monthlydata`.`stock-id` = %(stock-id)s
           AND stocks.`monthlydata`.`date` = DATE(%(date)s)
            """
    elif '1y' in interval:
        check_cache_fdata_db_stmt = """SELECT `stocks`.`yearlydata`.`data-id` 
         FROM stocks.`yearlydata` USE INDEX (`stockid-and-date`)
         WHERE stocks.`yearlydata`.`stock-id` = %(stock-id)s
           AND stocks.`yearlydata`.`date` = DATE(%(date)s)
            """
    else:
        check_cache_fdata_db_stmt = f"""SELECT `stocks`.`{interval}data`.`data-id` 
         FROM stocks.`{interval}data` USE INDEX (`stockid-and-date`)
         WHERE stocks.`{interval}data`.`stock-id` = %(stock-id)s
           AND stocks.`{interval}data`.`date` = %(date)s
            """

    retrieve_data_result = cnx.execute(check_cache_fdata_db_stmt, {'stock-id': stock_id,
                                                                   'date': valid_date if not is_utilizing_yfinance else
                                                                   valid_datetime.strftime("%Y-%m-%d %H:%M:%S")},
                                       multi=True)
    for retrieve_result in retrieve_data_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            if not force_generation:
                print(
                    f'[INFO] Failed to locate a from data-id  for {ticker} on {valid_datetime.strftime("%Y-%m-%d")} with has_actuals: {has_actuals}')
            break
        else:
            from_date_id = id_res[0][0].decode('latin1')

    # Check nn-data table after retrieval of from-date and to-date id's
    if '1d' in interval:
        check_cache_nn_db_stmt = """SELECT `stocks`.`daily-nn-data`.`close`,`stocks`.`daily-nn-data`.`open` 
         FROM stocks.`daily-nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
        `stock-id` = %(stock-id)s
           AND `stocks`.`daily-nn-data`.`from-date-id` = %(from-date-id)s
           AND `stocks`.`daily-nn-data`.`to-date-id` = %(to-date-id)s
            AND `stocks`.`daily-nn-data`.`model` = %(model)s
            """
    elif '1wk' in interval:
        check_cache_nn_db_stmt = """SELECT `stocks`.`weekly-nn-data`.`close`,`stocks`.`weekly-nn-data`.`open` 
         FROM stocks.`weekly-nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
        `stock-id` = %(stock-id)s
           AND `stocks`.`weekly-nn-data`.`from-date-id` = %(from-date-id)s
           AND `stocks`.`weekly-nn-data`.`to-date-id` = %(to-date-id)s
            AND `stocks`.`weekly-nn-data`.`model` = %(model)s
            """
    elif '1m' in interval:
        check_cache_nn_db_stmt = """SELECT `stocks`.`monthly-nn-data`.`close`,`stocks`.`monthly-nn-data`.`open` 
         FROM stocks.`monthly-nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
        `stock-id` = %(stock-id)s
           AND `stocks`.`monthly-nn-data`.`from-date-id` = %(from-date-id)s
           AND `stocks`.`monthly-nn-data`.`to-date-id` = %(to-date-id)s
            AND `stocks`.`monthly-nn-data`.`model` = %(model)s
            """
    elif '1y' in interval:
        check_cache_nn_db_stmt = """SELECT `stocks`.`yearly-nn-data`.`close`,`stocks`.`yearly-nn-data`.`open` 
         FROM stocks.`yearly-nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
        `stock-id` = %(stock-id)s
           AND `stocks`.`yearly-nn-data`.`from-date-id` = %(from-date-id)s
           AND `stocks`.`yearly-nn-data`.`to-date-id` = %(to-date-id)s
            AND `stocks`.`yearly-nn-data`.`model` = %(model)s
            """
    else:
        check_cache_nn_db_stmt = f"""SELECT `stocks`.`{interval}-nn-data`.`close`,`stocks`.`{interval}-nn-data`.`open` 
         FROM stocks.`{interval}-nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
        `stock-id` = %(stock-id)s
           AND `stocks`.`{interval}-nn-data`.`from-date-id` = %(from-date-id)s
           AND `stocks`.`{interval}-nn-data`.`to-date-id` = %(to-date-id)s
            AND `stocks`.`{interval}-nn-data`.`model` = %(model)s
            """
    try:

        check_cache_studies_db_result = cnx.execute(check_cache_nn_db_stmt, {'stock-id': stock_id,
                                                                             'from-date-id': from_date_id,
                                                                             'to-date-id': to_date_id,
                                                                             'model': name},
                                                    multi=True)
        # Retrieve date, verify it is in date range, remove from date range
        for result in check_cache_studies_db_result:
            result = result.fetchall()
            for res in result:
                # Set predicted value
                if not force_generation:
                    return (
                        pd.DataFrame({'Close': float(res[0]), 'Open': float(res[1])}, index=[0]), stock_id,
                        from_date_id,
                        to_date_id)
    except mysql.connector.errors.IntegrityError:  # should not happen
        cnx.close()
        pass
    except Exception as e:
        print('[ERROR] Failed to check cached nn-data!\n', str(e))
        cnx.close()
        raise mysql.connector.errors.DatabaseError()
    return None


"""Load Specified Model"""


def load(nn: NN_Model = None, ticker: str = None, has_actuals: bool = False, name: str = "relu_1layer",
         force_generation=False,
         device_opt: str = '/device:GPU:0', rand_date=False, data: tuple = (), interval: str = '1d', sampler: Sample = None,
         opt_fib_vals: list = []):
    # Check to see if empty data value was passed in.
    # If true, exit out of function
    if data is None:
        return None, None, None, None, None, None

    # Connect to local DB
    path = Path(os.getcwd()).absolute()
    tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(path))
    root = tree.getroot()
    try:
        db_con = mysql.connector.connect(
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

    cnx = db_con.cursor(buffered=True)
    predicted = None
    from_date_id = None
    to_date_id = None
    stock_id = None

    try:
        vals = check_db_cache(cnx, ticker, has_actuals, name, force_generation, interval=interval)
        predicted = vals[0]
        stock_id = vals[1]
        from_date_id = vals[2]
        to_date_id = vals[3]
        del vals
    except Exception as e:
        pass

    # Start ML calculations
    if predicted is None or force_generation:
        # sampler.__init__(ticker)
        # If data is populated, go ahead and utilize it, skip over data check for normalizer...
        if isinstance(data,tuple) and len(data) != 0:
            sampler.set_sample_data(data[0], data[1], data[2], data[3])
        # if not type tuple, then this means that no data was passed in...
        train = None
        sampler.generate_sample(_has_actuals=has_actuals, out=8, rand_date=rand_date, interval=interval,opt_fib_vals=opt_fib_vals)
        sampler.trim_data(has_actuals)
        try:  # verify there is no extra 'index' column
            sampler.data = sampler.data.drop(['index'], axis=1)
        except Exception as e:
            # print('[ERROR] Failed to drop "index" from sampler data',str(e))
            pass
        try:
            sampler.data = sampler.data.drop(['Date'], axis=1)
        except Exception as e:
            print('[ERROR] Failed to drop "High" and "Low" from sampler data!', str(e))
        if not force_generation:
            print(f'[INFO] Did not query all specified dates within range for nn-data retrieval!')
        with listLock:
            # Verify that the data has at least the correct shape needed...
            try:
                reshape(sampler.normalized_data.iloc[-14:].to_numpy(), (1, 1, 126))
            except Exception as e:
                print(f'[ERROR] Couldn\'t generate ML output for ticker {ticker} for date id range {from_date_id} to {to_date_id}.\n\tException: {e}')
                return None, None, None, None, None, None
            with device(device_opt):
                if has_actuals:
                    train = (reshape(sampler.normalized_data.iloc[-15:-1].to_numpy(), (1, 1, 126)))
                else:
                    train = (reshape(sampler.normalized_data[-14:].to_numpy(), (1, 1, 126)))
                train = asarray(train).astype(float_)
                stacked_train = stack(train)
                prediction = nn.model.predict(stacked_train)
                del train, stacked_train
        predicted = pd.DataFrame((reshape(prediction, (1, 1))), columns=['Close'])  # NORMALIZED
        is_utilizing_yfinance = False
        # Upload data to DB given prediction has finished
        if '1d' in interval:
            check_cache_nn_db_stmt = """REPLACE INTO `stocks`.`daily-nn-data` (`nn-id`, `stock-id`, 
                                                                    `from-date-id`,`to-date-id`,
                                                                    `model`,`close`,`open` 
                                                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                            %(to-date-id)s,%(model)s,%(close)s,%(open)s)
            """
        elif '1wk' in interval:
            check_cache_nn_db_stmt = """REPLACE INTO `stocks`.`weekly-nn-data` (`nn-id`, `stock-id`, 
                                                                    `from-date-id`,`to-date-id`,
                                                                    `model`,`close`,`open` 
                                                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                            %(to-date-id)s,%(model)s,%(close)s,%(open)s)
            """
        elif '1m' in interval:
            check_cache_nn_db_stmt = """REPLACE INTO `stocks`.`monthly-nn-data` (`nn-id`, `stock-id`, 
                                                                    `from-date-id`,`to-date-id`,
                                                                    `model`,`close`,`open` 
                                                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                            %(to-date-id)s,%(model)s,%(close)s,%(open)s)
            """
        elif '1y' in interval:
            check_cache_nn_db_stmt = """REPLACE INTO `stocks`.`yearly-nn-data` (`nn-id`, `stock-id`, 
                                                                    `from-date-id`,`to-date-id`,
                                                                    `model`,`close`,`open` 
                                                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                            %(to-date-id)s,%(model)s,%(close)s,%(open)s)
            """
        else:
            is_utilizing_yfinance = True
            check_cache_nn_db_stmt = f"""REPLACE INTO `stocks`.`{interval}-nn-data` (`nn-id`, `stock-id`, 
                                                                    `from-date-id`,`to-date-id`,
                                                                    `model`,`close`,`open` 
                                                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                            %(to-date-id)s,%(model)s,%(close)s,%(open)s)
            """
        if from_date_id is not None and to_date_id is not None:
            try:
                check_cache_studies_db_result = cnx.execute(check_cache_nn_db_stmt,
                                                            {'id': f'{from_date_id}{to_date_id}{ticker.upper()}{name}',
                                                             'stock-id': stock_id,
                                                             'from-date-id': from_date_id,
                                                             'to-date-id': to_date_id,
                                                             'model': name,
                                                             'close': str(predicted['Close'].iloc[0])})
                db_con.commit()
            except mysql.connector.errors.IntegrityError:
                cnx.close()
                pass
            except Exception as e:
                print(f'[ERROR] Failed to insert id {stock_id} nn-data for model {name}!\nException:\n', str(e))
                cnx.close()
                pass
        cnx.close()

    unnormalized_prediction = sampler.unnormalize(predicted).to_numpy()

    # space = pd.DataFrame([[0,0]],columns=['Open','Close'])
    unnormalized_predict_values = sampler.data.append(pd.DataFrame([[unnormalized_prediction[0, 1] +
                                                                     sampler.data['Close'].iloc[-1]]],
                                                                   columns=['Close']), ignore_index=True)
    del unnormalized_prediction
    predicted_unnormalized = pd.concat([unnormalized_predict_values])
    del unnormalized_predict_values
    return sampler.unnormalize(predicted), sampler.unnormalized_data.tail(
        1), predicted_unnormalized, sampler.keltner, sampler.fib, sampler.studies


"""
Run Specified Model by creating model and running batches/epochs.

"""


def run(epochs, batch_size, choice=5):
    neural_net = Network(epochs, batch_size)
    nn = NN_Model(choice)
    if nn is None:
        nn = NN_Model.create_model()
    intervals=['1d','1wk','1mo']
    random_interval = random.choice(intervals)
    model = neural_net.run_model(nn,rand_date=True, interval=random_interval)
    for i in range(1, neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)


def copy_logs(path: Path = None, dest_folder: str = ""):
    shutil.move(f'{path}/logs/', f'{path}/old_logs/{dest_folder}', copy_function=shutil.copytree)
    os.mkdir(f'{path}/logs/')


def main():
    thread_manager = Thread_Pool(amount_of_threads=3)
    path = Path(os.getcwd()).absolute()
    # thread_manager.start_worker(threading.Thread(target=run, args=(50, 75, "relu_multilayer_l2")))
    # run(50,75,'relu_1layer')
    # copy_logs(path,'relu_1layer')
    thread_manager.start_worker(threading.Thread(target=run, args=(50, 75, "relu_2layer_0regularization")))
    # run(50,75,'relu_2layer')
    # copy_logs(path,'relu_2layer')
    # thread_manager.start_worker(threading.Thread(target=run, args=(50, 75, "relu_2layer_dropout_l2_noout")))
    # thread_manager.join_workers()
    # run(50,75,'relu_2layer_dropout')
    # copy_logs(path,'relu_2layer_dropout')
    thread_manager.start_worker(threading.Thread(target=run, args=(50, 75, "relu_2layer_l1l2")))
    # run(50,75,'relu_2layer_l1l2')
    # copy_logs(path,'relu_2layer_l1l2')
    thread_manager.start_worker(threading.Thread(target=run, args=(49, 75, "relu_1layer_l2")))
    thread_manager.join_workers()
    # run(50,75,'relu_1layer_l2')
    # copy_logs(path,'relu_1layer_l2')
    # thread_manager.start_worker(threading.Thread(target=run, args=(50, 75, "relu_2layer_dropout_l2_out")))
    # thread_manager.join_workers()
    # run(50,75,'relu_2layer_dropout_l1_l2')
    # copy_logs(path,'relu_2layer_dropout_l1_l2')
    # net=Network(1,1)
    # load("SPY", False, "relu_1layer", True)


if __name__ == "__main__":
    main()
