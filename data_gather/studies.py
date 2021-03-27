from data_gather._data_gather import Gather
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

'''
    This class manages stock-data implementations of studies. 
    As of now, EMA is only implemented, as this is the core indicator for our
    machine learning model.
    save data option enabled
'''
class Studies(Gather):
    def __repr__(self):
        return 'stock_data.studies object <%s>' % ",".join(self.indicator)
    
    def __init__(self,indicator):
        Gather.__init__(self)
        Gather.set_indicator(self, indicator)
        self.applied_studies= pd.DataFrame()
        self.timeframe="1d"
        pd.set_option('display.max_rows',300)
        pd.set_option('display.max_columns',10)
    def set_timeframe(self,new_timeframe):
        self.timeframe = new_timeframe
    def get_timeframe(self):
        return self.timeframe
    # Save EMA to self defined applied_studies
    def apply_ema(self, length, half=None):
        if half is not None:
            self.applied_studies= self.applied_studies.append(pd.DataFrame({f'ema{length}':[self.data.ewm(span=int(length),adjust=False,halflife=half).mean()]}))
        else:
            data = self.data
            for label,content in data.items():
                self.applied_studies= self.applied_studies.append(pd.DataFrame({f'ema{length}_{label}': [content.ewm(span=int(length)).mean()]}))
        return 0
    def save_data_csv(self,path):
        stock_data = pd.concat([self.data],ignore_index=True)
        study_data = pd.concat([self.applied_studies],ignore_index=True)
        stock_data.to_csv("{0}_data.csv".format(path),index=False,sep=',',encoding='utf-8')
        study_data.to_csv("{0}_studies.csv".format(path),index=False,sep=',',encoding='utf-8')
        return 0

