from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.preprocessing import normalize

'''
Class that takes in studies and stock data, then transforms the data into a new dataframe.

This frame then gets normalized and outputted.
'''

class Normalizer():
    def __init__(self):
        self.data= pd.DataFrame()
        self.studies= pd.DataFrame()
        self.normalized_data = pd.DataFrame()
        self.unnormalized_data = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
        self.min_max = MinMaxScaler()
    def read_data(self,date,ticker):
        self.data = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close','High','Low'],axis=1)
        self.studies = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=False)
        pd.set_option("display.max.columns", None)
    def convert_derivatives(self):
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
                self.normalized_data.loc[index,"Close EMA14 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema14']
                self.normalized_data.loc[index,"Close EMA30 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema30']
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = self.studies.at[index,"ema14"] - self.studies.at[index,'ema30']

            else: # ((CLOSE - OPEN)2 -(CLOSE - OPEN)1) / (index2 -index1)
                self.normalized_data.loc[index,"Close Diff"] = ((self.data.at[index,"Close"] - self.data.at[index-1,"Close"]))/(1)
                self.normalized_data.loc[index,"Open Diff"] = ((self.data.at[index,"Open"] - self.data.at[index-1,"Open"]))/(1)
                self.normalized_data.loc[index,"Derivative Diff"] = ((self.data.at[index,"Close"] - self.data.at[index,"Open"]) - (self.data.at[index-1,"Close"] - self.data.at[index-1,"Open"]))/(1)
                self.normalized_data.loc[index,"Derivative EMA14"] = (self.studies.at[index,'ema14']-self.studies.at[index-1,'ema14'])/1
                self.normalized_data.loc[index,"Derivative EMA30"] = (self.studies.at[index,'ema30']-self.studies.at[index-1,'ema30'])/1
                self.normalized_data.loc[index,"Close EMA14 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema14']
                self.normalized_data.loc[index,"Close EMA30 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema30']
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = self.studies.at[index,"ema14"] - self.studies.at[index,'ema30']
        # scaler = StandardScaler() 
        return 0
    def normalize(self):
        self.unnormalized_data = self.normalized_data
        try:
            self.normalized_data = pd.DataFrame(self.min_max.fit_transform(self.normalized_data),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                          'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
        except:
            return 1
        return 0
    def unnormalize(self,data):
        # print(self.min_max.inverse_transform((data.to_numpy())))
        return pd.DataFrame(self.min_max.inverse_transform((data.to_numpy())),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                            'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY
    def display_line(self):
        self.normalized_data.plot()
        plt.show()
# norm = Normalizer()
# norm.read_data("2016-03-18--2016-07-23","CCL")
# DAYS_SAMPLED=15
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()