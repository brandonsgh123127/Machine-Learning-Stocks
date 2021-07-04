from data_gather._data_gather import Gather
import pandas as pd
import os
import glob
import datetime
import threading
import math
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
        self.fibonacci_extension = pd.DataFrame()
        self.keltner = pd.DataFrame()
        self.timeframe="1d"
        self.listLock = threading.Lock()
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
    '''
        val1 first low/high
        val2 second low/high
        val3 third low/high to predict levels
    '''
    def fib_help(self,val1,val2,val3,fib_val):
        if val1>val2: # means val3 is a high point, predict down
            return ( val3 - ((val3-val2)*fib_val))
        else:
            return ( val3 + ((val3-val2)*fib_val))
    '''
    Fibonacci extensions utilized for predicting key breaking points
        val2 ------------------------ 
       ||    
      / \   ---------------------
     /  \  /-----------------------
    /   \ /
val1    val3_________________________
    '''
    def apply_fibonacci(self,val1,val2,val3):
        '''
        Fibonacci values:
        `0.236
        `0.382
        `0.5
        `0.618
        `0.796
        `0.316
        `0.202
        `0.241
        `0.283
        `1.556
        `2.73
        `5.44
        `3.83
        `3.43
        '''
        # Find greatest/least 3 points for pattern
        
        '''
        TO BE IMPLEMENTED
        '''
        min = (self.data['Low'].min(),self.data['Low'].idxmin())
        max = (self.data['High'].max(),self.data['High'].idxmax())
        val1=None;val2=None;val3=None
        # iterate through data to find all possible points in order
        local_max = self.data.High[(self.data.High.shift(1) < self.data.High) & (self.data.High.shift(-1) < self.data.High)]
        local_min = self.data.Low[(self.data.Low.shift(1) > self.data.Low) & (self.data.Low.shift(-1) > self.data.Low)]
        local_max = local_max.reset_index()
        local_min = local_min.reset_index()
        new_set = pd.concat([local_max,local_min]).set_index(['index']).sort_index()
        print(new_set,min,max)
        # after this, iterate new list and find which direction stock may go
          

        # calculate values 
        self.fibonacci_extension= pd.DataFrame({'Values':[self.fib_help(val1,val2,val3,0.202),self.fib_help(val1,val2,val3,0.236),self.fib_help(val1,val2,val3,0.241),
                                                          self.fib_help(val1,val2,val3,0.273),self.fib_help(val1,val2,val3,0.283),self.fib_help(val1,val2,val3,0.316),
                                                          self.fib_help(val1,val2,val3,0.382),self.fib_help(val1,val2,val3,0.5),self.fib_help(val1,val2,val3,0.618),
                                                          self.fib_help(val1,val2,val3,0.796),self.fib_help(val1,val2,val3,1.556),self.fib_help(val1,val2,val3,3.43),
                                                          self.fib_help(val1,val2,val3,3.83),self.fib_help(val1,val2,val3,5.44)]})
        return 0
    def keltner_channels(self,length,factor=None,displace=None):
        self.data_cp = self.data.copy()
        self.apply_ema(length,length) # apply length ema for middle band
        self.keltner = pd.DataFrame({'middle':[],'upper':[],'lower':[]})
        # self.keltner['middle']= self.applied_studies[f'ema{length}'].to_list()
        # print(self.keltner['middle'])
        self.data=self.data_cp
        true_range = pd.DataFrame({'trueRange':[]})
        avg_true_range = pd.DataFrame({'AvgTrueRange':[]})
        prev_row = None
        for index,row in self.data_cp.iterrows():
            # CALCULATE TR ---MAX of ( H – L ; H – C.1 ; C.1 – L )
            if index == 0: # previous close is not valid, so just do 0
                prev_row = row
                true_range=true_range.append({'trueRange':max([row['High']-row['Low'],row['High']-row['Low'],row['Low']-row['Low']])},ignore_index=True)
            else:#get previous close vals
                true_range=true_range.append({'trueRange':max([row['High']-row['Low'],row['High']-prev_row['Close'],row['Low']-prev_row['Close']])},ignore_index=True)
                prev_row=row  
                
        # iterate through keltner and calculate ATR
        for index,row in self.data.iterrows():
            if index == 0 or index <= length:
                avg_true_range=avg_true_range.append({'AvgTrueRange':-1},ignore_index=True) #add blank values
            else:
                end_atr = None
                for i in range(index-length-1,index): # go to range from index - length to index
                    if end_atr is None:
                        end_atr = true_range['trueRange'][i:i+1].to_numpy()
                    else:
                        # summation of all values
                        end_atr = int(end_atr + true_range['trueRange'][i:i+1].to_numpy())
                end_atr = end_atr /length
                avg_true_range=avg_true_range.append({'AvgTrueRange':end_atr},ignore_index=True)
        # now, calculate upper and lower bands given all data
        for index,row in avg_true_range.iterrows():
            # print(float(self.keltner['middle'][index:index+1]-(2*avg_true_range['AvgTrueRange'][index:index+1])))
            self.keltner=self.keltner.append({'middle':float(self.applied_studies[f'ema{length}'][index:index+1]),'upper':float(self.applied_studies[f'ema{length}'][index:index+1]+(2*avg_true_range['AvgTrueRange'][index:index+1])),'lower':float(self.applied_studies[f'ema{length}'][index:index+1]-(2*avg_true_range['AvgTrueRange'][index:index+1]))},ignore_index=True)
        # print(self.keltner)
        return 0
    def reset_data(self):
        self.applied_studies = pd.DataFrame()
    def save_data_csv(self,path):
        files_present = glob.glob(f'{path}_data.csv')
        if files_present:
            with self.listLock:
                try:
                    os.remove("{0}_data.csv".format(path))
                except:
                    pass
        files_present = glob.glob(f'{path}_studies.csv')
        if files_present:
            with self.listLock:
                try:
                    os.remove("{0}_studies.csv".format(path))
                except:
                    pass
        with self.listLock:
            self.data.to_csv("{0}_data.csv".format(path),index=False,sep=',',encoding='utf-8')
            self.applied_studies.to_csv("{0}_studies.csv".format(path),index=False,sep=',',encoding='utf-8')
        return 0
    def load_data_csv(self,path):
        self.data = pd.read_csv(f'{path}_data.csv')
        self.applied_studies = pd.read_csv(f'{path}_studies.csv')
        # print("Data Loaded")
# s = Studies("SPY")
# s.load_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")
# s.applied_studies = pd.DataFrame()
# s.keltner_channels(20)
# s.apply_fibonacci(1,2, 3)
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")