from data_gather._data_gather import Gather
import pandas as pd
import os
import glob
import datetime

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
    def apply_ema(self, length,span,half=None):
        if half is not None:
            self.applied_studies= pd.concat([self.applied_studies,pd.DataFrame({f'ema{length}': [self.data.ewm(span=int(length)).mean()]},halflife=half)],axis=1)
        else:
            data = self.data.drop(['Open','High','Low','Adj Close'],axis=1).rename(columns={'Close':f'ema{length}'}).ewm(alpha=2/(int(length)+1),adjust=True).mean()
            self.applied_studies= pd.concat([self.applied_studies,data],axis=1)
        return 0
    def reset_data(self):
        self.applied_studies = pd.DataFrame()
    def save_data_csv(self,path):
        files_present = glob.glob(f'{path}_data.csv')
        if files_present:
            os.remove(files_present[0])
        self.data.to_csv("{0}_data.csv".format(path),index=False,sep=',',encoding='utf-8')
        self.applied_studies.to_csv("{0}_studies.csv".format(path),index=False,sep=',',encoding='utf-8')
        return 0
    def load_data_csv(self,path):
        self.data = pd.read_csv(f'{path}_data.csv')
        self.applied_studies = pd.read_csv(f'{path}_studies.csv')
        print("Data Loaded")
# s = Studies("SPY")
# s.load_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")
# s.applied_studies = pd.DataFrame()
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")