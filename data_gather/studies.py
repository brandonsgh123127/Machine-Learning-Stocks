from data_gather._data_gather import Gather
import pandas as pd
import os
import glob
import threading
import gc
import sys
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
        with threading.Lock():
            Gather.__init__(self)
            Gather.set_indicator(self, indicator)
        self.applied_studies= pd.DataFrame()
        self.fibonacci_extension = pd.DataFrame()
        self.keltner = pd.DataFrame()
        self.timeframe="1d"
        self.listLock = threading.Lock()
        # pd.set_option('display.max_rows',300)
        # pd.set_option('display.max_columns',10)
    def set_timeframe(self,new_timeframe):
        self.timeframe = new_timeframe
    def get_timeframe(self):
        return self.timeframe
    # Save EMA to self defined applied_studies
    def apply_ema(self, length,span,half=None):
        if half is not None:
            self.applied_studies= pd.concat([self.applied_studies,pd.DataFrame({f'ema{length}': [self.data.ewm(span=int(length)).mean()]},halflife=half)],axis=1)
        else:
            with threading.Lock():
                data = self.data.copy().drop(['Open','High','Low','Adj Close'],axis=1).rename(columns={'Close':f'ema{length}'}).ewm(alpha=2/(int(length)+1),adjust=True).mean()
                self.applied_studies= pd.concat([self.applied_studies,data],axis=1)
                del data
                gc.collect()
        return 0
    '''
        val1 first low/high
        val2 second low/high
        val3 third low/high to predict levels
    '''
    def fib_help(self,val1,val2,val3,fib_val):
        if val1<val2: # means val 3 is higher low -- upwards
            return ( val3 + ((val2-val1)*fib_val))
        else: # val 3 is a lower high -- downards
            return ( val3 - ((val2-val1)*-(fib_val)))
    '''
    Fibonacci extensions utilized for predicting key breaking points
        val2 ------------------------                 val3
       ||                                    val1   /  \
      / \   ---------------------           / \    /    \ 
     /  \  /----------------------- or     /  \   /      \
    /   \ /                               /    \ /        \
val1    val3_________________________          vall2
    '''
    def apply_fibonacci(self):
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
        
        with threading.Lock():
            # val1=None;val2=None;val3=None
            # iterate through data to find all min and max
            try:
                # self.data = self.data.set
                self.data = self.data.reset_index()
                self.data=self.data.drop(['Date'],axis=1)
                # print(self.data)
            except Exception as e:
                pass
            local_max_high = self.data.High[(self.data.High.shift(1) < self.data.High) & (self.data.High.shift(-1) < self.data.High)]
            local_min_high = self.data.High[(self.data.High.shift(1) > self.data.High) & (self.data.High.shift(-1) > self.data.High)]
            # local_max_high = local_max_high.reset_index()
            local_min_high = local_min_high.rename({"High":'min_high'},axis='columns')
            local_max_low = self.data.Low[(self.data.Low.shift(1) < self.data.Low) & (self.data.Low.shift(-1) < self.data.Low)]
            local_min_low = self.data.Low[(self.data.Low.shift(1) > self.data.Low) & (self.data.Low.shift(-1) > self.data.Low)]
            local_min_low = local_min_low.rename({"Low":'min_low'},axis='columns')

            local_max_low = local_max_low.rename({"Low":'max_low'},axis='columns')
            # local_min_low = local_min_low.reset_index()
            local_max_high = local_max_high.rename({"High":'max_high'},axis='columns')
            
            # After finding min and max values, we can look for local mins and maxes by iterating
            new_set = pd.concat([local_max_low,local_max_high,local_min_low,local_min_high]).sort_index().reset_index()
            new_set.columns=['Index','Vals']
            new_set = new_set.drop(['Index'],axis=1)
            
            
            # After this, iterate new list and find which direction stock may go
            val1=None;val2=None;val3=None
            for i,row in new_set['Vals'].iteritems(): # val 1 
                if i != 0:
                    # if the first value is lower than the close , do upwards fib, else downwards
                    if new_set.at[0,'Vals'] < new_set.at[len(new_set.index)-1,'Vals']:
                        # attempt upwards fib
                        try:
                            if row < float(new_set.at[i - 1,'Vals']) and not float(new_set.at[i + 1,'Vals']) < row : # if low is found, jump to this value
                                val1 =  row
                                # find val2 by finding next local high
                                for j,sub in new_set['Vals'].iteritems():
                                    if j < i:
                                        continue
                                    else: # find val2 by making sure next local high is valid
                                        if sub > float(new_set.at[j + 1,'Vals']) and not float(new_set.at[j - 1,'Vals']) > sub:
                                            val2 = sub
                                            # find val3 by getting next low
                                            for k,low in new_set['Vals'].iteritems():
                                                if k < j:
                                                    continue
                                                else:
                                                    if low < float(new_set.at[k - 1,'Vals']) and not float(new_set.at[k + 1,'Vals']) < low:
                                                        val3 = low
                                                        break 
                                                    else:
                                                        continue
                                            break
                                        else:
                                            continue
                                break
                            else:
                                continue
                                        
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            print("[ERROR] Failed upwards fib!  This could be due to not finding a higher low...",flush=True)  
                    else:
                        # attempt downwards fib
                        try:
                            if row > float(new_set.at[i - 1,'Vals']) and not float(new_set.at[i + 1,'Vals']) > row : # if low is found, jump to this value
                                val1 =  row
                                # find val2 by finding next local high
                                for j,sub in new_set['Vals'].iteritems():
                                    if j < i:
                                        continue
                                    else: # find val2 by making sure next local low is valid
                                        if sub < float(new_set.at[j + 1,'Vals']) and not float(new_set.at[j - 1,'Vals']) < sub:
                                            val2 = sub
                                            # find val3 by getting next high
                                            for k,low in new_set['Vals'].iteritems():
                                                if k < j:
                                                    continue
                                                else:
                                                    if low > float(new_set.at[k - 1,'Vals']) and not float(new_set.at[k + 1,'Vals']) > low:
                                                        val3 = low
                                                        break 
                                                    else:
                                                        continue
                                            break
                                        else:
                                            continue
                                break
                            else:
                                continue
                                        
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            print("[ERROR] Failed downwards fib!  This could be due to not finding a lower high...",flush=True)  
                else:
                    val1=float(row)
                    continue

            # calculate values 
            self.fibonacci_extension= pd.DataFrame({'0.202':[self.fib_help(val1,val2,val3,0.202)],'0.236':[self.fib_help(val1,val2,val3,0.236)],'0.241':[self.fib_help(val1,val2,val3,0.241)],
                                                              '0.273':[self.fib_help(val1,val2,val3,0.273)],'0.283':[self.fib_help(val1,val2,val3,0.283)],'0.316':[self.fib_help(val1,val2,val3,0.316)],
                                                              '0.382':[self.fib_help(val1,val2,val3,0.382)],'0.5':[self.fib_help(val1,val2,val3,0.5)],'0.618':[self.fib_help(val1,val2,val3,0.618)],
                                                              '0.796':[self.fib_help(val1,val2,val3,0.796)],'1.556':[self.fib_help(val1,val2,val3,1.556)],'3.43':[self.fib_help(val1,val2,val3,3.43)],
                                                              '3.83':[self.fib_help(val1,val2,val3,3.83)],'5.44':[self.fib_help(val1,val2,val3,5.44)]})
        return 0
    ''' Keltner Channels for display data'''
    def keltner_channels(self,length:int,factor:int=2,displace:int=None):
        with threading.Lock():
            self.data_cp = self.data.copy()
            self.data_cp=self.data_cp.reset_index()
            self.apply_ema(length,length) # apply length ema for middle band
            self.keltner = pd.DataFrame({'middle':[],'upper':[],'lower':[]})
            self.data=self.data_cp
            true_range = pd.DataFrame(columns=['trueRange'])
            avg_true_range = pd.DataFrame(columns=['AvgTrueRange'])
            prev_row = None
            for index,row in self.data_cp.iterrows():
                # CALCULATE TR ---MAX of ( H – L ; H – C.1 ; C.1 – L )
                if index == 0: # previous close is not valid, so just do same day
                    prev_row = row
                    true_range=true_range.append({'trueRange':max(row['High']-row['Low'],row['High']-row['Low'],row['Low']-row['Low'])},ignore_index=True)
                else:#get previous close vals
                    true_range=true_range.append({'trueRange':max(row['High']-row['Low'],row['High']-prev_row['Close'],row['Low']-prev_row['Close'])},ignore_index=True)
                    prev_row=row  
                    
            # iterate through keltner and calculate ATR
            for index,row in self.data.iterrows():
                if index == 0 or index <= length:
                    avg_true_range=avg_true_range.append({'AvgTrueRange':1},ignore_index=True) #add blank values
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
                self.keltner=self.keltner.append({'middle':float(self.applied_studies[f'ema14'][index:index+1].astype(float)),'upper':float(self.applied_studies[f'ema14'][index:index+1].astype(float))+float(factor*avg_true_range['AvgTrueRange'][index:index+1].astype(float)),'lower':float(self.applied_studies[f'ema14'][index:index+1].astype(float))-float(factor*avg_true_range['AvgTrueRange'][index:index+1].astype(float))},ignore_index=True)
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
        files_present = glob.glob(f'{path}_keltner.csv')
        if files_present:
            with self.listLock:
                try:
                    os.remove("{0}_keltner.csv".format(path))
                except:
                    pass
        files_present = glob.glob(f'{path}_fib.csv')
        if files_present:
            with self.listLock:
                try:
                    os.remove("{0}_fib.csv".format(path))
                except:
                    pass
        with self.listLock:
            with threading.Lock():
                self.data.to_csv("{0}_data.csv".format(path),index=False,sep=',',encoding='utf-8')
                self.applied_studies.to_csv("{0}_studies.csv".format(path),index=False,sep=',',encoding='utf-8')
                self.keltner.to_csv("{0}_keltner.csv".format(path),index=False,sep=',',encoding='utf-8')
                self.fibonacci_extension.to_csv("{0}_fib.csv".format(path),index=False,sep=',',encoding='utf-8')
        return 0
    def load_data_csv(self,path):
        with threading.Lock():
            self.data = pd.read_csv(f'{path}_data.csv')
            self.applied_studies = pd.read_csv(f'{path}_studies.csv')
            self.keltner = pd.read_csv(f'{path}_keltner.csv')
            self.fibonacci_extension = pd.read_csv(f'{path}_fib.csv')
# s = Studies("RBLX")
# s.load_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\rblx/2021-06-23--2021-08-13")
# s.applied_studies = pd.DataFrame()
# s.keltner_channels(20)
# print(s.keltner)
# s.apply_fibonacci()
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")