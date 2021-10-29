from data_gather._data_gather import Gather
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
import os
import glob
import datetime
import threading
import gc
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
        with threading.Lock():
            Gather.__init__(self)
            Gather.set_indicator(self, indicator)
        self.applied_studies= pd.DataFrame(dtype=float)
        self.fibonacci_extension = pd.DataFrame()
        self.keltner = pd.DataFrame()
        self.timeframe="1d"
        self.listLock = threading.Lock()
        # pd.set_option('display.max_rows',300)
        # pd.set_option('display.max_columns',10)
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
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        self.cnx = self.db_con.cursor()
        self.cnx.autocommit = True
        # print('[INFO] Select stock')
        resultado = self.cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.cnx.execute(select_study_stmt, { 'study': f'ema{length}'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named ema{length} from database! Creating new Study...\n')
                        insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(ema)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.cnx.execute(insert_study_stmt,{'id':f'{length}',
                                                                            'ema':f'ema{length}'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                            retrieve_study_id_result = self.cnx.execute(retrieve_study_id_stmt,{'study':f'ema{length}'},multi=True)
                            for r in retrieve_study_id_result:
                                id_result = r.fetchall()
                                self.study_id = id_result[0][0].decode('latin1')
                        except mysql.connector.errors.IntegrityError:
                            pass
                        except Exception as e:
                            print(f'[ERROR] Failed to Insert study into stocks.study named ema{length}!\nException:\n',str(e))
                            raise mysql.connector.Error
                    
                    else:
                        # Get study_id
                        self.study_id = study_id_res[0][0].decode('latin1')
                    
                    
                    # Now, Start the process for inserting ema data...
                    date_range =[d.strftime('%Y-%m-%d') for d in pd.date_range(self.data.iloc[0]['Date'], self.data.iloc[-1]['Date'])] #start/end date list
                    holidays=USFederalHolidayCalendar().holidays(start=f'{datetime.datetime.now().year}-01-01',end=f'{datetime.datetime.now().year}-12-31').to_pydatetime()
                    # For each date, verify data is in the specified range by removing any unnecessary dates first
                    for date in date_range:
                        datetime_date=datetime.datetime.strptime(date,'%Y-%m-%d')
                        if datetime_date.weekday() == 5 or datetime_date in holidays:
                            date_range.remove(date)
                    # Second iteration needed to delete Sunday dates for some unknown reason...
                    for d in date_range:
                        datetime_date=datetime.datetime.strptime(d,'%Y-%m-%d')
                        if datetime_date.weekday() == 6:
                            date_range.remove(d)
                            
                    # iterate through each data row and verify data is in place before continuing...
                    study_data=pd.DataFrame(columns=[f'ema{length}'])
                    for index,row in self.data.iterrows():
                        self.cnx = self.db_con.cursor()
                        self.cnx.autocommit = True
   
                        # Before inserting data, check cached data, verify if there is data there...
                        check_cache_studies_db_stmt = """SELECT `stocks`.`data`.`date`,`stocks`.`data`.`open`,
                        `stocks`.`data`.`high`,`stocks`.`data`.`low`,
                        `stocks`.`data`.`close`,`stocks`.`data`.`adj-close`,
                        `stocks`.`study-data`.`val1` 
                         FROM stocks.`data` INNER JOIN stocks.stock 
                        ON `stock-id` = stocks.stock.`id` 
                          AND stocks.stock.`stock` = %(stock)s
                           AND `stocks`.`data`.`date` = DATE(%(date)s)
                           INNER JOIN stocks.`study-data` ON
                            stocks.stock.`id` = stocks.`study-data`.`stock-id`
                            AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`
                            AND stocks.`study-data`.`study-id` = %(id)s
                            """

                        try:
                            check_cache_studies_db_result = self.cnx.execute(check_cache_studies_db_stmt,{'stock':self.indicator.upper(),    
                                                                                            'date':self.data.loc[index,:]["Date"].strftime('%Y-%m-%d') if isinstance(self.data.loc[index,:]["Date"],datetime.datetime) else self.data.loc[index,:]["Date"],
                                                                                            'id': self.study_id},multi=True)
                            # Retrieve date, verify it is in date range, remove from date range
                            for res in check_cache_studies_db_result:
                                res= res.fetchall()
                                # Convert datetime to str
                                try:
                                    date=datetime.date.strftime(res[0][0],"%Y-%m-%d")
                                except:
                                    continue
                                if date is None:
                                    print(f'[INFO] No prior ema{length} found for {self.indicator.upper()} on {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")}... Generating ema{length} data...!\n',flush=True)
                                else:
                                    # check if date is there, if not fail this
                                    if date in date_range:
                                        study_data = study_data.append({f'ema{length}':res[0][6]},
                                                                        ignore_index=True)
                                        date_range.remove(date)                                 
                                    else:
                                        continue
                        except mysql.connector.errors.IntegrityError: # should not happen
                            self.cnx.close()
                            pass
                        except Exception as e:
                            print('[ERROR] Failed to check for cached ema-data element!\nException:\n',str(e))
                            self.cnx.close()
                            raise mysql.connector.errors.DatabaseError()
                    if len(date_range) == 0: # continue loop if found cached data
                        self.applied_studies=pd.concat([self.applied_studies,study_data])
                        continue
                    # Insert data into db if query above is not met
                    else:
                        print(f'[INFO] Did not query all specified dates within range for ema!  Remaining {date_range}')
                        
                        # Calculate locally, then push to database
                        with threading.Lock():
                            try:
                                data = self.data.drop(['Date'],axis=1)
                            except:
                                pass
                            data = data.copy().drop(['Open','High','Low','Adj Close'],axis=1).rename(columns={'Close':f'ema{length}'}).ewm(alpha=2/(int(length)+1),adjust=True).mean()
                            self.applied_studies= pd.concat([self.applied_studies,data],axis=1)
                            del data
                            gc.collect()

                        # Calculate and store data to DB ...    
                        for index,row in self.applied_studies.iterrows():
                            self.cnx = self.db_con.cursor()
                            self.cnx.autocommit = True
                            # Retrieve the stock-id, and data-point id in a single select statement
                            retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` 
                            INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE(%(date)s) 
                            """
                            retrieve_data_result = self.cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                                        'date':self.data.loc[index,:]['Date'].strftime("%Y-%m-%d")},multi=True)
                            # self.data=self.data.drop(['Date'],axis=1)
                            for retrieve_result in retrieve_data_result:
                                id_res = retrieve_result.fetchall()
                                if len(id_res) == 0:
                                    print(f'[ERROR] Failed to locate a data id for current index {index} with date {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                                    continue
                                else:
                                    self.stock_id = id_res[0][1].decode('latin1')
                                    self.data_id = id_res[0][0].decode('latin1')
                            
                            # Execute insert for study-data
                            insert_studies_db_stmt = """REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) 
                                VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),
                                %(stock-id)s,%(data-id)s,%(study-id)s,%(val)s)
                                """
                            try:
                                insert_studies_db_result = self.cnx.execute(insert_studies_db_stmt,{'id':f'{self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")}{self.indicator.upper()}{length}',
                                                                                                'stock-id':self.stock_id.encode('latin1'),
                                                                                                'data-id':self.data_id,
                                                                                                'study-id':self.study_id,
                                                                                                'val':row[f'ema{length}']})
                                self.db_con.commit()
                            except mysql.connector.errors.IntegrityError:
                                self.cnx.close()
                                pass
                            except Exception as e:
                                print('[ERROR] Failed to insert ema-data element!\nException:\n',str(e))
                                self.cnx.close()
                                pass
        self.cnx.close()
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
        """
                MYSQL PORTION... 
                Check DB before doing calculations
        """
        
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        self.cnx = self.db_con.cursor()
        self.cnx.autocommit = True
        # print('[INFO] Select stock')
        resultado = self.cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.cnx.execute(select_study_stmt, { 'study': f'fibonacci'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named fibonacci from database! Creating new Study...\n')
                        insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(fib)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.cnx.execute(insert_study_stmt,{'id':f'fibonacci',
                                                                            'fib':f'fibonacci'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                            retrieve_study_id_result = self.cnx.execute(retrieve_study_id_stmt,{'study':f'fibonacci'},multi=True)
                            for r in retrieve_study_id_result:
                                id_result = r.fetchall()
                                self.study_id = id_result[0][0].decode('latin1')
                        except mysql.connector.errors.IntegrityError:
                            pass
                        except Exception as e:
                            print(f'[ERROR] Failed to Insert study into stocks.study named fibonacci!\nException:\n',str(e))
                            raise mysql.connector.Error
                    else:
                        # Get study_id
                        self.study_id = study_id_res[0][0].decode('latin1')
                        
                        
                    # Now, Start the process for inserting fib data...
                    date_range =[d.strftime('%Y-%m-%d') for d in pd.date_range(self.data.iloc[0]['Date'], self.data.iloc[-1]['Date'])] #start/end date list
                    holidays=USFederalHolidayCalendar().holidays(start=f'{datetime.datetime.now().year}-01-01',end=f'{datetime.datetime.now().year}-12-31').to_pydatetime()
                    # For each date, verify data is in the specified range by removing any unnecessary dates first
                    for date in date_range:
                        datetime_date=datetime.datetime.strptime(date,'%Y-%m-%d')
                        if datetime_date.weekday() == 5 or datetime_date in holidays:
                            date_range.remove(date)
                    # Second iteration needed to delete Sunday dates for some unknown reason...
                    for d in date_range:
                        datetime_date=datetime.datetime.strptime(d,'%Y-%m-%d')
                        if datetime_date.weekday() == 6:
                            date_range.remove(d)
                            
                    # iterate through each data row and verify data is in place before continuing...
                    new_data= pd.DataFrame(columns=['Date','Open','High','Low','Close','Adj. Close'])
                    fib_data=pd.DataFrame(columns=['0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'])
                    for index,row in self.data.iterrows():
                        self.cnx = self.db_con.cursor()
                        self.cnx.autocommit = True
                        # Retrieve the stock-id, and data-point id in a single select statement
                        retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` 
                        INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE(%(date)s) 
                        """
                        retrieve_data_result = self.cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                                    'date':self.data.loc[index,:]["Date"].strftime('%Y-%m-%d') if isinstance(self.data.loc[index,:]["Date"],datetime.datetime) else self.data.loc[index,:]["Date"]},multi=True)
                        # self.data=self.data.drop(['Date'],axis=1)
                        for retrieve_result in retrieve_data_result:
                            id_res = retrieve_result.fetchall()
                            if len(id_res) == 0:
                                print(f'[INFO] Failed to locate a data-id for current index {index} with date {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                                break
                            else:
                                self.stock_id = id_res[0][1].decode('latin1')
                                self.data_id = id_res[0][0].decode('latin1')
                                
                                
                        # Before inserting data, check cached data, verify if there is data there...
                        check_cache_studies_db_stmt = """SELECT `stocks`.`data`.`date`,
                        `stocks`.`study-data`.`val1`,`stocks`.`study-data`.`val2`,
                        `stocks`.`study-data`.`val3`,`stocks`.`study-data`.`val4`,
                        `stocks`.`study-data`.`val5`,`stocks`.`study-data`.`val6`,
                        `stocks`.`study-data`.`val7`,`stocks`.`study-data`.`val8`,
                        `stocks`.`study-data`.`val9`,`stocks`.`study-data`.`val10`,
                        `stocks`.`study-data`.`val11`,`stocks`.`study-data`.`val12`,
                        `stocks`.`study-data`.`val13`,`stocks`.`study-data`.`val14` 
                         FROM stocks.`data` INNER JOIN stocks.stock 
                        ON `stocks`.`data`.`stock-id` = stocks.stock.`id` 
                          AND stocks.stock.`stock` = %(stock)s
                           AND `stocks`.`data`.`date` = DATE(%(date)s)
                           INNER JOIN stocks.`study-data` ON
                            stocks.stock.`id` = stocks.`study-data`.`stock-id`
                            AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`
                            AND stocks.`study-data`.`study-id` = %(id)s
                            """


                        try:
                            check_cache_studies_db_result = self.cnx.execute(check_cache_studies_db_stmt,{'stock':self.indicator.upper(),    
                                                                                            'date':self.data.loc[index,:]["Date"].strftime('%Y-%m-%d') if isinstance(self.data.loc[index,:]["Date"],datetime.datetime) else self.data.loc[index,:]["Date"],
                                                                                            'id': self.study_id},multi=True)
                            # Retrieve date, verify it is in date range, remove from date range
                            for res in check_cache_studies_db_result:
                                # print(str(res.statement))

                                res= res.fetchall()
                                # Convert datetime to str
                                try:
                                    date=datetime.date.strftime(res[0][0],"%Y-%m-%d")
                                except:
                                    continue
                                if date is None:
                                    print(f'[INFO] No prior fib found for {self.indicator.upper()} on {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")}... Creating fib data...!\n',flush=True)
                                else:
                                    # check if date is there, if not fail this
                                    if date in date_range:
                                        date_range.remove(date)
                                        fib_data = fib_data.append({'0.202':res[0][1],'0.236':res[0][2],
                                                                    '0.241':res[0][3],'0.273':res[0][4],
                                                                    '0.283':res[0][5],'0.316':res[0][6],
                                                                    '0.382':res[0][7],'0.5':res[0][8],
                                                                    '0.618':res[0][9],'0.796':res[0][10],
                                                                    '1.556':res[0][11],'3.43':res[0][12],
                                                                    '3.83':res[0][13],'5.44':res[0][14]},
                                                                    ignore_index=True)
                                        
                                    else:
                                        continue
                        except mysql.connector.errors.IntegrityError: # should not happen
                            self.cnx.close()
                            pass
                        except Exception as e:
                            print('[ERROR] Failed to check for cached fib-data element!\nException:\n',str(e))
                            self.cnx.close()
                            raise mysql.connector.errors.DatabaseError()
                    if len(date_range) == 0: # continue loop if found cached data
                        self.fibonacci_extension=fib_data
                        continue
                    else:
                        print(f'[INFO] Did not query all specified dates within range for fibonacci!  Remaining {date_range}')
                        
                        """
                        Do Calculations, then Insert new data to mysql...
                        """
                        '''
                    Fibonacci values:
                    0.236
                    0.382
                    0.5
                    0.618
                    0.796
                    0.316
                    0.202
                    0.241
                    0.283
                    1.556
                    2.73
                    5.44
                    3.83
                    3.43
                    '''
                    # Find greatest/least 3 points for pattern
                    
                    with threading.Lock():
                        # val1=None;val2=None;val3=None
                        # iterate through data to find all min and max
                        try:
                            # self.data = self.data.set
                            self.data = self.data.reset_index()
                            # self.data=self.data.drop(['Date'],axis=1)
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
            
                        # calculate values  -- 14 vals
                        self.fibonacci_extension= pd.DataFrame({'0.202':[self.fib_help(val1,val2,val3,0.202)],'0.236':[self.fib_help(val1,val2,val3,0.236)],'0.241':[self.fib_help(val1,val2,val3,0.241)],
                                                                          '0.273':[self.fib_help(val1,val2,val3,0.273)],'0.283':[self.fib_help(val1,val2,val3,0.283)],'0.316':[self.fib_help(val1,val2,val3,0.316)],
                                                                          '0.382':[self.fib_help(val1,val2,val3,0.382)],'0.5':[self.fib_help(val1,val2,val3,0.5)],'0.618':[self.fib_help(val1,val2,val3,0.618)],
                                                                          '0.796':[self.fib_help(val1,val2,val3,0.796)],'1.556':[self.fib_help(val1,val2,val3,1.556)],'3.43':[self.fib_help(val1,val2,val3,3.43)],
                                                                          '3.83':[self.fib_help(val1,val2,val3,3.83)],'5.44':[self.fib_help(val1,val2,val3,5.44)]})

                        for index,row in self.data.iterrows():
                            self.cnx = self.db_con.cursor()
                            self.cnx.autocommit = True
                            # Retrieve the stock-id, and data-point id in a single select statement
                            retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` 
                            INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE(%(date)s) 
                            """
                            retrieve_data_result = self.cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                                        'date':self.data.loc[index,:]['Date'].strftime("%Y-%m-%d")},multi=True)
                            # self.data=self.data.drop(['Date'],axis=1)
                            for retrieve_result in retrieve_data_result:
                                id_res = retrieve_result.fetchall()
                                if len(id_res) == 0:
                                    print(f'[INFO] Failed to locate a data-id for current index {index} with date {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                                    break
                                else:
                                    self.stock_id = id_res[0][1].decode('latin1')
                                    self.data_id = id_res[0][0].decode('latin1')
                            # Insert data if not in db...
                            insert_studies_db_stmt = """REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                                        `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`) 
                                VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),
                                %(stock-id)s,%(data-id)s,%(study-id)s,%(val1)s,%(val2)s,
                                %(val3)s,%(val4)s,%(val5)s,%(val6)s,%(val7)s,%(val8)s,
                                %(val9)s,%(val10)s,%(val11)s,%(val12)s,%(val13)s,%(val14)s)
                                """
                            try:
                                # print(type(self.stock_id),type(self.data_id),type(self.study_id),row['ema14'])
                                insert_studies_db_result = self.cnx.execute(insert_studies_db_stmt,{'id':f'{self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")}{self.indicator.upper()}fibonacci',
                                                                                                'stock-id':self.stock_id.encode('latin1'),
                                                                                                'data-id':self.data_id,
                                                                                                'study-id':self.study_id,
                                                                                                'val1':self.fibonacci_extension.at[0,"0.202"],
                                                                                                'val2':self.fibonacci_extension.at[0,"0.236"],
                                                                                                'val3':self.fibonacci_extension.at[0,"0.241"],
                                                                                                'val4':self.fibonacci_extension.at[0,"0.273"],
                                                                                                'val5':self.fibonacci_extension.at[0,"0.283"],
                                                                                                'val6':self.fibonacci_extension.at[0,"0.316"],
                                                                                                'val7':self.fibonacci_extension.at[0,"0.382"],
                                                                                                'val8':self.fibonacci_extension.at[0,"0.5"],
                                                                                                'val9':self.fibonacci_extension.at[0,"0.618"],
                                                                                                'val10':self.fibonacci_extension.at[0,"0.796"],
                                                                                                'val11':self.fibonacci_extension.at[0,"1.556"],
                                                                                                'val12':self.fibonacci_extension.at[0,"3.43"],
                                                                                                'val13':self.fibonacci_extension.at[0,"3.83"],
                                                                                                'val14':self.fibonacci_extension.at[0,"5.44"]
                                                                                                })
                            except mysql.connector.errors.IntegrityError:
                                self.cnx.close()
                                pass
                            except Exception as e:
                                print('[ERROR] Failed to insert study-data element fibonacci!\nException:\n',str(e))
                                self.cnx.close()
                                pass
                        try:
                            self.db_con.commit()
                        except mysql.connector.errors.IntegrityError:
                            self.cnx.close()
                            pass
                        except Exception as e:
                            print('[ERROR] Failed to insert fib-data element fibonacci!\nException:\n',str(e))
                            self.cnx.close()
                            pass

                                
        self.cnx.close()
        return 0
    ''' Keltner Channels for display data'''
    def keltner_channels(self,length:int,factor:int=2,displace:int=None):
        with threading.Lock():
            self.data_cp = self.data.copy()
            # self.data_cp=self.data_cp.reset_index()
            self.apply_ema(length,length) # apply length ema for middle band
            self.keltner = pd.DataFrame({'middle':[],'upper':[],'lower':[]},dtype=float)
            self.data=self.data_cp
            true_range = pd.DataFrame(columns=['trueRange'],dtype=float)
            avg_true_range = pd.DataFrame(columns=['AvgTrueRange'],dtype=float)
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
                if index == 0 or index <= length or index == len(self.data.index)-1:
                    avg_true_range=avg_true_range.append({'AvgTrueRange':1.33},ignore_index=True) #add blank values
                else:
                    end_atr = None
                    for i in range(index-length-1,index): # go to range from index - length to index
                        if end_atr is None:
                            end_atr = int(true_range['trueRange'][i:i+1].to_numpy())
                        else:
                            # summation of all values
                            end_atr = int(end_atr + true_range['trueRange'][i:i+1].to_numpy())
                    end_atr = end_atr / length
                    avg_true_range=avg_true_range.append({'AvgTrueRange':end_atr},ignore_index=True)
            # now, calculate upper and lower bands given all data
            for index,row in avg_true_range.iterrows():
                try:
                    if index == len(self.data.index) - 1: # if last element
                        self.keltner=self.keltner.append({'middle':(self.applied_studies[f'ema14'][index-1:index]),
                                      'upper':self.applied_studies[f'ema14'][index-1:index]
                                      +(factor*avg_true_range['AvgTrueRange'][index-1:index]),
                                      'lower':self.applied_studies[f'ema14'][index-1:index]
                                      -(factor*avg_true_range['AvgTrueRange'][index-1:index])}
                                      ,ignore_index=True)
    
                    else: #else
                        self.keltner=self.keltner.append({'middle':self.applied_studies[f'ema14'][index:index+1],
                                                          'upper':self.applied_studies[f'ema14'][index:index+1]
                                                          +float(factor*avg_true_range['AvgTrueRange'][index:index+1]),
                                                          'lower':self.applied_studies[f'ema14'][index:index+1]
                                                          -(factor*avg_true_range['AvgTrueRange'][index:index+1])}
                                                          ,ignore_index=True)
                except:
                    if index == len(self.data.index) - 1: # if last element
                        self.keltner=self.keltner.append({'middle':(self.applied_studies[f'ema14'][index-1:index]),
                                      'upper':float(self.applied_studies[f'ema14'][index-1:index])
                                      +(factor*avg_true_range['AvgTrueRange'][index-1:index]),
                                      'lower':float(self.applied_studies[f'ema14'][index-1:index])
                                      -(factor*avg_true_range['AvgTrueRange'][index-1:index])}
                                      ,ignore_index=True)

                    else: #else
                        self.keltner=self.keltner.append({'middle':self.applied_studies[f'ema14'][index:index+1],
                                                          'upper':float(self.applied_studies[f'ema14'][index:index+1])
                                                          +float(factor*avg_true_range['AvgTrueRange'][index:index+1]),
                                                          'lower':float(self.applied_studies[f'ema14'][index:index+1])
                                                          -(factor*avg_true_range['AvgTrueRange'][index:index+1])}
                                                          ,ignore_index=True)
            """
                    MYSQL Portion...
                    Store Data on DB...
            """
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        self.cnx = self.db_con.cursor()
        self.cnx.autocommit = True
        # print('[INFO] Select stock')
        resultado = self.cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.cnx.execute(select_study_stmt, { 'study': f'keltner{length}-{factor}'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named keltner{length}-{factor} from database! Creating new Study...\n')
                        insert_study_stmt = """INSERT INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(keltner)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.cnx.execute(insert_study_stmt,{'id':f'keltner{length}{factor}',
                                                                            'keltner':f'keltner{length}-{factor}'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                            retrieve_study_id_result = self.cnx.execute(retrieve_study_id_stmt,{'study':f'keltner{length}-{factor}'},multi=True)
                            for r in retrieve_study_id_result:
                                id_result = r.fetchall()
                                self.study_id = id_result[0][0].decode('latin1')
                        except mysql.connector.errors.IntegrityError:
                            pass
                        except Exception as e:
                            print(f'[ERROR] Failed to Insert study named keltner{length}-{factor}!\nException:\n',str(e))
                            raise mysql.connector.Error
                    else:
                        # Get study_id
                        self.study_id = study_id_res[0][0].decode('latin1')
                        
                    for index,row in self.keltner.iterrows():
                        self.cnx = self.db_con.cursor()
                        self.cnx.autocommit = True
                        # Retrieve the stock-id, and data-point id in a single select statement
                        retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id` FROM `stocks`.`data` 
                        INNER JOIN `stocks`.`stock` ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id` AND `stocks`.`data`.`date`= DATE(%(date)s) 
                        """
                        retrieve_data_result = self.cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                                    'date':self.data.loc[index,:]["Date"].strftime('%Y-%m-%d') if isinstance(self.data.loc[index,:]["Date"],datetime.datetime) else self.data.loc[index,:]["Date"]},multi=True)
                        # self.data=self.data.drop(['Date'],axis=1)
                        for retrieve_result in retrieve_data_result:
                            id_res = retrieve_result.fetchall()
                            if len(id_res) == 0:
                                print(f'[ERROR] Failed to locate a data-id for current index {index} with date {self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                                continue
                            else:
                                self.stock_id = id_res[0][1].decode('latin1')
                                self.data_id = id_res[0][0].decode('latin1')
                        # Execute insert for study-data
                        insert_studies_db_stmt = """REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
                            VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),
                            %(stock-id)s,%(data-id)s,%(study-id)s,%(val1)s,%(val2)s,%(val3)s)
                            """
                        try:
                            # print(type(self.stock_id),type(self.data_id),type(self.study_id),type(row['middle']))
                            if isinstance(self.data.loc[index,:]["Date"],datetime.datetime):
                                insert_studies_db_result = self.cnx.execute(insert_studies_db_stmt,{'id':f'{self.data.loc[index,:]["Date"].strftime("%Y-%m-%d")}{self.indicator}keltner{length}{factor}',
                                                                                                'stock-id':self.stock_id.encode('latin1'),
                                                                                                'data-id':self.data_id,
                                                                                                'study-id':self.study_id,
                                                                                                'val1':float(row[f'middle']),
                                                                                                'val2':float(row[f'upper']),
                                                                                                'val3':float(row[f'lower']),
                                                                                                })
                            else:
                                insert_studies_db_result = self.cnx.execute(insert_studies_db_stmt,{'id':f'{self.data.loc[index,:]["Date"]}{self.indicator}keltner{length}{factor}',
                                                                                                'stock-id':self.stock_id.encode('latin1'),
                                                                                                'data-id':self.data_id,
                                                                                                'study-id':self.study_id,
                                                                                                'val1':float(row[f'middle']),
                                                                                                'val2':float(row[f'upper']),
                                                                                                'val3':float(row[f'lower']),
                                                                                                })
                            self.db_con.commit()
                        except mysql.connector.errors.IntegrityError:
                            self.cnx.close()
                            pass
                        except Exception as e:
                            print(f'[ERROR] Failed to insert study-data element keltner{length}{factor} !\nException:',str(e))
                            self.cnx.close()
                            pass
        self.cnx.close()
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
            try:
                self.set_data_from_range(start, end)
            except Exception as e:
                print('[Error] Failed to load mysql data!\nException:\n',str(e))
        '''
        Fetch stock data per date range
        '''
        self.cnx=self.db_con.cursor(buffered=True)
        date_result = self.cnx.execute("""
        select * from stocks.`data` where date >= DATE(%s) and date <= DATE(%s) and `stock-id` = (select `id` from stocks.`stock` where stock = %s) ORDER BY stocks.`data`.`date` ASC
        """, (start, end, self.indicator),multi=True)
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


# s = Studies("RBLX")
# s.load_data_mysql('2019-03-03','2021-04-22')
# s.apply_ema("14",'14')
# s.apply_ema("30",'14') 


# s.applied_studies = pd.DataFrame()
# s.keltner_channels(20)
# print(s.keltner)
# s.apply_fibonacci()
# s.apply_ema("14",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3)))
# s.apply_ema("30",(datetime.datetime(2021,4,22)-datetime.datetime(2021,3,3))) 
# s.save_data_csv("C:\\users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\stock_no_tweets\\spy/2021-03-03--2021-04-22")