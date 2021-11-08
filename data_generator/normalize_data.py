from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import mysql.connector
from mysql.connector import errorcode
import binascii
import uuid
import xml.etree.ElementTree as ET
import datetime
import sys
from pandas.tseries.holiday import USFederalHolidayCalendar
import random

'''
Class that takes in studies and stock data, then transforms the data into a new dataframe.

This frame then gets normalized and outputted.
'''

class Normalizer():
    def __init__(self):
        self.data= pd.DataFrame()
        self.studies= pd.DataFrame(columns=['ema14','ema30'])
        self.normalized_data = pd.DataFrame()
        self.unnormalized_data = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
        self.min_max = MinMaxScaler()
        self.Date = pd.DataFrame(columns=['Date'])
        self.Open = pd.DataFrame(columns=['Open'],dtype='float')
        self.High = pd.DataFrame(columns=['High'],dtype='float')
        self.Low = pd.DataFrame(columns=['Low'],dtype='float')
        self.Close = pd.DataFrame(columns=['Close'],dtype='float')
        self.AdjClose = pd.DataFrame(columns=['Adj Close'],dtype='float')

        '''
        Utilize a config file to establish a mysql connection to the database
        '''
        self.new_uuid_gen = None
        self.path = Path(os.getcwd()).parent.absolute()
        tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(self.path))
        root = tree.getroot()
        # Connect
        try:
            self.db_con = mysql.connector.connect(
              host="127.0.0.1",
              user=root[0].text,
              password=root[1].text,
              raise_on_warnings = True,
              database='stocks',
              charset = 'latin1'
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
    def append_data(self,struct:pd.DataFrame,label:str,val):
        struct = struct.append({label:val},ignore_index=True)
        return struct
    '''
        Utilize mysql to gather data.  Gathers stock data from table.
    '''
    def mysql_read_data(self,ticker,date=None):
        try:
            self.cnx = self.db_con.cursor(buffered=True)
            self.cnx.autocommit = True
            # If string, convert to datetime.datetime                
            valid_datetime=datetime.datetime.now()
            if date is None:
                # Verify date before proceeding 
                holidays=USFederalHolidayCalendar().holidays(start=valid_datetime - datetime.timedelta(days=40),end=valid_datetime).to_pydatetime()
                valid_date=valid_datetime.date()
                if valid_date in holidays and valid_date.weekday() >= 0 and valid_date.weekday() <= 4: #week day holiday
                    valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                    valid_date = (valid_date - datetime.timedelta(days=1))
                if valid_date.weekday()==5: # if saturday
                    valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                    valid_date = (valid_date - datetime.timedelta(days=1))
                if valid_date.weekday()==6: # if sunday
                    valid_datetime = (valid_datetime - datetime.timedelta(days=2))
                    valid_date = (valid_date - datetime.timedelta(days=2))
                if valid_date in holidays:
                    valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                    valid_date = (valid_date - datetime.timedelta(days=1))
                initial_date=valid_datetime
            else:
                initial_date=date
            date_result = self.cnx.execute("""
        select * from stocks.`data` where stocks.`data`.`date` >= DATE(%(start)s) and stocks.`data`.`date` <= DATE(%(end)s) and `stock-id` = (select `id` from stocks.`stock` where stock = %(stock)s) ORDER BY stocks.`data`.`date` ASC
        """, ({'end':initial_date.strftime('%Y-%m-%d'),
               'start':(initial_date - datetime.timedelta(days=40)).strftime('%Y-%m-%d'),
               'stock':ticker.upper()}),multi=True)
        except Exception as e:
            print(f'[ERROR] Failed to retrieve data points for {ticker} from {initial_date.strftime("%Y-%m-%d")} to {(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}!\nException:\n',str(e))
            raise RuntimeError
        # date_res = self.cnx.fetchall()
        # print(date_result,flush=True)
        for res in date_result:
            r_set = res.fetchall()
            if len(r_set) == 0: # empty results 
                raise RuntimeError("Failed to query any results for statement:",f'select * from stocks.`data` where stocks.`data`.date >= DATE({(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}) and stocks.`data`.date <= DATE({initial_date.strftime("%Y-%m-%d")}) and `stock-id` = (select `id` from stocks.`stock` where stock = {ticker.upper()}) ORDER BY stocks.`data`.`date` ASC')
            for set in r_set:
                if len(set) == 0: #if somehow a result got returned and no values included, fail
                    print(f'[ERROR] Failed to retrieve data for {ticker} from range {initial_date}--{initial_date + datetime.timedelta(days=40)}\n')
                    exit(1)
                try:
                    # Iterate through each element to retrieve values
                    for index,row in enumerate(set):
                        # print(row)
                        append_lambda = lambda i: '' if i>=0 and i <=1 else self.append_data(self.Date, 'Date', row) if i==2 else self.append_data(self.Open,'Open',row) if i==3 else self.append_data(self.High,'High',row) if i==4 else self.append_data(self.Low,'Low',row) if i==5 else self.append_data(self.Close,'Close',row) if i==6 else self.append_data(self.AdjClose,'Adj Close',row) if i==7 else print('[ERROR] Could not map lambda!')
                        val = append_lambda(index)
                        if index == 2:
                            self.Date = val
                        elif index == 3:
                            self.Open = val
                        elif index == 4:
                            self.High = val
                        elif index == 5:
                            self.Low = val
                        elif index == 6:
                            self.Close = val
                        elif index == 7:
                            self.AdjClose = val
                except Exception as e:
                    print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    return
        # After retrieving data, Store to self.data
        self.Open.reset_index(drop=True, inplace=True)
        self.Date.reset_index(drop=True, inplace=True)
        self.High.reset_index(drop=True, inplace=True)
        self.Low.reset_index(drop=True, inplace=True)
        self.Close.reset_index(drop=True, inplace=True)
        self.AdjClose.reset_index(drop=True, inplace=True)
        self.data = pd.concat([self.Date,self.Open,self.High,self.Low,self.Close,self.AdjClose],names=['Date','Open','High','Low','Close','Adj Close'],ignore_index=True,axis=1)
        self.data = self.data.rename(columns={0: "Date", 1: "Open", 2: "High",3: "Low",4: "Close",5: "Adj Close"})
        self.cnx.close()
        return self.data
    
    '''
        Utilize mysql to gather data for daily studies
        Gathers the following:
        - ema
        - fibonacci extension
        - keltner channel
    '''
    def mysql_read_studies(self,ticker,study,date=None):
        self.cnx = self.db_con.cursor(buffered=True)
        self.cnx.autocommit = True
        valid_datetime=datetime.datetime.now()
            
        if date is None:
            # Verify date before proceeding 
            holidays=USFederalHolidayCalendar().holidays(start=valid_datetime - datetime.timedelta(days=40),end=valid_datetime).to_pydatetime()
            valid_date=valid_datetime.date()
            if valid_date in holidays and valid_date.weekday() >= 0 and valid_date.weekday() <= 4: #week day holiday
                valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                valid_date = (valid_date - datetime.timedelta(days=1))
            if valid_date.weekday()==5: # if saturday
                valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                valid_date = (valid_date - datetime.timedelta(days=1))
            if valid_date.weekday()==6: # if sunday
                valid_datetime = (valid_datetime - datetime.timedelta(days=2))
                valid_date = (valid_date - datetime.timedelta(days=2))
            if valid_date in holidays:
                valid_datetime = (valid_datetime - datetime.timedelta(days=1))
                valid_date = (valid_date - datetime.timedelta(days=1))
            initial_date=valid_datetime
        else:
            initial_date=date
        if study == 'ema':
            date_result = self.cnx.execute("""
            select stocks.`study-data`.val1, stocks.`study`.study from stocks.`study` INNER JOIN stocks.`study-data` 
            ON stocks.`study-data`.`study-id` = stocks.`study`.`study-id` INNER JOIN stocks.`data` ON
             stocks.`study-data`.`data-id` = `stocks`.`data`.`data-id`
              AND stocks.`data`.date >= %s
               AND stocks.`data`.date <= %s
                AND stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
                AND stocks.`study`.`study` like 'ema%%' 
             INNER JOIN stocks.stock ON stocks.stock.`id` = stocks.`data`.`stock-id` AND stocks.stock.stock = %s ORDER BY stocks.`data`.`date` ASC
            """, ((initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d"),
                  initial_date.strftime('%Y-%m-%d'),
                  ticker),multi=True)
            tmp_14 = pd.DataFrame(columns=['ema14'])
            tmp_30 = pd.DataFrame(columns=['ema30'])
            tmp_20 = pd.DataFrame(columns=['ema20'])
            # print(date_result)
            # date_res = self.cnx.fetchall()
            for set in date_result:
                s = set.fetchall()
                if len(s) == 0:
                    print(f'[ERROR] Failed to retrieve ema study data for {ticker} from range {initial_date.strftime("%Y-%m-%d")}--{(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}!')
                    break
                try:
                    # Iterate through each element to retrieve values
                    cur_val = None
                    for index,row in enumerate(s):
                        cur_val = row[0]
                        # print(row)
                        if row[1] == 'ema14':
                            tmp_14 = tmp_14.append({row[1]:cur_val},ignore_index=True)
                        elif row[1] == 'ema30':
                            tmp_30 = tmp_30.append({row[1]:cur_val},ignore_index=True)
                        elif row[1] == 'ema20':
                            tmp_20 = tmp_20.append({row[1]:cur_val},ignore_index=True)
                        else:
                            print('Unknown value in ema',row)
                            pass
                except Exception as e:
                    print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    self.cnx.close()
                    return
            # After retrieving data, Store to self.data
            self.studies = pd.concat([tmp_14,tmp_30,tmp_20],ignore_index=True,axis=1)
            self.studies = self.studies.rename(columns={0: "ema14", 1: "ema30", 2: "ema20"})
            self.cnx.close()
            return self.studies
        elif study == 'fib':
            date_result = self.cnx.execute("""
            select stocks.`study-data`.val1, stocks.`study-data`.val2,
            stocks.`study-data`.val3, stocks.`study-data`.val4, stocks.`study-data`.val5,
            stocks.`study-data`.val6, stocks.`study-data`.val7, stocks.`study-data`.val8,
            stocks.`study-data`.val9, stocks.`study-data`.val10, stocks.`study-data`.val11,
            stocks.`study-data`.val12, stocks.`study-data`.val13, stocks.`study-data`.val14,
            stocks.`study`.study from stocks.`study` INNER JOIN stocks.`study-data` 
            ON stocks.`study-data`.`study-id` = stocks.`study`.`study-id` INNER JOIN stocks.`data` ON
             stocks.`study-data`.`data-id` = `stocks`.`data`.`data-id` 
             AND stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
             AND stocks.`study`.`study` = 'fibonacci'
              AND stocks.`data`.date >= DATE(%s)
               AND stocks.`data`.date <= DATE(%s) 
             INNER JOIN stocks.stock ON stocks.stock.`id` = stocks.`data`.`stock-id` AND stocks.stock.stock = %s ORDER BY stocks.`data`.`date` ASC
            """, ((initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d"),
                  initial_date.strftime('%Y-%m-%d'),
                  ticker),multi=True)
            # print(len(date_res) - int(self.get_date_difference(start, end).strftime('%j')))
            fib1 = pd.DataFrame(columns=['0.202'])
            fib2 = pd.DataFrame(columns=['0.236'])
            fib3 = pd.DataFrame(columns=['0.241'])
            fib4 = pd.DataFrame(columns=['0.273'])
            fib5 = pd.DataFrame(columns=['0.283'])
            fib6 = pd.DataFrame(columns=['0.316'])
            fib7 = pd.DataFrame(columns=['0.382'])
            fib8 = pd.DataFrame(columns=['0.5'])
            fib9 = pd.DataFrame(columns=['0.618'])
            fib10 = pd.DataFrame(columns=['0.796']) 
            fib11 = pd.DataFrame(columns=['1.556'])
            fib12 = pd.DataFrame(columns=['3.43'])
            fib13 = pd.DataFrame(columns=['3.83'])
            fib14 = pd.DataFrame(columns=['5.44'])
            for set in date_result:
                s = set.fetchall()
                if len(s) == 0:
                    print(f'[ERROR] Failed to retrieve fib study data for {ticker} from range {initial_date.strftime("%Y-%m-%d")}--{(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}')
                    break
                try:
                    # Iterate through each element to retrieve values
                    cur_val = None
                    for index,row in enumerate(s):
                        fib1 = fib1.append({'0.202':row[0]},ignore_index=True)
                        fib2 = fib2.append({'0.236':row[1]},ignore_index=True)
                        fib3 = fib3.append({'0.241':row[2]},ignore_index=True)
                        fib4 = fib4.append({'0.273':row[3]},ignore_index=True)
                        fib5 = fib5.append({'0.283':row[4]},ignore_index=True)
                        fib6 = fib6.append({'0.316':row[5]},ignore_index=True)
                        fib7 = fib7.append({'0.382':row[6]},ignore_index=True)
                        fib8 = fib8.append({'0.5':row[7]},ignore_index=True)
                        fib9 = fib9.append({'0.618':row[8]},ignore_index=True)
                        fib10 = fib10.append({'0.796':row[9]},ignore_index=True)
                        fib11 = fib11.append({'1.556':row[10]},ignore_index=True)
                        fib12 = fib12.append({'3.43':row[11]},ignore_index=True)
                        fib13 = fib13.append({'3.83':row[12]},ignore_index=True)
                        fib14 = fib14.append({'5.44':row[13]},ignore_index=True)
                except Exception as e:
                    print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    self.cnx.close()
            # After retrieving data, Store to self.data
            fib = pd.concat([fib1,fib2,fib3,fib4,fib5,
                             fib6,fib7,fib8,fib9,fib10,
                             fib11,fib12,fib13,fib14],ignore_index=True,axis=1)
            self.fib = fib.rename(columns={0: "0.202", 1: "236",
                                           2: "0.241", 3: "0.273",
                                           4: "0.283", 5: "0.316",
                                           6: "0.382", 7: "0.5",
                                           8: "0.618", 9: "0.796",
                                           10: "1.556", 11: "3.43",
                                           12: "3.83", 13: "5.44",})
            self.cnx.close()
            return self.fib
        elif study == 'keltner':
            date_result = self.cnx.execute("""
            select stocks.`study-data`.val1, stocks.`study-data`.val2, stocks.`study-data`.val3,
             stocks.`study`.study from stocks.`study` INNER JOIN stocks.`study-data` 
            ON stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
             INNER JOIN stocks.`data` ON
             stocks.`study-data`.`data-id` = `stocks`.`data`.`data-id`
              AND stocks.`data`.date >= %s
               AND stocks.`data`.date <= %s
                AND stocks.`study-data`.`study-id` = stocks.`study`.`study-id`
                AND stocks.`study`.`study` = 'keltner20-1.3' 
             INNER JOIN stocks.stock ON stocks.stock.`id` = stocks.`data`.`stock-id` AND stocks.stock.stock = %s ORDER BY stocks.`data`.`date` ASC
            """, ((initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d"),
                  initial_date.strftime('%Y-%m-%d'),
                  ticker),multi=True)
            middle = pd.DataFrame(columns=['middle'])
            upper= pd.DataFrame(columns=['upper'])
            lower= pd.DataFrame(columns=['lower'])
            # print(date_result)
            # date_res = self.cnx.fetchall()
            for set in date_result:
                s = set.fetchall()
                # print(s)
                if len(s) == 0:
                    print(f'[ERROR] Failed to retrieve keltner study data for {ticker} from range {initial_date.strftime("%Y-%m-%d")}--{(initial_date - datetime.timedelta(days=40)).strftime("%Y-%m-%d")}')
                    break
                try:
                    # Iterate through each element to retrieve values
                    cur_val = None
                    for index,row in enumerate(s):
                        middle = middle.append({'middle':row[0]},ignore_index=True)
                        upper = upper.append({'upper':row[1]},ignore_index=True)
                        lower = lower.append({'lower':row[2]},ignore_index=True)
                except Exception as e:
                    print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    self.cnx.close()
                    return
            # After retrieving data, Store to self.data
            keltner = pd.concat([middle,upper,lower],ignore_index=True,axis=1)
            self.keltner = keltner.rename(columns={0: "middle", 1: "upper", 2: "lower"})
            self.cnx.close()
            return self.keltner
        
    '''
        utilize mysql to retrieve data and study data for later usage...
    '''
    def read_data(self,ticker,rand_dates=False):
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
            date=None
        try:
            self.mysql_read_data(ticker,date=date)
            self.data = self.data.drop(['Adj Close','Date'],axis=1)
        except Exception as e:
            print('[ERROR] Failed to read data!\nException:\n',str(e))
            raise RuntimeError
        try:
            self.studies = self.mysql_read_studies(ticker,'ema',date=date)
        except Exception as e:
            print('[ERROR] Failed to read ema studies!\nException:\n',str(e))
            raise RuntimeError
        try:
            self.keltner= self.mysql_read_studies(ticker,'keltner',date=date)
        except Exception as e:
            print('[ERROR] Failed to read keltner study!\nException:\n',str(e))
            raise RuntimeError
        try:
            self.fib = self.mysql_read_studies(ticker,'fib',date=date)
        except Exception as e:
            print('[ERROR] Failed to read ema14 study!\nException:\n',str(e))
            raise RuntimeError
        try:
            self.data = self.data.drop(['index'],axis=1)
            self.data = self.data.drop(['level_0'],axis=1)
        except:
            pass
        pd.set_option("display.max.columns", None)
        
        
    def convert_derivatives(self,out=8):
        self.data = self.data.astype('float')
        self.studies = self.studies.astype('float')
        self.normalized_data = pd.DataFrame((),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                      'Close EMA30 Diff','EMA14 EMA30 Diff'])
        self.normalized_data["Open"] = self.data["Open"]
        self.normalized_data["Close"] = self.data["Close"]
        self.normalized_data["Range"] = self.data["Open"]
        self.normalized_data["Euclidean Open"] = self.data["Open"]
        self.normalized_data["Euclidean Close"] =self.data["Close"]
        self.normalized_data["Open EMA14 Diff"] = self.studies["ema14"]
        self.normalized_data["Open EMA30 Diff"] = self.studies["ema30"]
        self.normalized_data["Close EMA14 Diff"] = self.studies["ema14"]
        self.normalized_data["Close EMA30 Diff"] = self.studies["ema30"]
        self.normalized_data["EMA14 EMA30 Diff"] = self.studies["ema14"]

        for index,row in self.data.iterrows():
            try:
                if index == 0:
                    self.normalized_data.loc[index,"Open"] = 0
                    self.normalized_data.loc[index,"Close"] = 0
                    self.normalized_data.loc[index,"Range"] = abs(self.data.at[index,"Close"] - self.data.at[index,"Open"])
                    self.normalized_data.loc[index,"Euclidean Open"] = np.power(np.power(((self.data.at[index,"Open"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Open"] - self.studies.at[index,"ema30"])),2),1/2)
                    self.normalized_data.loc[index,"Euclidean Close"] = np.power(np.power(((self.data.at[index,"Close"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Close"] - self.studies.at[index,"ema30"])),2),1/2)       
                    self.normalized_data.loc[index,"Open EMA14 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema14'])/self.data.at[index,"Open"]
                    self.normalized_data.loc[index,"Open EMA30 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema30'])/self.data.at[index,"Open"]
                    self.normalized_data.loc[index,"Close EMA14 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema14'])/self.data.at[index,"Close"]
                    self.normalized_data.loc[index,"Close EMA30 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema30'])/self.data.at[index,"Close"]
                    self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = (self.studies.at[index,"ema14"] - self.studies.at[index,'ema30'])/self.studies.at[index,"ema14"]
    
                else:
                    self.normalized_data.loc[index,"Close"] = ((self.data.at[index,"Close"] - self.data.at[index-1,"Close"]))/(1)
                    self.normalized_data.loc[index,"Open"] = ((self.data.at[index,"Open"] - self.data.at[index-1,"Open"]))/(1)
                    self.normalized_data.loc[index,"Range"] = abs(self.data.at[index,"Close"] - self.data.at[index,"Open"])
                    self.normalized_data.loc[index,"Euclidean Open"] = np.power(np.power(((self.data.at[index,"Open"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Open"] - self.studies.at[index,"ema30"])),2),1/2)
                    self.normalized_data.loc[index,"Euclidean Close"] = np.power(np.power(((self.data.at[index,"Close"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Close"] - self.studies.at[index,"ema30"])),2),1/2)       
                    self.normalized_data.loc[index,"Open EMA14 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema14'])/self.data.at[index,"Open"]
                    self.normalized_data.loc[index,"Open EMA30 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema30'])/self.data.at[index,"Open"]
                    self.normalized_data.loc[index,"Close EMA14 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema14'])/self.data.at[index,"Close"]
                    self.normalized_data.loc[index,"Close EMA30 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema30'])/self.data.at[index,"Close"]
                    self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = (self.studies.at[index,"ema14"] - self.studies.at[index,'ema30'])/self.studies.at[index,"ema14"]
            except:
                pass
        return 0
    '''
        Gather the divergence data for further use
    '''
    def convert_divergence(self):
        self.data = self.data.astype('float')
        self.normalized_data = pd.DataFrame((),columns=['Divergence','Gain/Loss'])
        self.normalized_data["Divergence"] = self.data["Open"]
        self.normalized_data["Gain/Loss"] = self.data["Close"]

        for index,row in self.data.iterrows():
            self.normalized_data.loc[index,"Divergence"] = ((self.data.at[index,"High"] - self.data.at[index,"Low"]))/(1)
            self.normalized_data.loc[index,"Gain/Loss"] = ((self.data.at[index,"Close"] - self.data.at[index,"Open"]))/(1)
            
        return 0
    '''
        Normalize:  Use Scalar to normalize given data
    '''
    def normalize(self,out:int=8):
        self.normalized_data = self.normalized_data[-15:]
        self.unnormalized_data = self.normalized_data
        try:
            scaler = self.min_max.fit(self.unnormalized_data) 
            if(out==8):
                self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                      'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
            elif(out==2):
                self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),columns=['Open','Close','Range']) #NORMALIZED DATA STORED IN NP ARRAY
        except Exception as e:
            print('[ERROR] Failed to normalize!\nException:\n',str(e))
            return 1
        return 0
    '''
        Normalize data for the divergence data
    '''
    def normalize_divergence(self):
        self.unnormalized_data = self.normalized_data
        scaler = self.min_max.fit(self.unnormalized_data) 
        try:
            self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),columns=['Divergence','Gain/Loss']) #NORMALIZED DATA STORED IN NP ARRAY
        except:
            return 1
        return 0
    '''
        Unnormalize data
    '''
    def unnormalize(self,data):
        scaler = self.min_max.fit(self.unnormalized_data) 
        if len(data.columns) == 10:
            return pd.DataFrame(scaler.inverse_transform((data.to_numpy())),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                          'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
        elif len(data.columns) == 3:
            tmp_data = pd.DataFrame(columns=['Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                          'Close EMA30 Diff','EMA14 EMA30 Diff'])
            new_data = pd.concat([data,tmp_data],axis=1)
            # print(new_data)
            return pd.DataFrame(scaler.inverse_transform((new_data.to_numpy())),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                          'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
    '''
        Unnormalize the divergence data
    '''
    def unnormalize_divergence(self,data):
        scaler = self.min_max.fit(self.unnormalized_data)
        return pd.DataFrame(scaler.inverse_transform((data.to_numpy())),columns=['Divergence','Gain/Loss'])

# norm = Normalizer()
# norm.read_data("2016-03-18","CCL")
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()