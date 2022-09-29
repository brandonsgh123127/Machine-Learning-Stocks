import numpy as np
import pytz
from scipy.signal import argrelextrema

from V1.data_gather._data_gather import Gather
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
import datetime
import threading
import gc
import mysql.connector
import sys, os

'''
    This class manages stock-data implementations of studies. 
    As of now, EMA is only implemented, as this is the core indicator for our
    machine learning model.
    save data option enabled
'''


class Studies(Gather):
    def __repr__(self):
        return 'stock_data.studies object <%s>' % ",".join(self.indicator)

    def __init__(self, indicator, force_generate=False):
        self.data_ids = None
        self.study_id = None
        with threading.Lock():
            super().__init__(indicator)
            self.set_indicator(indicator)
        self.applied_studies = pd.DataFrame(dtype=float)
        self.fibonacci_extension = pd.DataFrame()
        self.keltner = pd.DataFrame()
        self.timeframe = "1d"
        self.listLock = threading.Lock()
        # pd.set_option('display.max_rows',300)
        # pd.set_option('display.max_columns',10)
        self.Date = pd.DataFrame(columns=['Date'])
        self.Open = pd.DataFrame(columns=['Open'], dtype='float')
        self.High = pd.DataFrame(columns=['High'], dtype='float')
        self.Low = pd.DataFrame(columns=['Low'], dtype='float')
        self.Close = pd.DataFrame(columns=['Close'], dtype='float')
        self.AdjClose = pd.DataFrame(columns=['Adj Close'], dtype='float')

        self._force_generate = force_generate

    def set_force_generate(self, is_force_generation: bool):
        self._force_generate = is_force_generation
    def set_timeframe(self, new_timeframe):
        self.timeframe = new_timeframe

    def get_timeframe(self):
        return self.timeframe

    # Save EMA to self defined applied_studies
    async def apply_ema(self, length, span=None, half=None, skip_db=False, interval='1d'):
        # Now, Start the process for inserting ema data...
        date_range = [d.strftime('%Y-%m-%d') for d in
                      pd.date_range(self.data.iloc[0]['Date'], self.data.iloc[-1]['Date'])]  # start/end date list
        try:  # Try connection to db_con, if not, connect to
            self.ema_cnx = self.db_con.cursor()
        except:
            self.ema_cnx = self.db_con2.cursor()

        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        with threading.Lock():
            if not skip_db:
                self.ema_cnx.autocommit = True
                # print('[INFO] Select stock')
                resultado = self.ema_cnx.execute(select_stmt, {'stock': self.indicator.upper()}, multi=True)
                for result in resultado:
                    # Query new stock, id
                    if len(result.fetchall()) == 0:
                        print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                        raise mysql.connector.Error
                    else:
                        select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                        # print('[INFO] Select study id')
                        study_result = self.ema_cnx.execute(select_study_stmt, {'study': f'ema{length}'}, multi=True)
                        for s_res in study_result:
                            # Non existent DB value
                            study_id_res = s_res.fetchall()
                            if len(study_id_res) == 0:
                                print(
                                    f'[INFO] Failed to query study named ema{length} from database! Creating new Study...\n')
                                insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                                    VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(ema)s)"""
                                # Insert new study into DB
                                try:
                                    insert_result = self.ema_cnx.execute(insert_study_stmt, {'id': f'{length}',
                                                                                             'ema': f'ema{length}'},
                                                                         multi=True)
                                    self.db_con.commit()

                                    # Now get the id from the db
                                    retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                                    retrieve_study_id_result = self.ema_cnx.execute(retrieve_study_id_stmt,
                                                                                    {'study': f'ema{length}'},
                                                                                    multi=True)
                                    for r in retrieve_study_id_result:
                                        id_result = r.fetchall()
                                        self.study_id = id_result[0][0].decode('latin1')
                                except mysql.connector.errors.IntegrityError:
                                    pass
                                except Exception as e:
                                    print(f'[ERROR] Failed to Insert study into stocks.study named ema{length}!\n',
                                          str(e))
                                    raise mysql.connector.Error

                            else:
                                # Get study_id
                                self.study_id = study_id_res[0][0].decode('latin1')

                    holidays = USFederalHolidayCalendar().holidays(start=f'{datetime.datetime.now().year}-01-01',
                                                                   end=f'{datetime.datetime.now().year}-12-31').to_pydatetime()
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
                    study_data = pd.DataFrame(columns=[f'ema{length}'])
                    # Before inserting data, check cached data, verify if there is data there...
                    try:  # Try connection to db_con, if not, connect to
                        self.ema_cnx = self.db_con.cursor()
                    except:
                        self.ema_cnx = self.db_con2.cursor()
                    self.ema_cnx.autocommit = True
                    is_utilizing_yfinance = False
                    if '1d' in interval:
                        check_cache_studies_db_stmt = """SELECT `stocks`.`dailydata`.`date`,
                        `stocks`.`daily-study-data`.`val1` 
                         FROM stocks.`dailydata` USE INDEX (`id-and-date`)
                          INNER JOIN stocks.stock USE INDEX(`stockid`)
                        ON `stock-id` = stocks.stock.`id` 
                          AND stocks.stock.`stock` = %(stock)s
                            AND `stocks`.`dailydata`.`date` >= DATE(%(bdate)s)
                            AND `stocks`.`dailydata`.`date` <= DATE(%(edate)s)
                           INNER JOIN stocks.`daily-study-data` USE INDEX (`ids`)
                            ON
                            stocks.stock.`id` = stocks.`daily-study-data`.`stock-id`
                            AND stocks.`daily-study-data`.`data-id` = stocks.`dailydata`.`data-id`
                            AND stocks.`daily-study-data`.`study-id` = %(id)s 
                            ORDER BY stocks.`dailydata`.`date` ASC
                            """
                    elif '1wk' in interval:
                        check_cache_studies_db_stmt = """SELECT `stocks`.`weeklydata`.`date`,
                        `stocks`.`weekly-study-data`.`val1` 
                         FROM stocks.`weeklydata` USE INDEX (`id-and-date`)
                          INNER JOIN stocks.stock USE INDEX(`stockid`)
                        ON `stock-id` = stocks.stock.`id` 
                          AND stocks.stock.`stock` = %(stock)s
                            AND `stocks`.`weeklydata`.`date` >= DATE(%(bdate)s)
                            AND `stocks`.`weeklydata`.`date` <= DATE(%(edate)s)
                           INNER JOIN stocks.`weekly-study-data` USE INDEX (`ids`)
                            ON
                            stocks.stock.`id` = stocks.`weekly-study-data`.`stock-id`
                            AND stocks.`weekly-study-data`.`data-id` = stocks.`weeklydata`.`data-id`
                            AND stocks.`weekly-study-data`.`study-id` = %(id)s 
                            ORDER BY stocks.`weeklydata`.`date` ASC
                            """
                    elif '1m' in interval:
                        check_cache_studies_db_stmt = """SELECT `stocks`.`monthlydata`.`date`,
                            `stocks`.`monthly-study-data`.`val1` 
                             FROM stocks.`monthlydata` USE INDEX (`id-and-date`)
                              INNER JOIN stocks.stock USE INDEX(`stockid`)
                            ON `stock-id` = stocks.stock.`id` 
                              AND stocks.stock.`stock` = %(stock)s
                                AND `stocks`.`monthlydata`.`date` >= DATE(%(bdate)s)
                                AND `stocks`.`monthlydata`.`date` <= DATE(%(edate)s)
                               INNER JOIN stocks.`monthly-study-data` USE INDEX (`ids`)
                                ON
                                stocks.stock.`id` = stocks.`monthly-study-data`.`stock-id`
                                AND stocks.`monthly-study-data`.`data-id` = stocks.`monthlydata`.`data-id`
                                AND stocks.`monthly-study-data`.`study-id` = %(id)s 
                                ORDER BY stocks.`monthlydata`.`date` ASC
                                """
                    elif '1y' in interval:
                        check_cache_studies_db_stmt = """SELECT `stocks`.`yearlydata`.`date`,
                            `stocks`.`yearly-study-data`.`val1` 
                             FROM stocks.`yearlydata` USE INDEX (`id-and-date`)
                              INNER JOIN stocks.stock USE INDEX(`stockid`)
                            ON `stock-id` = stocks.stock.`id` 
                              AND stocks.stock.`stock` = %(stock)s
                                AND `stocks`.`yearlydata`.`date` >= DATE(%(bdate)s)
                                AND `stocks`.`yearlydata`.`date` <= DATE(%(edate)s)
                               INNER JOIN stocks.`yearly-study-data` USE INDEX (`ids`)
                                ON
                                stocks.stock.`id` = stocks.`yearly-study-data`.`stock-id`
                                AND stocks.`yearly-study-data`.`data-id` = stocks.`yearlydata`.`data-id`
                                AND stocks.`yearly-study-data`.`study-id` = %(id)s 
                                ORDER BY stocks.`yearlydata`.`date` ASC
                                """
                    else:
                        is_utilizing_yfinance = True
                        check_cache_studies_db_stmt = f"""SELECT `stocks`.`{interval}data`.`date`,
                            `stocks`.`{interval}-study-data`.`val1` 
                             FROM stocks.`{interval}data` USE INDEX (`id-and-date`)
                              INNER JOIN stocks.stock USE INDEX(`stockid`)
                            ON `stock-id` = stocks.stock.`id` 
                              AND stocks.stock.`stock` = %(stock)s
                                AND `stocks`.`{interval}data`.`date` >= %(bdate)s
                                AND `stocks`.`{interval}data`.`date` <= %(edate)s
                               INNER JOIN stocks.`{interval}-study-data` USE INDEX (`ids`)
                                ON
                                stocks.stock.`id` = stocks.`{interval}-study-data`.`stock-id`
                                AND stocks.`{interval}-study-data`.`data-id` = stocks.`{interval}data`.`data-id`
                                AND stocks.`{interval}-study-data`.`study-id` = %(id)s 
                                ORDER BY stocks.`{interval}data`.`date` ASC
                                """
                    try:
                        check_cache_studies_db_result = self.ema_cnx.execute(check_cache_studies_db_stmt,
                                                                             {'stock': self.indicator.upper(),
                                                                              'bdate': self.data["Date"].iloc[
                                                                                  0].strftime('%Y-%m-%d') if isinstance(
                                                                                  self.data["Date"].iloc[0],
                                                                                  datetime.datetime) else
                                                                              self.data["Date"].iloc[0],
                                                                              'edate': self.data["Date"].iloc[
                                                                                  -1].strftime(
                                                                                  '%Y-%m-%d') if isinstance(
                                                                                  self.data["Date"].iloc[-1],
                                                                                  datetime.datetime) else
                                                                              self.data["Date"].iloc[-1],
                                                                              'id': self.study_id}, multi=True)
                        # Retrieve date, verify it is in date range, remove from date range
                        for res in check_cache_studies_db_result:
                            res = res.fetchall()
                            # Convert datetime to str
                            for r in res:
                                try:
                                    date = datetime.date.strftime(r[0], "%Y-%m-%d")
                                except Exception as e:
                                    print(f'[ERROR] No date found for study element!\n{str(e)}')
                                    continue
                                if date is None:
                                    print(
                                        f'[INFO] Not enough prior ema{length} found for {self.indicator.upper()} from {self.data["Date"].iloc[0]} to {self.data["Date"].iloc[-1]}... Generating ema{length} data...!\n',
                                        flush=True)
                                    break
                                else:
                                    # check if date is there, if not fail this
                                    study_data = study_data.append({f'ema{length}': r[1]},
                                                                   ignore_index=True)
                                    if date in date_range:
                                        date_range.remove(date)
                                    else:
                                        # print(f'[INFO] Skipping date removal for {date}')
                                        continue
                    except mysql.connector.errors.IntegrityError:  # should not happen
                        self.ema_cnx.close()
                        pass
                    except Exception as e:
                        print('[ERROR] Failed to check for cached ema-data element!\n', str(e))
                        self.ema_cnx.close()
                        raise mysql.connector.errors.DatabaseError()
            if len(date_range) == 0 and not self._force_generate and not skip_db:  # continue loop if found cached data
                self.applied_studies = pd.concat([self.applied_studies, study_data], axis=1)
            # Insert data into db if query above is not met
            else:
                # if not self._force_generate:
                # print(f'[INFO] Did not query all specified dates within range for ema!  Remaining {date_range}')

                # Calculate locally, then push to database
                with threading.Lock():
                    try:
                        data = self.data.copy().drop(['Date'], axis=1)
                    except:
                        pass
                    data = data.drop(['Open', 'High', 'Low'], axis=1)
                    try:
                        data = data.drop(['Adj Close'], axis=1)
                    except:
                        pass
                    data = data.rename(columns={'Close': f'ema{length}'}).ewm(alpha=2 / (int(length) + 1),
                                                                              adjust=True).mean()
                    self.applied_studies = pd.concat([self.applied_studies, data], axis=1)
                    del data
                    gc.collect()
                if not skip_db:
                    try:
                        self.ema_cnx.close()
                    except:
                        pass
                    # Calculate and store data to DB ...   
                    try:  # Try connection to db_con, if not, connect to
                        self.ema_cnx = self.db_con.cursor()
                    except:
                        self.ema_cnx = self.db_con2.cursor()
                    self.ema_cnx.autocommit = True
                    # Retrieve the stock-id, and data-point id in a single select statement
                    if '1d' in interval:
                        retrieve_data_stmt = """SELECT `stocks`.`dailydata`.`data-id`,
                         `stocks`.`dailydata`.`stock-id` FROM `stocks`.`dailydata` USE INDEX (`id-and-date`)
                        INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`dailydata`.`stock-id`
                         AND `stocks`.`dailydata`.`date`>= DATE(%(bdate)s) 
                         AND `stocks`.`dailydata`.`date`<= DATE(%(edate)s)
                         ORDER BY stocks.`dailydata`.`date` ASC 
                         """
                    elif '1wk' in interval:
                        retrieve_data_stmt = """SELECT `stocks`.`weeklydata`.`data-id`,
                             `stocks`.`weeklydata`.`stock-id` FROM `stocks`.`weeklydata` USE INDEX (`id-and-date`)
                            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`weeklydata`.`stock-id`
                             AND `stocks`.`weeklydata`.`date`>= DATE(%(bdate)s) 
                             AND `stocks`.`weeklydata`.`date`<= DATE(%(edate)s)
                             ORDER BY stocks.`weeklydata`.`date` ASC 
                             """
                    elif '1m' in interval:
                        retrieve_data_stmt = """SELECT `stocks`.`monthlydata`.`data-id`,
                         `stocks`.`monthlydata`.`stock-id` FROM `stocks`.`monthlydata` USE INDEX (`id-and-date`)
                        INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`monthlydata`.`stock-id`
                         AND `stocks`.`monthlydata`.`date`>= DATE(%(bdate)s) 
                         AND `stocks`.`monthlydata`.`date`<= DATE(%(edate)s)
                         ORDER BY stocks.`monthlydata`.`date` ASC 
                         """
                    elif '1y' in interval:
                        retrieve_data_stmt = """SELECT `stocks`.`yearlydata`.`data-id`,
                             `stocks`.`yearlydata`.`stock-id` FROM `stocks`.`yearlydata` USE INDEX (`id-and-date`)
                            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`yearlydata`.`stock-id`
                             AND `stocks`.`yearlydata`.`date`>= DATE(%(bdate)s) 
                             AND `stocks`.`yearlydata`.`date`<= DATE(%(edate)s)
                             ORDER BY stocks.`yearlydata`.`date` ASC 
                             """
                    else:
                        val1 = self.data["Date"].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
                        val2 = self.data["Date"].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
                        retrieve_data_stmt = f"""SELECT `stocks`.`{interval}data`.`data-id`,
                             `stocks`.`{interval}data`.`stock-id`, `stocks`.`{interval}data`.`date` FROM `stocks`.`{interval}data` USE INDEX (`id-and-date`)
                            INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`{interval}data`.`stock-id`
                             AND `stocks`.`{interval}data`.`date` >= '{str(val1)}'
                             ORDER BY `stocks`.`{interval}data`.`date` ASC 
                             """
                    if is_utilizing_yfinance:
                        retrieve_data_stmt = retrieve_data_stmt.replace('\'\'','\'')
                        retrieve_data_result = self.ema_cnx.execute(retrieve_data_stmt,
                                                                {'stock': f'{self.indicator.upper()}',
                                                                 'bdate': self.data["Date"].iloc[0].strftime(
                                                                     '%Y-%m-%d %H:%M:%S').translate("'") if isinstance(
                                                                     self.data["Date"].iloc[0], datetime.datetime) else
                                                                 self.data["Date"].iloc[0],
                                                                 'edate': self.data["Date"].iloc[-1].strftime(
                                                                     '%Y-%m-%d %H:%M:%S').translate("'") if isinstance(
                                                                     self.data["Date"].iloc[-1], datetime.datetime) else
                                                                 self.data["Date"].iloc[-1]}, multi=True)
                        # Since we couldn't query a single range, we need to another another query to get the range
                        self.data_ids = []
                        self.stock_ids = []

                        stock_id = ''
                        data_id = ''

                        for retrieve_result in retrieve_data_result:
                            id_res = retrieve_result.fetchall()
                            for res in id_res:
                                if len(res) == 0:
                                    print(f'[ERROR] Failed to locate a data id under {retrieve_data_result}')
                                    raise Exception()
                                else:
                                    try:
                                        # compare dates to ensure it is in a range
                                        if pytz.UTC.localize(res[2]) <= self.data["Date"].iloc[-1]:
                                            stock_id = res[1].decode('latin1')
                                            data_id = res[0].decode('latin1')
                                            self.stock_ids.append(res[1].decode('latin1'))
                                            self.data_ids.append(res[0].decode('latin1'))
                                        else:
                                            break
                                    except Exception as e:
                                        print(f'[ERROR] failed to query stock id/data_id for ema insert!\n{str(e)}')
                        # Add one more, as there is a bug where the lengths don't match data, causing failure
                        self.stock_ids.append(stock_id)
                        self.data_ids.append(data_id)

                    else:
                        retrieve_data_result = self.ema_cnx.execute(retrieve_data_stmt,
                                                                {'stock': f'{self.indicator.upper()}',
                                                                 'bdate': self.data["Date"].iloc[0].strftime(
                                                                     '%Y-%m-%d') if isinstance(
                                                                     self.data["Date"].iloc[0], datetime.datetime) else
                                                                 self.data["Date"].iloc[0],
                                                                 'edate': self.data["Date"].iloc[-1].strftime(
                                                                     '%Y-%m-%d') if isinstance(
                                                                     self.data["Date"].iloc[-1], datetime.datetime) else
                                                                 self.data["Date"].iloc[-1]}, multi=True)
                        self.data_ids = []
                        self.stock_ids = []
                        stock_id=''
                        data_id=''
                        for retrieve_result in retrieve_data_result:
                            id_res = retrieve_result.fetchall()
                            for res in id_res:
                                if len(res) == 0:
                                    print(f'[ERROR] Failed to locate a data id under {retrieve_data_result}')
                                    raise Exception()
                                else:
                                    try:
                                        stock_id=res[1].decode('latin1')
                                        data_id=res[0].decode('latin1')
                                        self.stock_ids.append(res[1].decode('latin1'))
                                        self.data_ids.append(res[0].decode('latin1'))
                                    except Exception as e:
                                        print(f'[ERROR] failed to query stock id/data_id for ema insert!\n{str(e)}')
                        # Add one more, as there is a bug where the lengths don't match data, causing failure
                        self.stock_ids.append(stock_id)
                        self.data_ids.append(data_id)
                    # Execute insert for study-data
                    if '1d' in interval:
                        insert_studies_db_stmt = "REPLACE INTO `stocks`.`daily-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"
                    elif '1wk' in interval:
                        insert_studies_db_stmt = "REPLACE INTO `stocks`.`weekly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"
                    elif '1m' in interval:
                        insert_studies_db_stmt = "REPLACE INTO `stocks`.`monthly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"
                    elif '1y' in interval:
                        insert_studies_db_stmt = "REPLACE INTO `stocks`.`yearly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"
                    else:
                        insert_studies_db_stmt = f"REPLACE INTO `stocks`.`{interval}-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"

                    insert_list = []
                    for index, id in self.data.iterrows():
                        emastr = f'ema{length}'
                        if is_utilizing_yfinance:
                            insert_tuple = (
                                f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator.upper()}{length}",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator.upper()}{length}",512)))',
                                f'{self.stock_ids[index]}',
                                f'{self.data_ids[index]}',
                                f'{self.study_id}',
                                self.applied_studies[emastr].iloc[index])
                        else:
                            insert_tuple = (
                                f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}{length}",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}{length}",512)))',
                                f'{self.stock_ids[index]}',
                                f'{self.data_ids[index]}',
                                f'{self.study_id}',
                                self.applied_studies[emastr].iloc[index])
                        insert_list.append(insert_tuple)  # add tuple to list
                    # Call execution statement to insert data in one shot
                    try:
                        # print(insert_studies_db_stmt)
                        insert_studies_db_result = self.ema_cnx.executemany(insert_studies_db_stmt, insert_list)
                        self.db_con.commit()
                    except mysql.connector.errors.IntegrityError:
                        print('[ERROR] Integrity Error')
                        self.ema_cnx.close()
                        pass
                    except TypeError as e:
                        print(f'[ERROR] TypeError!\n{str(e)}')
                    except ValueError as e:
                        print(f'[ERROR] ValueError!\n{str(e)}')
                    except Exception as e:
                        print('[ERROR] Failed to insert ema-data element!\n', str(e))
                        self.ema_cnx.close()
                        pass
        self.ema_cnx.close()
        return 0

    '''
        val1 first low/high
        val2 second low/high
        val3 third low/high to predict levels
    '''

    def fib_help(self, val1, val2, val3, fib_val):
        if val1 < val2:  # means val 3 is higher low -- upwards
            return val3 + ((val2 - val1) * fib_val)
        else:  # val 3 is a lower high -- downwards
            return val3 - ((val2 - val1) * -fib_val)

    def upwards_fib(self, new_set, interval):
        try:
            # After this, iterate new list and find which direction stock may go
            val1 = None
            val2 = None
            val3 = None
            new_set = new_set.iloc[0 if '1d' in interval else\
                                    8 if '1wk' in interval else\
                                    0 if '1mo' in interval else\
                                    15 if interval =='5m' else\
                                    0 if '15m' in interval else\
                                    0 if '30m' in interval else\
                                    0 if '60m' in interval else 0:]
            try:
                new_set = new_set.drop(columns=['index'])
            except:
                pass
            new_set = new_set.reset_index()
            if '1d' in interval:
                max_cutoff = 6
            elif '1wk' in interval:
                max_cutoff = 7
            elif '1mo' in interval:
                max_cutoff = 8
            elif interval == '5m':
                max_cutoff = 20
            elif '15m' in interval:
                max_cutoff = 20
            elif '30m' in interval:
                max_cutoff = 10
            elif '60m' in interval:
                max_cutoff = 6
            else:
                max_cutoff = 5
            if len(new_set) == 0:
                print(f'[ERROR] new_set is empty for upwards_fib-{self.indicator}!')
                return val1, val2, val3
            for i, row in new_set.iterrows():  # reverse order iteration
                if i == len(new_set) -1:
                    break
                # if the next value is greater than prior , do upwards fib, else downwards
                if new_set['Low'].idxmin() < len(new_set) - max_cutoff or new_set['Low'].iloc[i+1] > row['Low']:
                    val3 = new_set['Low'].min() if new_set['Low'].idxmin() < len(new_set) - max_cutoff else row['Low']

                    if new_set['Low'].idxmin() != len(new_set) - max_cutoff:
                        i = new_set['Low'].idxmin()

                    # find val2 by finding next local high
                    for j, sub in new_set.iterrows():
                        if j <= i:
                            continue
                        if j == len(new_set) - 1:
                            break
                        # find val2 by making sure next local high is valid
                        if float(new_set['High'].iloc[j + 1]) <= sub['High'] or (new_set['High'].idxmax() < len(new_set) - max_cutoff and (new_set['High'].idxmax() > new_set['Low'].idxmin() and new_set['High'].idxmax() > i)):
                            val2 = sub['High'] if float(new_set['High'].iloc[j + 1]) <= sub['High'] else new_set['High'].max()

                            if new_set['High'].idxmax() < len(new_set) - max_cutoff:
                                if i == new_set['Low'].idxmin() and new_set['High'].idxmax() > new_set['Low'].idxmin():
                                    j = new_set['High'].idxmax()
                                elif new_set['High'].idxmax() > i:
                                    j = new_set['High'].idxmax()
                            # find val3 by getting next low
                            if new_set['Low'].min() != val3:
                                val1 = new_set['Low'].min()
                            else:
                                for k, low in new_set.iterrows():
                                    if k <= j:
                                        continue
                                    else:
                                        if float(new_set['Low'].iloc[k + 1]) >= low['Low'] <= float(
                                                new_set['Low'].iloc[k - 1]):
                                            val1 = low['Low']
                                            return val1, val2, val3
                                        else:
                                            continue
                                break
                        else:
                            continue
                    break
                else:
                    return self.upwards_fib(new_set[1:], interval)
            return val1, val2, val3
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def downwards_fib(self, new_set, interval):
        try:
            # After this, iterate new list and find which direction stock may go
            val1 = None
            val2 = None
            val3 = None
            new_set = new_set.iloc[0 if '1d' in interval else\
                                    8 if '1wk' in interval else\
                                    0 if '1mo' in interval else\
                                    15 if interval =='5m' else\
                                    0 if '15m' in interval else\
                                    0 if '30m' in interval else\
                                    0 if '60m' in interval else 0:]
            try:
                new_set = new_set.drop(columns=['index'])
            except:
                pass
            new_set = new_set.reset_index()
            if '1d' in interval:
                max_cutoff = 6
            elif '1wk' in interval:
                max_cutoff = 7
            elif '1mo' in interval:
                max_cutoff = 8
            elif interval == '5m':
                max_cutoff = 20
            elif '15m' in interval:
                max_cutoff = 20
            elif '30m' in interval:
                max_cutoff = 10
            elif '60m' in interval:
                max_cutoff = 6
            else:
                max_cutoff = -5
            if len(new_set) == 0:
                return val1, val2, val3
            for i, row in new_set.iterrows():  # reverse order iteration
                if i == len(new_set) -1:
                    break
                # if the next value is less than prior , do downwards fib, else
                if new_set['High'].idxmax() < len(new_set) - max_cutoff or new_set['High'].iloc[i+1] <= row['High']:
                    val3 = new_set['High'].max() if new_set['High'].idxmax() < len(new_set) - max_cutoff else row['High']
                    if new_set['High'].idxmax() < len(new_set) - max_cutoff:
                        i = new_set['High'].idxmax()
                    # find val2 by finding next local high
                    for j, sub in new_set.iterrows():
                        if j <= i:
                            continue
                        if j == len(new_set) - 1:
                            break
                        # find val2 by making sure next local low is valid
                        if float(new_set['Low'].iloc[j + 1]) >= sub['Low'] or (new_set['Low'].idxmin() <= len(new_set) - max_cutoff and (new_set['Low'].idxmin() > new_set['High'].idxmax() and new_set['Low'].idxmin() > i)):
                            val2 = new_set['Low'].min() if (new_set['Low'].idxmin() <= len(new_set) - max_cutoff) else sub['Low']
                            if new_set['Low'].idxmin() < len(new_set) - max_cutoff:
                                if i == new_set['High'].idxmax() and new_set['Low'].idxmin() > new_set['High'].idxmax():
                                    j = new_set['Low'].idxmin()
                            # find val3 by getting next low
                            if new_set['High'].max() != val3:
                                val1 = new_set['High'].max()
                            else:
                                for k, high in new_set.iterrows():
                                    if k <= j:
                                        continue
                                    else:
                                        if float(new_set['High'].iloc[k + 1]) <= high['High']:
                                            val1 = high['High']
                                            return val1, val2, val3
                                        else:
                                            continue
                                break
                        else:
                            continue
                    break
                else:
                    return self.downwards_fib(new_set[1:], interval)
            return val1, val2, val3
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    def insert_fib_vals(self, skip_db, interval):
        # Insert data if not in db...
        if not skip_db:
            is_utilizing_yfinance = False
            if '1d' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`daily-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                            `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`,`val15`, `val16`,`val17`,`val18`,`val19`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
            elif '1wk' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`weekly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                                `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`,`val15`, `val16`,`val17`,`val18`,`val19`) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
            elif '1wk' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`monthly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                            `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`,`val15`, `val16`,`val17`,`val18`,`val19`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
            elif '1y' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`yearly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                            `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`,`val15`,`val16`,`val17`,`val18`,`val19`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
            else:
                is_utilizing_yfinance = True
                insert_studies_db_stmt = f"""REPLACE INTO `stocks`.`{interval}-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                            `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`,`val15`, `val16`,`val17`,`val18`,`val19`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """

            insert_list = []
            self.fibonacci_extension = self.fibonacci_extension.reset_index().astype(float)
            for index, row in self.data.iterrows():
                if is_utilizing_yfinance:
                    insert_tuple = (
                        f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator.upper()}fibonacci",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator.upper()}fibonacci",512)))',
                        f'{self.stock_ids[index]}',
                        f'{self.data_ids[index]}',
                        f'{self.study_id}',
                        self.fibonacci_extension.at[0, "0.202"],
                        self.fibonacci_extension.at[0, "0.236"],
                        self.fibonacci_extension.at[0, "0.241"],
                        self.fibonacci_extension.at[0, "0.273"],
                        self.fibonacci_extension.at[0, "0.283"],
                        self.fibonacci_extension.at[0, "0.316"],
                        self.fibonacci_extension.at[0, "0.382"],
                        self.fibonacci_extension.at[0, "0.5"],
                        self.fibonacci_extension.at[0, "0.618"],
                        self.fibonacci_extension.at[0, "0.796"],
                        self.fibonacci_extension.at[0, "1.556"],
                        self.fibonacci_extension.at[0, "2.493"],
                        self.fibonacci_extension.at[0, "2.86"],
                        self.fibonacci_extension.at[0, "3.43"],
                        self.fibonacci_extension.at[0, "3.83"],
                        self.fibonacci_extension.at[0, "5.44"],
                        self.fibonacci_extension.at[0, "8.23"],
                        self.fibonacci_extension.at[0, "9.55"],
                        self.fibonacci_extension.at[0, "11.13"],
                    )

                else:
                    insert_tuple = (
                        f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}fibonacci",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}fibonacci",512)))',
                        f'{self.stock_ids[index]}',
                        f'{self.data_ids[index]}',
                        f'{self.study_id}',
                        self.fibonacci_extension.at[0, "0.202"],
                        self.fibonacci_extension.at[0, "0.236"],
                        self.fibonacci_extension.at[0, "0.241"],
                        self.fibonacci_extension.at[0, "0.273"],
                        self.fibonacci_extension.at[0, "0.283"],
                        self.fibonacci_extension.at[0, "0.316"],
                        self.fibonacci_extension.at[0, "0.382"],
                        self.fibonacci_extension.at[0, "0.5"],
                        self.fibonacci_extension.at[0, "0.618"],
                        self.fibonacci_extension.at[0, "0.796"],
                        self.fibonacci_extension.at[0, "1.556"],
                        self.fibonacci_extension.at[0, "2.493"],
                        self.fibonacci_extension.at[0, "2.86"],
                        self.fibonacci_extension.at[0, "3.43"],
                        self.fibonacci_extension.at[0, "3.83"],
                        self.fibonacci_extension.at[0, "5.44"],
                        self.fibonacci_extension.at[0, "8.23"],
                        self.fibonacci_extension.at[0, "9.55"],
                        self.fibonacci_extension.at[0, "11.13"],
                    )
                insert_list.append(insert_tuple)  # add tuple to list
                # duplicate row by 1
                self.fibonacci_extension = self.fibonacci_extension.append([self.fibonacci_extension.iloc[0]] * 1,
                                                                           ignore_index=True)

            try:
                insert_studies_db_result = self.fib_cnx.executemany(insert_studies_db_stmt, insert_list)
            except mysql.connector.errors.IntegrityError:
                self.fib_cnx.close()
                pass
            except Exception as e:
                print('[ERROR] Failed to insert study-data element fibonacci!\n', str(e))
                self.fib_cnx.close()
                pass
            try:
                self.db_con.commit()
            except mysql.connector.errors.IntegrityError:
                print('Integrity Error!')
                self.fib_cnx.close()
                pass
            except Exception as e:
                print('[ERROR] Failed to insert fib-data element fibonacci!\n', str(e))
                self.fib_cnx.close()
                pass
        else:
            for index, row in self.data.iterrows():
                self.fibonacci_extension = self.fibonacci_extension.append([self.fibonacci_extension.iloc[0]] * 1,
                                                                           ignore_index=True)

        '''
        Fibonacci extensions utilized for predicting key breaking points
        val2 ------------------------                 val3
       ||                                    val1   /  \
      / \   ---------------------           / \    /    \ 
     /  \  /----------------------- or     /  \   /      \
    /   \ /                               /    \ /        \
val1    val3_________________________          vall2
        '''

    async def apply_fibonacci(self, skip_db=False, interval='1d'):
        date_range = [d.strftime('%Y-%m-%d') for d in
                      pd.date_range(self.data.iloc[0]['Date'], self.data.iloc[-1]['Date'])]  # start/end date list
        self.fib_cnx = self.db_con.cursor()
        self.fib_cnx.autocommit = True

        if not skip_db:

            """
                    MYSQL PORTION... 
                    Check DB before doing calculations
            """

            # Retrieve query from database, confirm that stock is in database, else make new query
            select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
            # print('[INFO] Select stock')
            resultado = self.fib_cnx.execute(select_stmt, {'stock': self.indicator.upper()}, multi=True)
            for result in resultado:
                # Query new stock, id
                if len(result.fetchall()) == 0:
                    print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                    raise mysql.connector.Error
                else:
                    select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                    # print('[INFO] Select study id')
                    study_result = self.fib_cnx.execute(select_study_stmt, {'study': f'fibonacci'}, multi=True)
                    for s_res in study_result:
                        # Non existent DB value
                        study_id_res = s_res.fetchall()
                        if len(study_id_res) == 0:
                            print(
                                f'[INFO] Failed to query study named fibonacci from database! Creating new Study...\n')
                            insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                                VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(fib)s)"""
                            # Insert new study into DB
                            try:
                                insert_result = self.fib_cnx.execute(insert_study_stmt, {'id': f'fibonacci',
                                                                                         'fib': f'fibonacci'},
                                                                     multi=True)
                                self.db_con.commit()

                                # Now get the id from the db
                                retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                                retrieve_study_id_result = self.fib_cnx.execute(retrieve_study_id_stmt,
                                                                                {'study': f'fibonacci'}, multi=True)
                                for r in retrieve_study_id_result:
                                    id_result = r.fetchall()
                                    self.study_id = id_result[0][0].decode('latin1')
                            except mysql.connector.errors.IntegrityError:
                                pass
                            except Exception as e:
                                print(f'[ERROR] Failed to Insert study into stocks.study named fibonacci!\n', str(e))
                                raise mysql.connector.Error
                        else:
                            # Get study_id
                            self.study_id = study_id_res[0][0].decode('latin1')

            # Now, Start the process for inserting fib data...
            holidays = USFederalHolidayCalendar().holidays(start=f'{datetime.datetime.now().year}-01-01',
                                                           end=f'{datetime.datetime.now().year}-12-31').to_pydatetime()
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
            fib_data = pd.DataFrame(
                columns=['0.202', '0.236', '0.241', '0.273', '0.283', '0.316', '0.382', '0.5', '0.618', '0.796',
                         '1.556', '2.493', '2.86', '3.43', '3.83', '5.44', '8.23','9.55','11.13'])
            try:
                self.fib_cnx.close()
            except:
                pass
            self.fib_cnx = self.db_con.cursor()
            self.fib_cnx.autocommit = True
            retrieve_data_stmt=''
            is_utilizing_yfinance = False
            # Retrieve the stock-id, and data-point id in a single select statement
            if '1d' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`dailydata`.`data-id`,
                 `stocks`.`dailydata`.`stock-id` FROM `stocks`.`dailydata` USE INDEX (`id-and-date`)
                INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`dailydata`.`stock-id`
                 AND `stocks`.`dailydata`.`date`>= DATE(%(bdate)s) 
                 AND `stocks`.`dailydata`.`date`<= DATE(%(edate)s)
                 ORDER BY stocks.`dailydata`.`date` ASC 
                 """
            elif '1wk' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`weeklydata`.`data-id`,
                     `stocks`.`weeklydata`.`stock-id` FROM `stocks`.`weeklydata` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`weeklydata`.`stock-id`
                     AND `stocks`.`weeklydata`.`date`>= DATE(%(bdate)s) 
                     AND `stocks`.`weeklydata`.`date`<= DATE(%(edate)s)
                     ORDER BY stocks.`weeklydata`.`date` ASC 
                     """
            elif '1m' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`monthlydata`.`data-id`,
                 `stocks`.`monthlydata`.`stock-id` FROM `stocks`.`monthlydata` USE INDEX (`id-and-date`)
                INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`monthlydata`.`stock-id`
                 AND `stocks`.`monthlydata`.`date`>= DATE(%(bdate)s) 
                 AND `stocks`.`monthlydata`.`date`<= DATE(%(edate)s)
                 ORDER BY stocks.`monthlydata`.`date` ASC 
                 """
            elif '1y' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`yearlydata`.`data-id`,
                     `stocks`.`yearlydata`.`stock-id` FROM `stocks`.`yearlydata` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`yearlydata`.`stock-id`
                     AND `stocks`.`yearlydata`.`date`>= DATE(%(bdate)s) 
                     AND `stocks`.`yearlydata`.`date`<= DATE(%(edate)s)
                     ORDER BY stocks.`yearlydata`.`date` ASC 
                     """
            else:
                is_utilizing_yfinance = True
                val1 = self.data["Date"].iloc[0].strftime('%Y-%m-%d %H:%M:%S')
                val2 = self.data["Date"].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
                retrieve_data_stmt = f"""SELECT `stocks`.`{interval}data`.`data-id`,
                     `stocks`.`{interval}data`.`stock-id`, `stocks`.`{interval}data`.`date` FROM `stocks`.`{interval}data` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`{interval}data`.`stock-id`
                     AND `stocks`.`{interval}data`.`date`>= '{val1}'
                     ORDER BY stocks.`{interval}data`.`date` ASC 
                     """
            if is_utilizing_yfinance:
                retrieve_data_result = self.fib_cnx.execute(retrieve_data_stmt, {'stock': f'{self.indicator.upper()}',
                                                                                 'bdate': self.data["Date"].iloc[
                                                                                     0].strftime(
                                                                                     '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                                     self.data["Date"].iloc[0],
                                                                                     datetime.datetime) else
                                                                                 self.data["Date"].iloc[0],
                                                                                 'edate': self.data["Date"].iloc[
                                                                                     -1].strftime(
                                                                                     '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                                     self.data["Date"].iloc[-1],
                                                                                     datetime.datetime) else
                                                                                 self.data["Date"].iloc[-1]},
                                                            multi=True)
                self.stock_ids = []
                self.data_ids = []
                # self.data=self.data.drop(['Date'],axis=1)
                for retrieve_result in retrieve_data_result:
                    id_res = retrieve_result.fetchall()
                    if len(id_res) == 0:
                        print(
                            f'[INFO] Failed to locate any data-ids/stock-ids from {self.data["Date"].iloc[0].strftime("%Y-%m-%d")} to {self.data["Date"].iloc[-1].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                        break
                    else:
                        for res in id_res:
                            try:
                                if pytz.UTC.localize(res[2]) <= self.data["Date"].iloc[-1]:
                                    self.stock_ids.append(res[1].decode('latin1'))
                                    self.data_ids.append(res[0].decode('latin1'))
                                else:
                                    break
                            except Exception as e:
                                print(
                                    f'[ERROR] Failed to grab stock id/data id for {self.indicator} for fib retrieval!\n{str(e)}')
                                break
            else:
                retrieve_data_result = self.fib_cnx.execute(retrieve_data_stmt, {'stock': f'{self.indicator.upper()}',
                                                                                 'bdate': self.data["Date"].iloc[
                                                                                     0].strftime('%Y-%m-%d') if isinstance(
                                                                                     self.data["Date"].iloc[0],
                                                                                     datetime.datetime) else
                                                                                 self.data["Date"].iloc[0],
                                                                                 'edate': self.data["Date"].iloc[
                                                                                     -1].strftime('%Y-%m-%d') if isinstance(
                                                                                     self.data["Date"].iloc[-1],
                                                                                     datetime.datetime) else
                                                                                 self.data["Date"].iloc[-1]},
                                                            multi=True)
                self.stock_ids = []
                self.data_ids = []
                # self.data=self.data.drop(['Date'],axis=1)
                for retrieve_result in retrieve_data_result:
                    id_res = retrieve_result.fetchall()
                    if len(id_res) == 0:
                        print(
                            f'[INFO] Failed to locate any data-ids/stock-ids from {self.data["Date"].iloc[0].strftime("%Y-%m-%d")} to {self.data["Date"].iloc[-1].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                        break
                    else:
                        for res in id_res:
                            try:
                                self.stock_ids.append(res[1].decode('latin1'))
                                self.data_ids.append(res[0].decode('latin1'))
                            except Exception as e:
                                print(
                                    f'[ERROR] Failed to grab stock id/data id for {self.indicator} for fib retrieval!\n{str(e)}')
                                break

            # Before inserting data, check cached data, verify if there is data there...
            if '1d' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`dailydata`.`date`,
                `stocks`.`daily-study-data`.`val1`,`stocks`.`daily-study-data`.`val2`,
                `stocks`.`daily-study-data`.`val3`,`stocks`.`daily-study-data`.`val4`,
                `stocks`.`daily-study-data`.`val5`,`stocks`.`daily-study-data`.`val6`,
                `stocks`.`daily-study-data`.`val7`,`stocks`.`daily-study-data`.`val8`,
                `stocks`.`daily-study-data`.`val9`,`stocks`.`daily-study-data`.`val10`,
                `stocks`.`daily-study-data`.`val11`,`stocks`.`daily-study-data`.`val12`,
                `stocks`.`daily-study-data`.`val13`,`stocks`.`daily-study-data`.`val14`,
                `stocks`.`daily-study-data`.`val15`,
                `stocks`.`daily-study-data`.`val16`,`stocks`.`daily-study-data`.`val17`,
                `stocks`.`daily-study-data`.`val18`,`stocks`.`daily-study-data`.`val19` 
                 FROM stocks.`dailydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                ON `stocks`.`dailydata`.`stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`dailydata`.`date` >= DATE(%(bdate)s)
                   AND `stocks`.`dailydata`.`date` <= DATE(%(edate)s)
                   INNER JOIN stocks.`daily-study-data` USE INDEX (`ids`) ON
                    stocks.stock.`id` = stocks.`daily-study-data`.`stock-id`
                    AND stocks.`daily-study-data`.`data-id` = stocks.`dailydata`.`data-id`
                    AND stocks.`daily-study-data`.`study-id` = %(id)s ORDER BY stocks.`dailydata`.`date` ASC
                    """
            elif '1wk' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`weeklydata`.`date`,
                `stocks`.`weekly-study-data`.`val1`,`stocks`.`weekly-study-data`.`val2`,
                `stocks`.`weekly-study-data`.`val3`,`stocks`.`weekly-study-data`.`val4`,
                `stocks`.`weekly-study-data`.`val5`,`stocks`.`weekly-study-data`.`val6`,
                `stocks`.`weekly-study-data`.`val7`,`stocks`.`weekly-study-data`.`val8`,
                `stocks`.`weekly-study-data`.`val9`,`stocks`.`weekly-study-data`.`val10`,
                `stocks`.`weekly-study-data`.`val11`,`stocks`.`weekly-study-data`.`val12`,
                `stocks`.`weekly-study-data`.`val13`,`stocks`.`weekly-study-data`.`val14`,
                `stocks`.`weekly-study-data`.`val15`,`stocks`.`weekly-study-data`.`val16`,
                `stocks`.`weekly-study-data`.`val17`,
                `stocks`.`weekly-study-data`.`val18`,`stocks`.`weekly-study-data`.`val19`
                 FROM stocks.`weeklydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                ON `stocks`.`weeklydata`.`stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`weeklydata`.`date` >= DATE(%(bdate)s)
                   AND `stocks`.`weeklydata`.`date` <= DATE(%(edate)s)
                   INNER JOIN stocks.`weekly-study-data` USE INDEX (`ids`) ON
                    stocks.stock.`id` = stocks.`weekly-study-data`.`stock-id`
                    AND stocks.`weekly-study-data`.`data-id` = stocks.`weeklydata`.`data-id`
                    AND stocks.`weekly-study-data`.`study-id` = %(id)s ORDER BY stocks.`weeklydata`.`date` ASC
                    """
            elif '1m' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`monthlydata`.`date`,
                `stocks`.`monthly-study-data`.`val1`,`stocks`.`monthly-study-data`.`val2`,
                `stocks`.`monthly-study-data`.`val3`,`stocks`.`monthly-study-data`.`val4`,
                `stocks`.`monthly-study-data`.`val5`,`stocks`.`monthly-study-data`.`val6`,
                `stocks`.`monthly-study-data`.`val7`,`stocks`.`monthly-study-data`.`val8`,
                `stocks`.`monthly-study-data`.`val9`,`stocks`.`monthly-study-data`.`val10`,
                `stocks`.`monthly-study-data`.`val11`,`stocks`.`monthly-study-data`.`val12`,
                `stocks`.`monthly-study-data`.`val13`,`stocks`.`monthly-study-data`.`val14`,
                `stocks`.`monthly-study-data`.`val15`,`stocks`.`monthly-study-data`.`val16`,
                `stocks`.`monthly-study-data`.`val15`,`stocks`.`monthly-study-data`.`val16`,
                `stocks`.`monthly-study-data`.`val17`,
                `stocks`.`monthly-study-data`.`val18`,`stocks`.`monthly-study-data`.`val19`

                 FROM stocks.`monthlydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                ON `stocks`.`monthlydata`.`stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`monthlydata`.`date` >= DATE(%(bdate)s)
                   AND `stocks`.`monthlydata`.`date` <= DATE(%(edate)s)
                   INNER JOIN stocks.`monthly-study-data` USE INDEX (`ids`) ON
                    stocks.stock.`id` = stocks.`monthly-study-data`.`stock-id`
                    AND stocks.`monthly-study-data`.`data-id` = stocks.`monthlydata`.`data-id`
                    AND stocks.`monthly-study-data`.`study-id` = %(id)s ORDER BY stocks.`monthlydata`.`date` ASC
                    """
            elif '1y' in interval:
                check_cache_studies_db_stmt = """SELECT `stocks`.`yearlydata`.`date`,
                `stocks`.`yearly-study-data`.`val1`,`stocks`.`yearly-study-data`.`val2`,
                `stocks`.`yearly-study-data`.`val3`,`stocks`.`yearly-study-data`.`val4`,
                `stocks`.`yearly-study-data`.`val5`,`stocks`.`yearly-study-data`.`val6`,
                `stocks`.`yearly-study-data`.`val7`,`stocks`.`yearly-study-data`.`val8`,
                `stocks`.`yearly-study-data`.`val9`,`stocks`.`yearly-study-data`.`val10`,
                `stocks`.`yearly-study-data`.`val11`,`stocks`.`yearly-study-data`.`val12`,
                `stocks`.`yearly-study-data`.`val13`,`stocks`.`yearly-study-data`.`val14`,
                `stocks`.`yearly-study-data`.`val15`,`stocks`.`yearly-study-data`.`val16`,
                `stocks`.`yearly-study-data`.`val17`,
                `stocks`.`yearly-study-data`.`val18`,`stocks`.`yearly-study-data`.`val19`
                 FROM stocks.`yearlydata` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                ON `stocks`.`yearlydata`.`stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`yearlydata`.`date` >= DATE(%(bdate)s)
                   AND `stocks`.`yearlydata`.`date` <= DATE(%(edate)s)
                   INNER JOIN stocks.`yearly-study-data` USE INDEX (`ids`) ON
                    stocks.stock.`id` = stocks.`yearly-study-data`.`stock-id`
                    AND stocks.`yearly-study-data`.`data-id` = stocks.`yearlydata`.`data-id`
                    AND stocks.`yearly-study-data`.`study-id` = %(id)s ORDER BY stocks.`yearlydata`.`date` ASC
                    """
            else:
                check_cache_studies_db_stmt = f"""SELECT `stocks`.`{interval}data`.`date`,
                `stocks`.`{interval}-study-data`.`val1`,`stocks`.`{interval}-study-data`.`val2`,
                `stocks`.`{interval}-study-data`.`val3`,`stocks`.`{interval}-study-data`.`val4`,
                `stocks`.`{interval}-study-data`.`val5`,`stocks`.`{interval}-study-data`.`val6`,
                `stocks`.`{interval}-study-data`.`val7`,`stocks`.`{interval}-study-data`.`val8`,
                `stocks`.`{interval}-study-data`.`val9`,`stocks`.`{interval}-study-data`.`val10`,
                `stocks`.`{interval}-study-data`.`val11`,`stocks`.`{interval}-study-data`.`val12`,
                `stocks`.`{interval}-study-data`.`val13`,`stocks`.`{interval}-study-data`.`val14`,
                `stocks`.`{interval}-study-data`.`val15`,`stocks`.`{interval}-study-data`.`val16`,
                `stocks`.`{interval}-study-data`.`val17`,
                `stocks`.`{interval}-study-data`.`val18`,`stocks`.`{interval}-study-data`.`val19`
                 FROM stocks.`{interval}data` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
                ON `stocks`.`{interval}data`.`stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                   AND `stocks`.`{interval}data`.`date` >= %(bdate)s
                   AND `stocks`.`{interval}data`.`date` <= %(edate)s
                   INNER JOIN stocks.`{interval}-study-data` USE INDEX (`ids`) ON
                    stocks.stock.`id` = stocks.`{interval}-study-data`.`stock-id`
                    AND stocks.`{interval}-study-data`.`data-id` = stocks.`{interval}data`.`data-id`
                    AND stocks.`{interval}-study-data`.`study-id` = %(id)s ORDER BY stocks.`{interval}data`.`date` ASC
                    """


            try:
                if is_utilizing_yfinance:
                    check_cache_studies_db_result = self.fib_cnx.execute(check_cache_studies_db_stmt,
                                                                         {'stock': self.indicator.upper(),
                                                                          'bdate': self.data["Date"].iloc[0].strftime(
                                                                              '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                              self.data["Date"].iloc[0],
                                                                              datetime.datetime) else
                                                                          self.data["Date"].iloc[0],
                                                                          'edate': self.data["Date"].iloc[-1].strftime(
                                                                              '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                              self.data["Date"].iloc[-1],
                                                                              datetime.datetime) else
                                                                          self.data["Date"].iloc[-1],
                                                                          'id': self.study_id}, multi=True)
                else:
                    check_cache_studies_db_result = self.fib_cnx.execute(check_cache_studies_db_stmt,
                                                                         {'stock': self.indicator.upper(),
                                                                          'bdate': self.data["Date"].iloc[0].strftime(
                                                                              '%Y-%m-%d') if isinstance(
                                                                              self.data["Date"].iloc[0],
                                                                              datetime.datetime) else
                                                                          self.data["Date"].iloc[0],
                                                                          'edate': self.data["Date"].iloc[-1].strftime(
                                                                              '%Y-%m-%d') if isinstance(
                                                                              self.data["Date"].iloc[-1],
                                                                              datetime.datetime) else
                                                                          self.data["Date"].iloc[-1],
                                                                          'id': self.study_id}, multi=True)
                # Retrieve date, verify it is in date range, remove from date range
                for res in check_cache_studies_db_result:
                    # print(str(res.statement))
                    res = res.fetchall()
                    for r in res:
                        # Convert datetime to str
                        try:
                            date = datetime.date.strftime(r[0], "%Y-%m-%d")
                        except Exception as e:
                            print(f'[ERROR] Could not find a date for fib data for {self.indicator.upper()}!\n{str(e)}')
                            continue
                        if date is None:
                            print(
                                f'[INFO] Not enough fib data found for {self.indicator.upper()}... Creating fib data...!\n',
                                flush=True)
                            break
                        else:
                            fib_data = fib_data.append({'0.202': r[1], '0.236': r[2],
                                                        '0.241': r[3], '0.273': r[4],
                                                        '0.283': r[5], '0.316': r[6],
                                                        '0.382': r[7], '0.5': r[8],
                                                        '0.618': r[9], '0.796': r[10],
                                                        '1.556': r[11], '2.493': r[12],
                                                        '2.86': r[13],
                                                        '3.43': r[14],
                                                        '3.83': r[15],
                                                        '5.44': r[16],
                                                        '8.23': r[17],
                                                        '9.55': r[18],
                                                        '11.13': r[19],
                                                        },
                                                       ignore_index=True)
                            # check if date is there, if not fail this
                            if date in date_range:
                                date_range.remove(date)
                            else:
                                continue
            except mysql.connector.errors.IntegrityError:  # should not happen
                self.fib_cnx.close()
                print('[ERROR] Integrity Error!')
                pass
            except Exception as e:
                print('[ERROR] Failed to check for cached fib-data element!\n', str(e))
                self.fib_cnx.close()
                raise mysql.connector.errors.DatabaseError()
        if len(date_range) == 0 and not self._force_generate and not skip_db:  # continue loop if found cached data
            self.fibonacci_extension = fib_data
        else:
            # if not self._force_generate and not skip_db:
            # print(f'[INFO] Did not query all specified dates within range for fibonacci!  Remaining {date_range}')

            """
            Do Calculations, then Insert new data to mysql...
            """
            '''
            Fibonacci values:
            0.236
            0.382
            0.5
            0.618
            0.796
            0.316
            0.202
            0.241
            0.283
            1.556
            2.73
            5.44
            8.23
            9.55
            2.86
            3.83
            3.43
            11.13
            '''
            # Find greatest/least 3 points for pattern

            with threading.Lock():
                # val1=None;val2=None;val3=None
                # iterate through data to find all min and max
                try:
                    # self.data = self.data.set
                    data = self.data.copy()
                    data = data.reset_index()
                    # self.data=self.data.drop(['Date'],axis=1)
                    # print(self.data)
                except Exception as e:
                    pass
                local_max_high = data.iloc[argrelextrema(data.High.values, np.greater_equal,
                                                              order=2)[0]]
                # local_max_high = local_max_high.reset_index()
                local_max_low = data.iloc[argrelextrema(data.Low.values, np.less_equal,
                                                             order=2)[0]]

                # local_max_low = local_max_low.rename({"Low": 'max_low'}, axis='columns')
                # local_max_high = local_max_high.rename({"High": 'max_high'}, axis='columns')

                # After finding min and max values, we can look for local mins and maxes by iterating
                new_set = pd.concat([local_max_high,local_max_low]).sort_values(by=['Date']).drop_duplicates().reset_index()

                new_set['High'] = new_set['High'].astype('float')
                self.data['High'] = self.data['High'].astype('float')
                data['High'] = data['High'].astype('float')
                new_set['Low'] = new_set['Low'].astype('float')
                self.data['Low'] = self.data['Low'].astype('float')
                data['Low'] = data['Low'].astype('float')
                # new_set.columns = ['Index', 'Vals']
                pd.set_option('display.max_columns', None)
                # attempt upwards fib

            if data['High'].iloc[-1] >= new_set['High'].iloc[0]:
                try:
                    val1, val2, val3 = self.upwards_fib(new_set, interval)
                    # calculate values  -- 14 vals
                    self.fibonacci_extension = pd.DataFrame({'0.202': [self.fib_help(val1, val2, val3, 0.202)],
                                                             '0.236': [self.fib_help(val1, val2, val3, 0.236)],
                                                             '0.241': [self.fib_help(val1, val2, val3, 0.241)],
                                                             '0.273': [self.fib_help(val1, val2, val3, 0.273)],
                                                             '0.283': [self.fib_help(val1, val2, val3, 0.283)],
                                                             '0.316': [self.fib_help(val1, val2, val3, 0.316)],
                                                             '0.382': [self.fib_help(val1, val2, val3, 0.382)],
                                                             '0.5': [self.fib_help(val1, val2, val3, 0.5)],
                                                             '0.618': [self.fib_help(val1, val2, val3, 0.618)],
                                                             '0.796': [self.fib_help(val1, val2, val3, 0.796)],
                                                             '1.556': [self.fib_help(val1, val2, val3, 1.556)],
                                                             '2.493': [self.fib_help(val1, val2, val3, 2.493)],
                                                             '2.86': [self.fib_help(val1, val2, val3, 2.86)],
                                                             '3.43': [self.fib_help(val1, val2, val3, 3.43)],
                                                             '3.83': [self.fib_help(val1, val2, val3, 3.83)],
                                                             '5.44': [self.fib_help(val1, val2, val3, 5.44)],
                                                             '8.23': [self.fib_help(val1, val2, val3, 8.23)],
                                                             '9.55': [self.fib_help(val1, val2, val3, 9.55)],
                                                             '11.13': [self.fib_help(val1, val2, val3, 11.13)]
                                                             })
                    self.insert_fib_vals(skip_db=skip_db,interval=interval)  # insert to db
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(fname,exc_type,exc_obj,exc_tb.tb_lineno)
            else:
                try:
                    val1, val2, val3 = self.downwards_fib(new_set, interval)
                    if self.fibonacci_extension.empty:  # If upwards fails, initialize here
                        # calculate values  -- 14 vals
                        self.fibonacci_extension = pd.DataFrame({'0.202': [self.fib_help(val1, val2, val3, 0.202)],
                                                                 '0.236': [self.fib_help(val1, val2, val3, 0.236)],
                                                                 '0.241': [self.fib_help(val1, val2, val3, 0.241)],
                                                                 '0.273': [self.fib_help(val1, val2, val3, 0.273)],
                                                                 '0.283': [self.fib_help(val1, val2, val3, 0.283)],
                                                                 '0.316': [self.fib_help(val1, val2, val3, 0.316)],
                                                                 '0.382': [self.fib_help(val1, val2, val3, 0.382)],
                                                                 '0.5': [self.fib_help(val1, val2, val3, 0.5)],
                                                                 '0.618': [self.fib_help(val1, val2, val3, 0.618)],
                                                                 '0.796': [self.fib_help(val1, val2, val3, 0.796)],
                                                                 '1.556': [self.fib_help(val1, val2, val3, 1.556)],
                                                                 '2.493': [self.fib_help(val1, val2, val3, 2.493)],
                                                                 '2.86': [self.fib_help(val1, val2, val3, 2.86)],
                                                                 '3.43': [self.fib_help(val1, val2, val3, 3.43)],
                                                                 '3.83': [self.fib_help(val1, val2, val3, 3.83)],
                                                                 '5.44': [self.fib_help(val1, val2, val3, 5.44)],
                                                                 '8.23': [self.fib_help(val1, val2, val3, 8.23)],
                                                                 '9.55': [self.fib_help(val1, val2, val3, 9.55)],
                                                                 '11.13': [self.fib_help(val1, val2, val3, 11.13)]
                                                                 })

                        self.insert_fib_vals(skip_db=skip_db,interval=interval)  # insert to db
                    else:  # else, append
                        self.fibonacci_extension = self.fibonacci_extension.append(
                            {'0.202': [self.fib_help(val1, val2, val3, 0.202)],
                             '0.236': [self.fib_help(val1, val2, val3, 0.236)],
                             '0.241': [self.fib_help(val1, val2, val3, 0.241)],
                             '0.273': [self.fib_help(val1, val2, val3, 0.273)],
                             '0.283': [self.fib_help(val1, val2, val3, 0.283)],
                             '0.316': [self.fib_help(val1, val2, val3, 0.316)],
                             '0.382': [self.fib_help(val1, val2, val3, 0.382)],
                             '0.5': [self.fib_help(val1, val2, val3, 0.5)],
                             '0.618': [self.fib_help(val1, val2, val3, 0.618)],
                             '0.796': [self.fib_help(val1, val2, val3, 0.796)],
                             '1.556': [self.fib_help(val1, val2, val3, 1.556)],
                             '2.493': [self.fib_help(val1, val2, val3, 2.493)],
                             '2.86': [self.fib_help(val1, val2, val3, 2.86)],
                             '3.43': [self.fib_help(val1, val2, val3, 3.43)],
                             '3.83': [self.fib_help(val1, val2, val3, 3.83)],
                             '5.44': [self.fib_help(val1, val2, val3, 5.44)],
                             '8.23': [self.fib_help(val1, val2, val3, 8.23)],
                             '9.55': [self.fib_help(val1, val2, val3, 9.55)],
                             '11.13': [self.fib_help(val1, val2, val3, 11.13)]
                             })

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    val1, val2, val3 = self.upwards_fib(new_set, interval)
        try:
            self.fibonacci_extension = self.fibonacci_extension.drop(['index'],axis=1)
        except:
            pass
        self.fib_cnx.close()
        return 0

    ''' Keltner Channels for display data'''

    async def keltner_channels(self, length: int, factor: int = 2, displace: int = None, skip_db=False,interval='1d'):
        try:
            with threading.Lock():
                self.data_cp = self.data.copy()
                # self.data_cp=self.data_cp.reset_index()
                ema_task = self.apply_ema(length, length, skip_db=skip_db,interval=interval)  # apply length ema for middle band
                self.keltner = pd.DataFrame({'middle': [], 'upper': [], 'lower': []}, dtype=float)
                true_range = pd.DataFrame(columns=['trueRange'], dtype=float)
                avg_true_range = pd.DataFrame(columns=['AvgTrueRange'], dtype=float)
                prev_row = None
                await ema_task
                for index, row in self.data_cp.iterrows():
                    # CALCULATE TR ---MAX of ( H – L ; H – C.1 ; C.1 – L )
                    if index == 0:  # previous close is not valid, so just do same day
                        prev_row = row
                        true_range = true_range.append(
                            {'trueRange': max(abs(row['High'] - row['Low']),
                                              abs(row['High'] - row['Low']),
                                              abs(row['Low'] - row['Low']))},
                            ignore_index=True)
                    else:  # get previous close vals
                        try:
                            contains_16 = row['Date'].hour == 16
                            if contains_16:
                                continue
                        except Exception as e:
                            print(e)
                        true_range = true_range.append({'trueRange': max(abs(row['High'] - row['Low']),
                                                                         abs(row['High'] - prev_row['Close']),
                                                                         abs(row['Low'] - prev_row['Close']))},
                                                       ignore_index=True)
                        prev_row = row
                # iterate through keltner and calculate ATR
                for index, row in self.data_cp.iterrows():
                    try:
                        if index == len(self.data_cp.index) - 1:
                            avg_true_range = avg_true_range.append({'AvgTrueRange': avg_true_range['AvgTrueRange'].iloc[index-1]},
                                                                   ignore_index=True)  # add blank values
                        elif index == 0 or index <= length:
                            avg_true_range = avg_true_range.append({'AvgTrueRange': true_range.iloc[index]},
                                                                   ignore_index=True)  # add blank values
                        else:
                            end_atr = None
                            for i in range(index - length, index):  # go to range from index - length to index
                                if end_atr is None:
                                    end_atr = float(true_range['trueRange'].iloc[i])
                                else:
                                    # summation of all values
                                    end_atr = float(end_atr + true_range['trueRange'].iloc[i])
                            end_atr = end_atr / length
                            avg_true_range = avg_true_range.append({'AvgTrueRange': end_atr}, ignore_index=True)
                    except Exception as e:
                        raise Exception("[Error] Failed to calculate Keltner ATR...\n", str(e))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(fname,exc_type,exc_obj,exc_tb)
        # now, calculate upper and lower bands given all data
        for index, row in avg_true_range.iterrows():
            try:
                if index == len(self.data_cp.index) - 1:  # if last element
                    self.keltner = self.keltner.append({'middle': (self.applied_studies[f'ema14'][index - 1]),
                                                        'upper': self.applied_studies[f'ema14'][index - 1]
                                                                 + (factor * avg_true_range['AvgTrueRange'][
                                                                             index - 1]),
                                                        'lower': self.applied_studies[f'ema14'][index - 1]
                                                                 - (factor * avg_true_range['AvgTrueRange'][
                                                                             index - 1])}
                                                       , ignore_index=True)

                else:  # else
                    self.keltner = self.keltner.append({'middle': self.applied_studies[f'ema14'][index],
                                                        'upper': self.applied_studies[f'ema14'][index]
                                                                 + (factor * avg_true_range['AvgTrueRange'][
                                                                                  index]),
                                                        'lower': self.applied_studies[f'ema14'][index]
                                                                 - (factor * avg_true_range['AvgTrueRange'][
                                                                             index])}
                                                       , ignore_index=True)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                raise Exception("[Error] Failed to calculate Keltner Bands...\n", str(e))
        try:
            self.kelt_cnx = self.db_con.cursor()
        except:
            self.kelt_cnx = self.db_con2.cursor()

        if not skip_db:
            """
                    MYSQL Portion...
                    Store Data on DB...
            """
            # Retrieve query from database, confirm that stock is in database, else make new query
            select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
            self.kelt_cnx.autocommit = True
            # print('[INFO] Select stock')
            resultado = self.kelt_cnx.execute(select_stmt, {'stock': self.indicator.upper()}, multi=True)
            for result in resultado:
                # Query new stock, id
                if len(result.fetchall()) == 0:
                    print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                    raise mysql.connector.Error
                else:
                    select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                    # print('[INFO] Select study id')
                    study_result = self.kelt_cnx.execute(select_study_stmt, {'study': f'keltner{length}-{factor}'},
                                                         multi=True)
                    for s_res in study_result:
                        # Non existent DB value
                        study_id_res = s_res.fetchall()
                        if len(study_id_res) == 0:
                            print(
                                f'[INFO] Failed to query study named keltner{length}-{factor} from database! Creating new Study...\n')
                            insert_study_stmt = """INSERT INTO stocks.study (`study-id`,study) 
                                VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(keltner)s)"""
                            # Insert new study into DB
                            try:
                                insert_result = self.kelt_cnx.execute(insert_study_stmt,
                                                                      {'id': f'keltner{length}{factor}',
                                                                       'keltner': f'keltner{length}-{factor}'},
                                                                      multi=True)
                                self.db_con.commit()

                                # Now get the id from the db
                                retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                                retrieve_study_id_result = self.kelt_cnx.execute(retrieve_study_id_stmt,
                                                                                 {'study': f'keltner{length}-{factor}'},
                                                                                 multi=True)
                                for r in retrieve_study_id_result:
                                    id_result = r.fetchall()
                                    self.study_id = id_result[0][0].decode('latin1')
                            except mysql.connector.errors.IntegrityError:
                                pass
                            except Exception as e:
                                print(f'[ERROR] Failed to Insert study named keltner{length}-{factor}!\n', str(e))
                                raise mysql.connector.Error
                        else:
                            # Get study_id
                            self.study_id = study_id_res[0][0].decode('latin1')
        if not skip_db:

            # Retrieve the stock-id, and data-point id in a single select statement
            try:
                self.kelt_cnx.close()
            except:
                pass
            try:
                self.kelt_cnx = self.db_con.cursor()
            except:
                self.kelt_cnx = self.db_con2.cursor()
            self.kelt_cnx.autocommit = True
            retrieve_data_stmt=''
            is_utilizing_yfinance = False
            if '1d' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`dailydata`.`data-id`,
                 `stocks`.`dailydata`.`stock-id` FROM `stocks`.`dailydata` USE INDEX (`id-and-date`)
                INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`dailydata`.`stock-id`
                 AND `stocks`.`dailydata`.`date`>= DATE(%(bdate)s) 
                 AND `stocks`.`dailydata`.`date`<= DATE(%(edate)s)
                 ORDER BY stocks.`dailydata`.`date` ASC 
                 """
            elif '1wk' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`weeklydata`.`data-id`,
                     `stocks`.`weeklydata`.`stock-id` FROM `stocks`.`weeklydata` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`weeklydata`.`stock-id`
                     AND `stocks`.`weeklydata`.`date`>= DATE(%(bdate)s) 
                     AND `stocks`.`weeklydata`.`date`<= DATE(%(edate)s)
                     ORDER BY stocks.`weeklydata`.`date` ASC 
                     """
            elif '1m' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`monthlydata`.`data-id`,
                 `stocks`.`monthlydata`.`stock-id` FROM `stocks`.`monthlydata` USE INDEX (`id-and-date`)
                INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`monthlydata`.`stock-id`
                 AND `stocks`.`monthlydata`.`date`>= DATE(%(bdate)s) 
                 AND `stocks`.`monthlydata`.`date`<= DATE(%(edate)s)
                 ORDER BY stocks.`monthlydata`.`date` ASC 
                 """
            elif '1y' in interval:
                retrieve_data_stmt = """SELECT `stocks`.`yearlydata`.`data-id`,
                     `stocks`.`yearlydata`.`stock-id` FROM `stocks`.`yearlydata` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`yearlydata`.`stock-id`
                     AND `stocks`.`yearlydata`.`date`>= DATE(%(bdate)s) 
                     AND `stocks`.`yearlydata`.`date`<= DATE(%(edate)s)
                     ORDER BY stocks.`yearlydata`.`date` ASC 
                     """
            else:
                is_utilizing_yfinance = True
                retrieve_data_stmt = f"""SELECT `stocks`.`{interval}data`.`data-id`,
                     `stocks`.`{interval}data`.`stock-id` FROM `stocks`.`{interval}data` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`{interval}data`.`stock-id`
                     AND `stocks`.`{interval}data`.`date`>= %(bdate)s
                     AND `stocks`.`{interval}data`.`date`<= %(edate)s
                     ORDER BY stocks.`{interval}data`.`date` ASC 
                     """

            if is_utilizing_yfinance:
                retrieve_data_result = self.kelt_cnx.execute(retrieve_data_stmt, {'stock': f'{self.indicator.upper()}',
                                                                                  'bdate': self.data["Date"].iloc[
                                                                                      0].strftime(
                                                                                      '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                                      self.data["Date"].iloc[0],
                                                                                      datetime.datetime) else
                                                                                  self.data["Date"].iloc[0],
                                                                                  'edate': self.data["Date"].iloc[
                                                                                      -1].strftime(
                                                                                      '%Y-%m-%d %H:%M:%S') if isinstance(
                                                                                      self.data["Date"].iloc[-1],
                                                                                      datetime.datetime) else
                                                                                  self.data["Date"].iloc[-1]},
                                                             multi=True)
            else:
                retrieve_data_result = self.kelt_cnx.execute(retrieve_data_stmt, {'stock': f'{self.indicator.upper()}',
                                                                                  'bdate': self.data["Date"].iloc[
                                                                                      0].strftime('%Y-%m-%d') if isinstance(
                                                                                      self.data["Date"].iloc[0],
                                                                                      datetime.datetime) else
                                                                                  self.data["Date"].iloc[0],
                                                                                  'edate': self.data["Date"].iloc[
                                                                                      -1].strftime(
                                                                                      '%Y-%m-%d') if isinstance(
                                                                                      self.data["Date"].iloc[-1],
                                                                                      datetime.datetime) else
                                                                                  self.data["Date"].iloc[-1]},
                                                             multi=True)
            self.stock_ids = []
            self.data_ids = []
            stock_id=''
            data_id=''
            # self.data=self.data.drop(['Date'],axis=1)
            for retrieve_result in retrieve_data_result:
                id_res = retrieve_result.fetchall()
                if len(id_res) == 0:
                    print(
                        f'[ERROR] Failed to locate a data-id for current index {index} with date {self.data_cp.loc[index, :]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                    raise Exception('[ERROR] Failed to locate a data-id when parsing keltner data!')
                else:
                    for res in id_res:
                        stock_id=res[1].decode('latin1')
                        data_id=res[0].decode('latin1')
                        self.stock_ids.append(res[1].decode('latin1'))
                        self.data_ids.append(res[0].decode('latin1'))
            # Add once more since there is currently a bug where stock id, data id len doesnt match data len
            self.stock_ids.append(stock_id)
            self.data_ids.append(data_id)

            # Execute insert for study-data
            if '1d' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`daily-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            elif '1wk' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`weekly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            elif '1m' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`monthly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            elif '1y' in interval:
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`yearly-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            else:
                insert_studies_db_stmt = f"""REPLACE INTO `stocks`.`{interval}-study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            insert_list = []
            for index, row in self.keltner.iterrows():
                try:
                    if is_utilizing_yfinance:
                        insert_tuple = (
                            f'AES_ENCRYPT("{self.data_cp.loc[index, :]["Date"].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator}keltner{length}{factor}", UNHEX(SHA2("{self.data_cp.loc[index, :]["Date"].strftime("%Y-%m-%d %H:%M:%S")}{self.indicator}keltner{length}{factor}",512)))',
                            f'{self.stock_ids[index]}',
                            f'{self.data_ids[index]}',
                            f'{self.study_id}',
                            row["middle"],
                            row["upper"],
                            row["lower"])
                    else:
                        insert_tuple = (
                            f'AES_ENCRYPT("{self.data_cp.loc[index, :]["Date"].strftime("%Y-%m-%d")}{self.indicator}keltner{length}{factor}", UNHEX(SHA2("{self.data_cp.loc[index, :]["Date"].strftime("%Y-%m-%d")}{self.indicator}keltner{length}{factor}",512)))',
                            f'{self.stock_ids[index]}',
                            f'{self.data_ids[index]}',
                            f'{self.study_id}',
                            row["middle"],
                            row["upper"],
                            row["lower"])
                except Exception as e:
                    print('[ERROR] Failed to set keltner tuple',e,flush=True)
                insert_list.append(insert_tuple)
            try:
                insert_studies_db_result = self.kelt_cnx.executemany(insert_studies_db_stmt, insert_list)
                self.db_con.commit()
            except mysql.connector.errors.IntegrityError:
                self.kelt_cnx.close()
                pass
            except Exception as e:
                print(f'[ERROR] Failed to insert study-data element keltner{length}{factor} !\n', str(e))
                self.kelt_cnx.close()
                pass
        self.kelt_cnx.close()
        return 0

    def reset_data(self):
        self.applied_studies = pd.DataFrame()

    # append to specified struct
    def append_data(self, struct: pd.DataFrame, label: str, val):
        struct = struct.append({label: val}, ignore_index=True)
        return struct


# s = Studies("SPY")
# s.set_data_from_range(datetime.datetime(2019,3,3), datetime.datetime(2019,4,22), _force_generate=False, skip_db=False)
# s.apply_ema("14",'14')
# s.apply_ema("30",'14')


# s.applied_studies = pd.DataFrame()
# s.keltner_channels(20)
# print(s.keltner)
# s.apply_fibonacci()
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")
