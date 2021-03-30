from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

class Normalizer():
    def __init__(self):
        print("Normalizer initialized!")
        self.data= pd.DataFrame()
        self.studies= pd.DataFrame()
        self.normalized_data = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
    def read_data(self,date,ticker):
        self.data = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close','High','Low'],axis=1)
        self.studies = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=False)
        self.studies.reset_index()
        pd.set_option("display.max.columns", None)
    def convert_derivatives(self):
        self.normalized_data["Derivative Diff"] = self.data["Open"]
        self.normalized_data["Derivative EMA14"] =self.studies["ema14"]
        self.normalized_data["Derivative EMA30"] =self.studies["ema30"]
        self.normalized_data["Close EMA14 Diff"] = self.data["Close"]
        self.normalized_data["Close EMA30 Diff"] = self.data["Close"]
        self.normalized_data["EMA14 EMA30 Diff"] = self.studies["ema14"]

        for index,row in self.data.iterrows():
            if index == 0:
                self.normalized_data.loc[index,"Derivative Diff"] = 0
                self.normalized_data.loc[index,"Derivative EMA14"] = 0
                self.normalized_data.loc[index,"Derivative EMA30"] = 0        
                self.normalized_data.loc[index,"Close EMA14 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema14']
                self.normalized_data.loc[index,"Close EMA30 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema30']
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = self.studies.at[index,"ema14"] - self.studies.at[index,'ema30']

            else: # ((CLOSE - OPEN)2 -(CLOSE - OPEN)1) / (index2 -index1)
                self.normalized_data.loc[index,"Derivative Diff"] = ((self.data.at[index,"Close"] - self.data.at[index,"Open"]) - (self.data.at[index-1,"Close"] - self.data.at[index-1,"Open"]))/(1)
                self.normalized_data.loc[index,"Derivative EMA14"] = (self.studies.at[index,'ema14']-self.studies.at[index-1,'ema14'])/1
                self.normalized_data.loc[index,"Derivative EMA30"] = (self.studies.at[index,'ema30']-self.studies.at[index-1,'ema30'])/1
                self.normalized_data.loc[index,"Close EMA14 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema14']
                self.normalized_data.loc[index,"Close EMA30 Diff"] = self.data.at[index,"Close"] - self.studies.at[index,'ema30']
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = self.studies.at[index,"ema14"] - self.studies.at[index,'ema30']
        scaler = MinMaxScaler() 
        self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),columns=['Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED DATA STORED IN NP ARRAY

    def display_line(self):
        #self.normalized_data['index'] = range(1, len(self.normalized_data) + 1)
        self.normalized_data.plot()
        plt.show()
norm = Normalizer()
norm.read_data("2018-01-13--2018-03-31","SHOP")
norm.convert_derivatives()
norm.display_line()