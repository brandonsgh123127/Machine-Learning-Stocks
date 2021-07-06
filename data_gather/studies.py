from data_gather.data_gatherer import Gather
import pandas as pd
import os
import glob
import datetime
import threading
import math
import uuid
import mysql.connector
from mysql.connector import errorcode
import sys,os

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
        super().__init__()
        self.set_indicator(indicator)
        self.applied_studies= pd.DataFrame()
        self.fibonacci_extension = pd.DataFrame()
        self.keltner = pd.DataFrame()
        self.timeframe="1d"
        self.listLock = threading.Lock()
        pd.set_option('display.max_rows',300)
        pd.set_option('display.max_columns',10)
        self.Date = pd.DataFrame(columns=['Date'])
        self.Open = pd.DataFrame(columns=['Open'],dtype='float')
        self.High = pd.DataFrame(columns=['High'],dtype='float')
        self.Low = pd.DataFrame(columns=['Low'],dtype='float')
        self.Close = pd.DataFrame(columns=['Close'],dtype='float')
        self.AdjClose = pd.DataFrame(columns=['Adj Close'],dtype='float')
    def set_timeframe(self,new_timeframe):
        self.timeframe = new_timeframe
    def get_timeframe(self):
        return self.timeframe
    # Save EMA to self defined applied_studies
    def apply_ema(self, length,span=None,half=None):
        # Calculate locally, then push to database
        data = self.data.drop(['Open','High','Low','Adj Close'],axis=1).rename(columns={'Date':'Date','Close':f'ema{length}'})
        data = data.drop(['Date'],axis=1)
        data.astype('float')
        data = data.ewm(alpha=2/(int(length)+1),adjust=True).mean()
        self.applied_studies= pd.concat([self.applied_studies,data],axis=1)
        
        
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        self.cnx = self.db_con.cursor()
        # print('[INFO] Select stock')
        resultado = self.cnx.execute(select_stmt, { 'stock': self.indicator},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.cnx.execute(select_study_stmt, { 'study': f'ema{length}'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    uuid_gen = uuid.uuid4()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named ema{length} from database! Creating new Study...\n')
                        insert_study_stmt = """INSERT INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(ema)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.cnx.execute(insert_study_stmt,{'id':f'{uuid_gen.bytes}{self.indicator}',
                                                                            'ema':f'ema{length}'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` = %(study)s"""
                            retrieve_study_id_result = self.cnx.execute(retrieve_study_id_stmt,{'study':f'ema{length}'},multi=True)
                            for r in retrieve_study_id_result:
                                id_result = r.fetchall()
                                self.study_id = id_result[0][0]
                        except mysql.connector.errors.IntegrityError:
                            pass
                        except Exception as e:
                            print(f'[ERROR] Failed to Insert study into stocks.study named ema{length}!\nException:\n',str(e))
                            raise mysql.connector.Error
                    else:
                        # Get study_id
                        self.study_id = study_id_res[0][0]
                        
                    for index,row in self.applied_studies.iterrows():
                        # Retrieve the stock-id, and data-point id in a single select statement
                        retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` 
                        INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`=%(date)s 
                        """
                        retrieve_data_result = self.cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator}',
                                                                                    'date':self.data.loc[index,:]['Date']},multi=True)
                        for retrieve_result in retrieve_data_result:
                            id_res = retrieve_result.fetchall()
                            if len(id_res) == 0:
                                # print(f'[ERROR] Failed to locate a data /id for current index {index} with date {self.data.loc[index,:]["Date"]} under {retrieve_data_result}')
                                continue
                            else:
                                self.stock_id = id_res[0][1] 
                                self.data_id = id_res[0][0]
                        # Execute insert for study-data
                        insert_studies_db_stmt = """INSERT INTO `stocks`.`study-data` (id, `stock-id`, `data-id`,`study-id`,`val1`) 
                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),
                            %(stock-id)s,%(data-id)s,%(study-id)s,%(val)s)
                            """
                        try:
                            insert_studies_db_result = self.cnx.execute(insert_studies_db_stmt,{'id':f'{uuid_gen.bytes}{self.data.loc[index,:]["Date"]}{self.indicator}',
                                                                                            'stock-id':self.stock_id,
                                                                                            'data-id':self.data_id,
                                                                                            'study-id':self.study_id,
                                                                                            'val':row[f'ema{length}']})
                            self.db_con.commit()
                        except mysql.connector.errors.IntegrityError:
                            pass
                        except Exception as e:
                            # print('[ERROR] Failed to insert study-date element!\nException:\n',str(e))
                            pass
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
    #append to specified struct
    def append_data(self,struct:pd.DataFrame,label:str,val):
        struct = struct.append({label:val},ignore_index=True)
        return struct
    
    # Load data from mysql server
    def load_data_mysql(self,start,end):
        # print(self.cnx)
        # print('LOAD\n\n')
        # Retrieve query from database, confirm that stock is in database, else make new query
        try:
            self.set_data_from_range(datetime.datetime.strptime(start,'%Y-%m-%d'), datetime.datetime.strptime(end,'%Y-%m-%d')) # Make sure data is generated in database
        except:
            self.set_data_from_range(start, end)
            print('f')
        '''
        Fetch stock data per date range
        '''
        self.cnx=self.db_con.cursor(buffered=True)
        date_result = self.cnx.execute("""
        select * from stocks.`data` where date >= %s and date <= %s and `stock-id` = (select `id` from stocks.`stock` where stock = %s) ORDER BY stocks.`data`.`date` ASC
        """, (start, end, 'SPY'),multi=True)
        date_res = self.cnx.fetchall()
        # print(len(date_res) - int(self.get_date_difference(start, end).strftime('%j')))
        for set in date_res:
            if len(set) == 0:
                try:
                    print('\n\n[INFO] Please rerun current function in order to store studies!\n\n')
                    exit(1)
                except Exception as e:
                    print(f'[ERROR] Failed to retrieve data for {self.indicator} from range {start}--{end}\nException:\n',str(e))
                    exit(1)
            try:
                # Iterate through each element to retrieve values
                for index,row in enumerate(set):
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
                # print(self.Open)
                    # print(index, row,'\n')
                # print('________________________________')
            except Exception as e:
                print('[ERROR] Unknown error occurred when retrieving study information!\nException:\n',str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            
        # After retrieving data, Store to self.data
        # print(self.Open)
        self.Open.reset_index(drop=True, inplace=True)
        self.Date.reset_index(drop=True, inplace=True)
        self.High.reset_index(drop=True, inplace=True)
        self.Low.reset_index(drop=True, inplace=True)
        self.Close.reset_index(drop=True, inplace=True)
        self.AdjClose.reset_index(drop=True, inplace=True)
        self.data = pd.concat([self.Date,self.Open,self.High,self.Low,self.Close,self.AdjClose],names=['Date','Open','High','Low','Close','Adj Close'],ignore_index=True,axis=1)
        self.data = self.data.rename(columns={0: "Date", 1: "Open", 2: "High",3: "Low",4: "Close",5: "Adj Close"})


s = Studies("RBLX")
s.load_data_mysql('2019-03-03','2021-04-22')
s.apply_ema("14",'14')
s.apply_ema("30",'14') 


# s.applied_studies = pd.DataFrame()
# s.keltner_channels(20)
# s.apply_fibonacci(1,2, 3)
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")