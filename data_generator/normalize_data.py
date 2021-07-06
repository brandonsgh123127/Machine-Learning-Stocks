from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.preprocessing import normalize
import mysql.connector
from mysql.connector import errorcode
import binascii
import uuid
import xml.etree.ElementTree as ET
import datetime
import sys

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
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err) 
        self.cnx = self.db_con.cursor(buffered=True)
    def append_data(self,struct:pd.DataFrame,label:str,val):
        struct = struct.append({label:val},ignore_index=True)
        return struct
    def mysql_read_data(self,initial_date:datetime.datetime,ticker):
        try:
            date_result = self.cnx.execute("""
        select * from stocks.`data` where stocks.`data`.date >= DATE(%s) and stocks.`data`.date <= DATE(%s) and `stock-id` = (select `id` from stocks.`stock` where stock = %s) ORDER BY stocks.`data`.`date` ASC
        """, (initial_date, initial_date + datetime.timedelta(days=45), ticker),multi=True)
        except Exception as e:
            print(f'[ERROR] Failed to retrieve data points for {ticker} from {initial_date} to {initial_date + datetime.timedelta(days=45)}!\nException:\n',str(e))
        # date_res = self.cnx.fetchall()
        for res in date_result:
            r_set = res.fetchall()
            if len(r_set) == 0:
                print(f'[INFO] NO Data from {initial_date} to {initial_date + datetime.timedelta(days=45)} for {ticker}!\nSkipping...')
                raise RuntimeWarning
            for set in r_set:
                if len(set) == 0:
                    print(f'[ERROR] Failed to retrieve data for {self.indicator} from range {initial_date}--{initial_date + datetime.timedelta(days=45)}\n')
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
        # After retrieving data, Store to self.data
        self.Open.reset_index(drop=True, inplace=True)
        self.Date.reset_index(drop=True, inplace=True)
        self.High.reset_index(drop=True, inplace=True)
        self.Low.reset_index(drop=True, inplace=True)
        self.Close.reset_index(drop=True, inplace=True)
        self.AdjClose.reset_index(drop=True, inplace=True)
        self.data = pd.concat([self.Date,self.Open,self.High,self.Low,self.Close,self.AdjClose],names=['Date','Open','High','Low','Close','Adj Close'],ignore_index=True,axis=1)
        self.data = self.data.rename(columns={0: "Date", 1: "Open", 2: "High",3: "Low",4: "Close",5: "Adj Close"})
        return self.data
    def mysql_read_studies(self,initial_date:datetime.datetime,ticker):
        date_result = self.cnx.execute("""
        select stocks.`study-data`.val1, stocks.`study`.study from stocks.`study` INNER JOIN stocks.`study-data` 
        ON stocks.`study-data`.`study-id` = stocks.`study`.`study-id` INNER JOIN stocks.`data` ON
         stocks.`study-data`.`data-id` = `stocks`.`data`.`data-id` AND stocks.`data`.date >= %s and stocks.`data`.date <= %s 
         INNER JOIN stocks.stock ON stocks.stock.`id` = stocks.`data`.`stock-id` AND stocks.stock.stock = %s ORDER BY stocks.`data`.`date` ASC
        """, (initial_date, initial_date + datetime.timedelta(days=45),ticker),multi=True)
        date_res = self.cnx.fetchall()
        # print(len(date_res) - int(self.get_date_difference(start, end).strftime('%j')))
        tmp_14 = pd.DataFrame(columns=['ema14'])
        tmp_30 = pd.DataFrame(columns=['ema30'])
        for set in date_res:
            if len(set) == 0:
                print(f'[ERROR] Failed to retrieve study data for {self.indicator} from range {initial_date}--{initial_date + datetime.timedelta(days=45)}\nException:\n')
                break
            try:
                # Iterate through each element to retrieve values
                cur_val = None
                for index,row in enumerate(set):
                    if index == 0:
                        cur_val = row
                    elif index == 1:
                        if row == 'ema14':
                            tmp_14 = tmp_14.append({row:cur_val},ignore_index=True)
                        elif row == 'ema30':
                            tmp_30 = tmp_30.append({row:cur_val},ignore_index=True)
            except Exception as e:
                print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
        # After retrieving data, Store to self.data
        self.studies = pd.concat([tmp_14,tmp_30],ignore_index=True,axis=1)
        self.studies = self.studies.rename(columns={0: "ema14", 1: "ema30"})
        return self.studies
    def read_data(self,date,ticker):
        self.data = self.mysql_read_data(date, ticker)
        self.data = self.data.drop(['Adj Close','Date'],axis=1)
        self.studies = self.mysql_read_studies(date,ticker)
        pd.set_option("display.max.columns", None)
    def convert_derivatives(self):
        # print(len(self.studies),len(self.data))
        self.normalized_data = pd.DataFrame((),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                'Close EMA30 Diff','EMA14 EMA30 Diff'])
        self.normalized_data["Open Diff"] = self.data["Open"]
        self.normalized_data["Close Diff"] = self.data["Close"]
        self.normalized_data["Derivative Diff"] = self.data["Open"]
        self.normalized_data["Derivative EMA14"] =self.studies["ema14"]
        self.normalized_data["Derivative EMA30"] =self.studies["ema30"]
        self.normalized_data["Close EMA14 Diff"] = self.data["Close"]
        self.normalized_data["Close EMA30 Diff"] = self.data["Close"]
        self.normalized_data["EMA14 EMA30 Diff"] = self.studies["ema14"]

        for index,row in self.data.iterrows():
            if index == 0:
                self.normalized_data.loc[index,"Open Diff"] = 0
                self.normalized_data.loc[index,"Close Diff"] = 0
                self.normalized_data.loc[index,"Derivative Diff"] = 0
                self.normalized_data.loc[index,"Derivative EMA14"] = 0
                self.normalized_data.loc[index,"Derivative EMA30"] = 0        
                self.normalized_data.loc[index,"Close EMA14 Diff"] = float(self.data.at[index,"Close"]) - float(self.studies.at[index,'ema14'])
                self.normalized_data.loc[index,"Close EMA30 Diff"] = float(self.data.at[index,"Close"]) - float(self.studies.at[index,'ema30'])
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = float(self.studies.at[index,"ema14"]) - float(self.studies.at[index,'ema30'])

            else: # ((CLOSE - OPEN)2 -(CLOSE - OPEN)1) / (index2 -index1)
                self.normalized_data.loc[index,"Close Diff"] = ((float(self.data.at[index,"Close"]) - float(self.data.at[index-1,"Close"])))/(1)
                self.normalized_data.loc[index,"Open Diff"] = ((float(self.data.at[index,"Open"]) - float(self.data.at[index-1,"Open"])))/(1)
                self.normalized_data.loc[index,"Derivative Diff"] = ((float(self.data.at[index,"Close"]) - float(self.data.at[index,"Open"])) - (float(self.data.at[index-1,"Close"]) - float(self.data.at[index-1,"Open"])))/(1)
                self.normalized_data.loc[index,"Derivative EMA14"] = (float(self.studies.at[index,'ema14'])-float(self.studies.at[index-1,'ema14']))/1
                self.normalized_data.loc[index,"Derivative EMA30"] = (float(self.studies.at[index,'ema30'])-float(self.studies.at[index-1,'ema30']))/1
                self.normalized_data.loc[index,"Close EMA14 Diff"] = float(self.data.at[index,"Close"]) - float(self.studies.at[index,'ema14'])
                self.normalized_data.loc[index,"Close EMA30 Diff"] = float(self.data.at[index,"Close"]) - float(self.studies.at[index,'ema30'])
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = float(self.studies.at[index,"ema14"]) - float(self.studies.at[index,'ema30'])
        # scaler = StandardScaler() 
        return 0
    def convert_divergence(self):
        self.normalized_data = pd.DataFrame((),columns=['Divergence','Gain/Loss'])
        self.normalized_data["Divergence"] = self.data["Open"]
        self.normalized_data["Gain/Loss"] = self.data["Close"]

        for index,row in self.data.iterrows():
            self.normalized_data.loc[index,"Divergence"] = ((self.data.at[index,"High"] - self.data.at[index,"Low"]))/(1)
            self.normalized_data.loc[index,"Gain/Loss"] = ((self.data.at[index,"Close"] - self.data.at[index,"Open"]))/(1)
            
        return 0
    def normalize(self):
        self.unnormalized_data = self.normalized_data
        try:
            self.normalized_data = pd.DataFrame(self.min_max.fit_transform(self.normalized_data),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                          'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
        except:
            return 1
        return 0
    def normalize_divergence(self):
        self.unnormalized_data = self.normalized_data
        try:
            self.normalized_data = pd.DataFrame(self.min_max.fit_transform(self.normalized_data),columns=['Divergence','Gain/Loss']) #NORMALIZED DATA STORED IN NP ARRAY
        except:
            return 1
        return 0
    def unnormalize(self,data):
        # print(self.min_max.inverse_transform((data.to_numpy())))
        return pd.DataFrame(self.min_max.inverse_transform((data.to_numpy())),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                            'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
        
    def unnormalize_divergence(self,data):
        return pd.DataFrame(self.min_max.inverse_transform((data.to_numpy())),columns=['Divergence','Gain/Loss'])
    def display_line(self):
        self.normalized_data.plot()
        plt.show()
# norm = Normalizer()
# norm.read_data("2016-03-18--2016-07-23","CCL")
# DAYS_SAMPLED=15
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()