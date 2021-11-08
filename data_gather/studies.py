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
    
    def __init__(self,indicator,force_generate=False):
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
        
        self._force_generate=force_generate
        
    def set_timeframe(self,new_timeframe):
        self.timeframe = new_timeframe
    def get_timeframe(self):
        return self.timeframe
    
    
    
    
    
    
    
    
    
    # Save EMA to self defined applied_studies
    def apply_ema(self, length,span=None,half=None):
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        with threading.Lock():
            try: # Try connection to db_con, if not, connect to 
                self.ema_cnx = self.db_con.cursor()
            except:
                self.ema_cnx = self.db_con2.cursor()
            self.ema_cnx.autocommit = True
            # print('[INFO] Select stock')
            resultado = self.ema_cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
            for result in resultado:
                # Query new stock, id
                if len(result.fetchall()) == 0:
                    print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                    raise mysql.connector.Error
                else:
                    select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                    # print('[INFO] Select study id')
                    study_result = self.ema_cnx.execute(select_study_stmt, { 'study': f'ema{length}'},multi=True)
                    for s_res in study_result:
                        # Non existent DB value
                        study_id_res = s_res.fetchall()
                        if len(study_id_res) == 0:
                            print(f'[INFO] Failed to query study named ema{length} from database! Creating new Study...\n')
                            insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                                VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(ema)s)"""
                            # Insert new study into DB
                            try:
                                insert_result = self.ema_cnx.execute(insert_study_stmt,{'id':f'{length}',
                                                                                'ema':f'ema{length}'},multi=True)
                                self.db_con.commit()
                                
                                # Now get the id from the db
                                retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                                retrieve_study_id_result = self.ema_cnx.execute(retrieve_study_id_stmt,{'study':f'ema{length}'},multi=True)
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
                # Before inserting data, check cached data, verify if there is data there...
                try: # Try connection to db_con, if not, connect to 
                    self.ema_cnx = self.db_con.cursor()
                except:
                    self.ema_cnx = self.db_con2.cursor()
                self.ema_cnx.autocommit = True
                check_cache_studies_db_stmt = """SELECT `stocks`.`data`.`date`,
                `stocks`.`study-data`.`val1` 
                 FROM stocks.`data` USE INDEX (`id-and-date`)
                  INNER JOIN stocks.stock USE INDEX(`stockid`)
                ON `stock-id` = stocks.stock.`id` 
                  AND stocks.stock.`stock` = %(stock)s
                    AND `stocks`.`data`.`date` >= DATE(%(bdate)s)
                    AND `stocks`.`data`.`date` <= DATE(%(edate)s)
                   INNER JOIN stocks.`study-data` USE INDEX (`ids`)
                    ON
                    stocks.stock.`id` = stocks.`study-data`.`stock-id`
                    AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`
                    AND stocks.`study-data`.`study-id` = %(id)s 
                    ORDER BY stocks.`data`.`date` ASC
                    """
                try:
                    check_cache_studies_db_result = self.ema_cnx.execute(check_cache_studies_db_stmt,{'stock':self.indicator.upper(),    
                                                                                    'bdate':self.data["Date"].iloc[0].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[0],datetime.datetime) else self.data["Date"].iloc[0],
                                                                                    'edate':self.data["Date"].iloc[-1].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[-1],datetime.datetime) else self.data["Date"].iloc[-1],
                                                                                    'id': self.study_id},multi=True)
                    # Retrieve date, verify it is in date range, remove from date range
                    for res in check_cache_studies_db_result:
                        res= res.fetchall()
                        # Convert datetime to str
                        for r in res:
                            try:
                                date=datetime.date.strftime(r[0],"%Y-%m-%d")
                            except Exception as e:
                                print(f'[ERROR] No date found for study element!\nException:\n{str(e)}')
                                continue
                            if date is None:
                                print(f'[INFO] Not enough prior ema{length} found for {self.indicator.upper()} from {self.data["Date"].iloc[0]} to {self.data["Date"].iloc[-1]}... Generating ema{length} data...!\n',flush=True)
                                break
                            else:
                                # check if date is there, if not fail this
                                if date in date_range:
                                    study_data = study_data.append({f'ema{length}':r[1]},
                                                                    ignore_index=True)
                                    date_range.remove(date)                                 
                                else:
                                    # print(f'[INFO] Skipping date removal for {date}')
                                    continue
                except mysql.connector.errors.IntegrityError: # should not happen
                    self.ema_cnx.close()
                    pass
                except Exception as e:
                    print('[ERROR] Failed to check for cached ema-data element!\nException:\n',str(e))
                    self.ema_cnx.close()
                    raise mysql.connector.errors.DatabaseError()
                if len(date_range) == 0 and not self._force_generate: # continue loop if found cached data
                    self.applied_studies=pd.concat([self.applied_studies,study_data])
                    continue
                # Insert data into db if query above is not met
                else:
                    if not self._force_generate:
                        print(f'[INFO] Did not query all specified dates within range for ema!  Remaining {date_range}')
                    
                    # Calculate locally, then push to database
                    with threading.Lock():
                        try:
                            data = self.data.copy().drop(['Date'],axis=1)
                        except:
                            pass
                        data = data.copy().drop(['Open','High','Low','Adj Close'],axis=1).rename(columns={'Close':f'ema{length}'}).ewm(alpha=2/(int(length)+1),adjust=True).mean()
                        self.applied_studies= pd.concat([self.applied_studies,data],axis=1)
                        del data
                        gc.collect()
                   
                    try:
                        self.ema_cnx.close()
                    except:
                        pass
                    # Calculate and store data to DB ...   
                    try: # Try connection to db_con, if not, connect to 
                        self.ema_cnx = self.db_con.cursor()
                    except:
                        self.ema_cnx = self.db_con2.cursor()
                    self.ema_cnx.autocommit = True
                    # Retrieve the stock-id, and data-point id in a single select statement
                    retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`,
                     `stocks`.`data`.`stock-id` FROM `stocks`.`data` USE INDEX (`id-and-date`)
                    INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`
                     AND `stocks`.`data`.`date`>= DATE(%(bdate)s) 
                     AND `stocks`.`data`.`date`<= DATE(%(edate)s)
                     ORDER BY stocks.`data`.`date` ASC 
                    """
                    retrieve_data_result = self.ema_cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                                'bdate':self.data["Date"].iloc[0].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[0],datetime.datetime) else self.data["Date"].iloc[0],
                                                                                'edate':self.data["Date"].iloc[-1].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[-1],datetime.datetime) else self.data["Date"].iloc[-1]},multi=True)
                    self.stock_ids=[]
                    self.data_ids=[]
                    for retrieve_result in retrieve_data_result:
                        id_res = retrieve_result.fetchall()
                        for res in id_res:
                            if len(res) == 0:
                                print(f'[ERROR] Failed to locate a data id under {retrieve_data_result}')
                                raise Exception()
                            else:
                                try:
                                    self.stock_ids.append(res[1].decode('latin1'))
                                    self.data_ids.append(res[0].decode('latin1'))
                                except Exception as e:
                                    print(f'[ERROR] failed to query stock id/data_id for ema insert!\nException:\n{str(e)}')
                    # Execute insert for study-data
                    insert_studies_db_stmt = "REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`) VALUES (%s,%s,%s,%s,%s)"        
                    
                    insert_list=[]
                    for index,id in self.data.iterrows():
                        emastr=f'ema{length}'
                        insert_tuple=(f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}{length}",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}{length}",512)))',
                        f'{self.stock_ids[index]}',
                        f'{self.data_ids[index]}',
                        f'{self.study_id}',
                        self.applied_studies[emastr].iloc[index])
                        insert_list.append(insert_tuple) # add tuple to list
                    # Call execution statement to insert data in one shot
                    try:
                        # print(insert_studies_db_stmt)
                        insert_studies_db_result = self.ema_cnx.executemany(insert_studies_db_stmt,insert_list)
                        self.db_con.commit()
                    except mysql.connector.errors.IntegrityError:
                        print('[ERROR] Integrity Error')
                        self.ema_cnx.close()
                        pass
                    except TypeError as e:
                        print(f'[ERROR] TypeError!\nException:\n{str(e)}')
                    except ValueError as e:
                        print(f'[ERROR] ValueError!\nException:\n{str(e)}')
                    except Exception as e:
                        print('[ERROR] Failed to insert ema-data element!\nException:\n',str(e))
                        self.ema_cnx.close()
                        pass
        self.ema_cnx.close()
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
        self.fib_cnx = self.db_con.cursor()
        self.fib_cnx.autocommit = True
        # print('[INFO] Select stock')
        resultado = self.fib_cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.fib_cnx.execute(select_study_stmt, { 'study': f'fibonacci'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named fibonacci from database! Creating new Study...\n')
                        insert_study_stmt = """REPLACE INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(fib)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.fib_cnx.execute(insert_study_stmt,{'id':f'fibonacci',
                                                                            'fib':f'fibonacci'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                            retrieve_study_id_result = self.fib_cnx.execute(retrieve_study_id_stmt,{'study':f'fibonacci'},multi=True)
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
        try:
            self.fib_cnx.close()
        except:
            pass
        self.fib_cnx = self.db_con.cursor()
        self.fib_cnx.autocommit = True
        # Retrieve the stock-id, and data-point id in a single select statement
        retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`, `stocks`.`data`.`stock-id`
         FROM `stocks`.`data` USE INDEX (`id-and-date`)
        INNER JOIN `stocks`.`stock` USE INDEX (`stockid`) ON `stocks`.stock.stock = %(stock)s
         AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`
          AND `stocks`.`data`.`date` >= DATE(%(bdate)s) 
          AND `stocks`.`data`.`date` <= DATE(%(edate)s) 
        """
        retrieve_data_result = self.fib_cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                    'bdate':self.data["Date"].iloc[0].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[0],datetime.datetime) else self.data["Date"].iloc[0],
                                                                    'edate':self.data["Date"].iloc[-1].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[-1],datetime.datetime) else self.data["Date"].iloc[-1]},
                                                                    multi=True)
        self.stock_ids=[]
        self.data_ids=[]
        # self.data=self.data.drop(['Date'],axis=1)
        for retrieve_result in retrieve_data_result:
            id_res = retrieve_result.fetchall()
            if len(id_res) == 0:
                print(f'[INFO] Failed to locate any data-ids/stock-ids from {self.data["Date"].iloc[0].strftime("%Y-%m-%d")} to {self.data["Date"].iloc[-1].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                break
            else:
                for res in id_res:
                    try:
                        self.stock_ids.append(res[1].decode('latin1'))
                        self.data_ids.append(res[0].decode('latin1'))
                    except Exception as e:
                        print(f'[ERROR] Failed to grab stock id/data id for {self.indicator} for fib retrieval!\nException:\n{str(e)}')
                        break
                    
        # Before inserting data, check cached data, verify if there is data there...
        check_cache_studies_db_stmt = """SELECT `stocks`.`data`.`date`,
        `stocks`.`study-data`.`val1`,`stocks`.`study-data`.`val2`,
        `stocks`.`study-data`.`val3`,`stocks`.`study-data`.`val4`,
        `stocks`.`study-data`.`val5`,`stocks`.`study-data`.`val6`,
        `stocks`.`study-data`.`val7`,`stocks`.`study-data`.`val8`,
        `stocks`.`study-data`.`val9`,`stocks`.`study-data`.`val10`,
        `stocks`.`study-data`.`val11`,`stocks`.`study-data`.`val12`,
        `stocks`.`study-data`.`val13`,`stocks`.`study-data`.`val14` 
         FROM stocks.`data` USE INDEX (`id-and-date`) INNER JOIN stocks.stock 
        ON `stocks`.`data`.`stock-id` = stocks.stock.`id` 
          AND stocks.stock.`stock` = %(stock)s
           AND `stocks`.`data`.`date` >= DATE(%(bdate)s)
           AND `stocks`.`data`.`date` <= DATE(%(edate)s)
           INNER JOIN stocks.`study-data` USE INDEX (`ids`) ON
            stocks.stock.`id` = stocks.`study-data`.`stock-id`
            AND stocks.`study-data`.`data-id` = stocks.`data`.`data-id`
            AND stocks.`study-data`.`study-id` = %(id)s ORDER BY stocks.`data`.`date` ASC
            """

        try:
            check_cache_studies_db_result = self.fib_cnx.execute(check_cache_studies_db_stmt,{'stock':self.indicator.upper(),    
                                                                            'bdate':self.data["Date"].iloc[0].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[0],datetime.datetime) else self.data["Date"].iloc[0],
                                                                            'edate':self.data["Date"].iloc[-1].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[-1],datetime.datetime) else self.data["Date"].iloc[-1],
                                                                            'id': self.study_id},multi=True)
            # Retrieve date, verify it is in date range, remove from date range
            for res in check_cache_studies_db_result:
                # print(str(res.statement))
                res= res.fetchall()
                for r in res:
                    # Convert datetime to str
                    try:
                        date=datetime.date.strftime(r[0],"%Y-%m-%d")
                    except Exception as e:
                        print(f'[ERROR] Could not find a date for fib data for {self.indicator.upper()}!\nException:\n{str(e)}')
                        continue
                    if date is None:
                        print(f'[INFO] Not enough fib data found for {self.indicator.upper()}... Creating fib data...!\n',flush=True)
                        break
                    else:
                        # check if date is there, if not fail this
                        if date in date_range:
                            date_range.remove(date)
                            fib_data = fib_data.append({'0.202':r[1],'0.236':r[2],
                                                        '0.241':r[3],'0.273':r[4],
                                                        '0.283':r[5],'0.316':r[6],
                                                        '0.382':r[7],'0.5':r[8],
                                                        '0.618':r[9],'0.796':r[10],
                                                        '1.556':r[11],'3.43':r[12],
                                                        '3.83':r[13],'5.44':r[14]},
                                                        ignore_index=True)
                            
                        else:
                            continue
        except mysql.connector.errors.IntegrityError: # should not happen
            self.fib_cnx.close()
            print('[ERROR] Integrity Error!')
            pass
        except Exception as e:
            print('[ERROR] Failed to check for cached fib-data element!\nException:\n',str(e))
            self.fib_cnx.close()
            raise mysql.connector.errors.DatabaseError()
        if len(date_range) == 0 and not self._force_generate: # continue loop if found cached data
            self.fibonacci_extension=fib_data
        else:
            if not self._force_generate:
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
                for i,row in new_set['Vals'].iloc[int(len(new_set.index)/3):].iteritems(): # val 1 
                    if i != 0:
                        # if the first value is lower than the close , do upwards fib, else downwards
                        if new_set.at[0,'Vals'] < new_set.at[len(new_set.index)-1,'Vals']:
                            # attempt upwards fib
                            try:
                                if row < float(new_set.at[i - 1,'Vals']) and not float(new_set.at[i + 1,'Vals']) < row : # if low is found, jump to this value
                                    val1 =  row
                                    # find val2 by finding next local high
                                    for j,sub in new_set['Vals'].iloc[int(len(new_set.index)/3):].iteritems():
                                        if j < i:
                                            continue
                                        else: # find val2 by making sure next local high is valid
                                            if sub > float(new_set.at[j + 1,'Vals']) and not float(new_set.at[j - 1,'Vals']) > sub:
                                                val2 = sub
                                                # find val3 by getting next low
                                                for k,low in new_set['Vals'].iloc[int(len(new_set.index)/3):].iteritems():
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
                                print(f'[ERROR] Failed upwards fib!  This could be due to not finding a higher low...\nException:\n{str(e)}',flush=True)  
                        else:
                            # attempt downwards fib
                            try:
                                if row > float(new_set.at[i - 1,'Vals']) and not float(new_set.at[i + 1,'Vals']) > row : # if low is found, jump to this value
                                    val1 =  row
                                    # find val2 by finding next local high
                                    for j,sub in new_set['Vals'].iloc[int(len(new_set.index)/3):].iteritems():
                                        if j < i:
                                            continue
                                        else: # find val2 by making sure next local low is valid
                                            if sub < float(new_set.at[j + 1,'Vals']) and not float(new_set.at[j - 1,'Vals']) < sub:
                                                val2 = sub
                                                # find val3 by getting next high
                                                for k,low in new_set['Vals'].iloc[int(len(new_set.index)/3):].iteritems():
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
                # Insert data if not in db...
                insert_studies_db_stmt = """REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,
                                            `val2`,`val3`,`val4`,`val5`,`val6`,`val7`,`val8`,`val9`,`val10`,`val11`,`val12`,`val13`,`val14`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                insert_list=[]
                self.fibonacci_extension= self.fibonacci_extension.reset_index()
                for index,row in self.data.iterrows():

                    insert_tuple=(f'AES_ENCRYPT("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}fibonacci",UNHEX(SHA2("{self.data["Date"].iloc[index].strftime("%Y-%m-%d")}{self.indicator.upper()}fibonacci",512)))',
                    f'{self.stock_ids[index]}',
                    f'{self.data_ids[index]}',
                    f'{self.study_id}',
                    self.fibonacci_extension.at[0,"0.202"],
                    self.fibonacci_extension.at[0,"0.236"],
                    self.fibonacci_extension.at[0,"0.241"],
                    self.fibonacci_extension.at[0,"0.273"],
                    self.fibonacci_extension.at[0,"0.283"],
                    self.fibonacci_extension.at[0,"0.316"],
                    self.fibonacci_extension.at[0,"0.382"],
                    self.fibonacci_extension.at[0,"0.5"],
                    self.fibonacci_extension.at[0,"0.618"],
                    self.fibonacci_extension.at[0,"0.796"],
                    self.fibonacci_extension.at[0,"1.556"],
                    self.fibonacci_extension.at[0,"3.43"],
                    self.fibonacci_extension.at[0,"3.83"],
                    self.fibonacci_extension.at[0,"5.44"])
                    insert_list.append(insert_tuple) # add tuple to list
                try:
                    # print(type(self.stock_id),type(self.data_id),type(self.study_id),row['ema14'])
                    insert_studies_db_result = self.fib_cnx.executemany(insert_studies_db_stmt,insert_list)
                
                except mysql.connector.errors.IntegrityError:
                    self.fib_cnx.close()
                    pass
                except Exception as e:
                    print('[ERROR] Failed to insert study-data element fibonacci!\nException:\n',str(e))
                    self.fib_cnx.close()
                    pass
                try:
                    self.db_con.commit()
                except mysql.connector.errors.IntegrityError:
                    self.fib_cnx.close()
                    pass
                except Exception as e:
                    print('[ERROR] Failed to insert fib-data element fibonacci!\nException:\n',str(e))
                    self.fib_cnx.close()
                    pass
    
                                
        self.fib_cnx.close()
        return 0
    
    
    
    
    
    
    
    
    
    
    ''' Keltner Channels for display data'''
    def keltner_channels(self,length:int,factor:int=2,displace:int=None):
        with threading.Lock():
            self.data_cp = self.data.copy()
            # self.data_cp=self.data_cp.reset_index()
            self.apply_ema(length,length) # apply length ema for middle band
            self.keltner = pd.DataFrame({'middle':[],'upper':[],'lower':[]},dtype=float)
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
            for index,row in self.data_cp.iterrows():
                if index == 0 or index <= length or index == len(self.data_cp.index)-1:
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
                    if index == len(self.data_cp.index) - 1: # if last element
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
                except Exception as e:
                    raise Exception("[Error] Failed to calculate Keltner...\n",str(e))
            """
                    MYSQL Portion...
                    Store Data on DB...
            """
        # Retrieve query from database, confirm that stock is in database, else make new query
        select_stmt = "SELECT stock FROM stocks.stock WHERE stock like %(stock)s"
        try:
            self.kelt_cnx = self.db_con.cursor()
        except:
            self.kelt_cnx = self.db_con2.cursor()
        self.kelt_cnx.autocommit = True
        # print('[INFO] Select stock')
        resultado = self.kelt_cnx.execute(select_stmt, { 'stock': self.indicator.upper()},multi=True)
        for result in resultado:
            # Query new stock, id
            if len(result.fetchall()) == 0:
                print(f'[ERROR] Failed to query stock named {self.indicator.upper()} from database!\n')
                raise mysql.connector.Error
            else:
                select_study_stmt = "SELECT `study-id` FROM stocks.study WHERE study like %(study)s"
                # print('[INFO] Select study id')
                study_result = self.kelt_cnx.execute(select_study_stmt, { 'study': f'keltner{length}-{factor}'},multi=True)
                for s_res in study_result:
                    # Non existent DB value
                    study_id_res = s_res.fetchall()
                    if len(study_id_res) == 0:
                        print(f'[INFO] Failed to query study named keltner{length}-{factor} from database! Creating new Study...\n')
                        insert_study_stmt = """INSERT INTO stocks.study (`study-id`,study) 
                            VALUES (AES_ENCRYPT(%(id)s, %(id)s),%(keltner)s)"""
                        # Insert new study into DB
                        try:
                            insert_result = self.kelt_cnx.execute(insert_study_stmt,{'id':f'keltner{length}{factor}',
                                                                            'keltner':f'keltner{length}-{factor}'},multi=True)
                            self.db_con.commit()
                            
                            # Now get the id from the db
                            retrieve_study_id_stmt = """ SELECT `study-id` FROM stocks.study WHERE `study` like %(study)s"""
                            retrieve_study_id_result = self.kelt_cnx.execute(retrieve_study_id_stmt,{'study':f'keltner{length}-{factor}'},multi=True)
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
            
        # Retrieve the stock-id, and data-point id in a single select statement
        try:
            self.kelt_cnx.close()
        except:
            pass 
        try:
            self.kelt_cnx = self.db_con.cursor()
        except:
            self.kelt_cnx = self.db_con2.cursor()
        self.kelt_cnx.autocommit = True
        retrieve_data_stmt = """SELECT `stocks`.`data`.`data-id`,
         `stocks`.`data`.`stock-id` FROM `stocks`.`data` USE INDEX (`id-and-date`)
        INNER JOIN `stocks`.`stock`
         ON `stocks`.stock.stock = %(stock)s
          AND `stocks`.`stock`.`id` = `stocks`.`data`.`stock-id`
           AND `stocks`.`data`.`date`>= DATE(%(bdate)s) 
           AND `stocks`.`data`.`date`<= DATE(%(edate)s) 
           ORDER BY stocks.`data`.`date` ASC
        """
        retrieve_data_result = self.kelt_cnx.execute(retrieve_data_stmt,{'stock':f'{self.indicator.upper()}',
                                                                        'bdate':self.data["Date"].iloc[0].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[0],datetime.datetime) else self.data["Date"].iloc[0],
                                                                        'edate':self.data["Date"].iloc[-1].strftime('%Y-%m-%d') if isinstance(self.data["Date"].iloc[-1],datetime.datetime) else self.data["Date"].iloc[-1]},
                                                                        multi=True)
        self.stock_ids=[]
        self.data_ids=[]
        # self.data=self.data.drop(['Date'],axis=1)
        for retrieve_result in retrieve_data_result:
            id_res = retrieve_result.fetchall()
            if len(id_res) == 0:
                print(f'[ERROR] Failed to locate a data-id for current index {index} with date {self.data_cp.loc[index,:]["Date"].strftime("%Y-%m-%d")} under {retrieve_data_result}')
                raise Exception('[ERROR] Failed to locate a data-id when parsing keltner data!')
            else:
                for res in id_res:
                    self.stock_ids.append(res[1].decode('latin1'))
                    self.data_ids.append(res[0].decode('latin1'))
                        # Execute insert for study-data
        insert_studies_db_stmt = """REPLACE INTO `stocks`.`study-data` (`id`, `stock-id`, `data-id`,`study-id`,`val1`,`val2`,`val3`) 
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """
        insert_list=[]
        for index,row in self.keltner.iterrows():
            insert_tuple=(f'AES_ENCRYPT("{self.data_cp.loc[index,:]["Date"].strftime("%Y-%m-%d")}{self.indicator}keltner{length}{factor}", UNHEX(SHA2("{self.data_cp.loc[index,:]["Date"].strftime("%Y-%m-%d")}{self.indicator}keltner{length}{factor}",512)))',
            f'{self.stock_ids[index]}',
            f'{self.data_ids[index]}',
            f'{self.study_id}',
            row["middle"].values[0],
            row["upper"].values[0],
            row["lower"].values[0])
            insert_list.append(insert_tuple)
        try:
            insert_studies_db_result = self.kelt_cnx.executemany(insert_studies_db_stmt,insert_list)
            self.db_con.commit()
        except mysql.connector.errors.IntegrityError:
            self.kelt_cnx.close()
            pass
        except Exception as e:
            print(f'[ERROR] Failed to insert study-data element keltner{length}{factor} !\nException:',str(e))
            self.kelt_cnx.close()
            pass
        self.kelt_cnx.close()
        return 0
    def reset_data(self):
        self.applied_studies = pd.DataFrame()
    #append to specified struct
    def append_data(self,struct:pd.DataFrame,label:str,val):
        struct = struct.append({label:val},ignore_index=True)
        return struct
    

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