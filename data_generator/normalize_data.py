from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

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
        self.data = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close'],axis=1)
        self.studies = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=False)
        self.keltner = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_keltner.csv',index_col=False)
        pd.set_option("display.max.columns", None)
    def convert_derivatives(self,out=8):
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
            if index == 0:
                self.normalized_data.loc[index,"Open"] = 0
                self.normalized_data.loc[index,"Close"] = 0
                self.normalized_data.loc[index,"Range"] = abs(self.data.at[index,"Close"] - self.data.at[index,"Open"])
                self.normalized_data.loc[index,"Euclidean Open"] = pow(pow(((self.data.at[index,"Open"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Open"] - self.studies.at[index,"ema30"])),2),1/2)
                self.normalized_data.loc[index,"Euclidean Close"] = pow(pow(((self.data.at[index,"Close"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Close"] - self.studies.at[index,"ema30"])),2),1/2)       
                self.normalized_data.loc[index,"Open EMA14 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema14'])/self.data.at[index,"Open"]
                self.normalized_data.loc[index,"Open EMA30 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema30'])/self.data.at[index,"Open"]
                self.normalized_data.loc[index,"Close EMA14 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema14'])/self.data.at[index,"Close"]
                self.normalized_data.loc[index,"Close EMA30 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema30'])/self.data.at[index,"Close"]
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = (self.studies.at[index,"ema14"] - self.studies.at[index,'ema30'])/self.studies.at[index,"ema14"]

            else:
                self.normalized_data.loc[index,"Close"] = ((self.data.at[index,"Close"] - self.data.at[index-1,"Close"]))/(1)
                self.normalized_data.loc[index,"Open"] = ((self.data.at[index,"Open"] - self.data.at[index-1,"Open"]))/(1)
                self.normalized_data.loc[index,"Range"] = abs(self.data.at[index,"Close"] - self.data.at[index,"Open"])
                self.normalized_data.loc[index,"Euclidean Open"] = pow(pow(((self.data.at[index,"Open"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Open"] - self.studies.at[index,"ema30"])),2),1/2)
                self.normalized_data.loc[index,"Euclidean Close"] = pow(pow(((self.data.at[index,"Close"] - self.studies.at[index,"ema14"])+(self.data.at[index,"Close"] - self.studies.at[index,"ema30"])),2),1/2)       
                self.normalized_data.loc[index,"Open EMA14 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema14'])/self.data.at[index,"Open"]
                self.normalized_data.loc[index,"Open EMA30 Diff"] = (self.data.at[index,"Open"] - self.studies.at[index,'ema30'])/self.data.at[index,"Open"]
                self.normalized_data.loc[index,"Close EMA14 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema14'])/self.data.at[index,"Close"]
                self.normalized_data.loc[index,"Close EMA30 Diff"] = (self.data.at[index,"Close"] - self.studies.at[index,'ema30'])/self.data.at[index,"Close"]
                self.normalized_data.loc[index,"EMA14 EMA30 Diff"] = (self.studies.at[index,"ema14"] - self.studies.at[index,'ema30'])/self.studies.at[index,"ema14"]
        return 0
    def convert_divergence(self):
        self.normalized_data = pd.DataFrame((),columns=['Divergence','Gain/Loss'])
        self.normalized_data["Divergence"] = self.data["Open"]
        self.normalized_data["Gain/Loss"] = self.data["Close"]

        for index,row in self.data.iterrows():
            self.normalized_data.loc[index,"Divergence"] = ((self.data.at[index,"High"] - self.data.at[index,"Low"]))/(1)
            self.normalized_data.loc[index,"Gain/Loss"] = ((self.data.at[index,"Close"] - self.data.at[index,"Open"]))/(1)
            
        return 0
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
    def normalize_divergence(self):
        self.unnormalized_data = self.normalized_data
        scaler = self.min_max.fit(self.unnormalized_data) 
        try:
            self.normalized_data = pd.DataFrame(scaler.fit_transform(self.normalized_data),columns=['Divergence','Gain/Loss']) #NORMALIZED DATA STORED IN NP ARRAY
        except:
            return 1
        return 0
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
    def unnormalize_divergence(self,data):
        scaler = self.min_max.fit(self.unnormalized_data)
        return pd.DataFrame(scaler.inverse_transform((data.to_numpy())),columns=['Divergence','Gain/Loss'])
    def display_line(self):
        self.normalized_data.plot()
        plt.show()
# norm = Normalizer()
# norm.read_data("2016-03-18--2016-07-23","CCL")
# DAYS_SAMPLED=15
# norm.convert_derivatives()
# print(norm.normalized_data)
# norm.display_line()