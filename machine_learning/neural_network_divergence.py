import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
import pandas as pd
import threading
from machine_learning.neural_framework import Neural_Framework
import pandas as pd
from pathlib import Path
from mysql.connector import errorcode
import binascii
import uuid
import mysql.connector
import xml.etree.ElementTree as ET
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar



class Neural_Divergence(Neural_Framework):
    def __init__(self,epochs,batch_size):
        super().__init__(epochs, batch_size)
        self.model_map_names = {1:"divergence",2:"divergence_2",3:"divergence_3",4:"divergence_4"} # model is sigmoid tan function combo, model_new_2 is original relu leakyrelu combo, model_new_3 is tanh sigmoid combo
    def create_model(self):
        self.nn_input = keras.Input(shape=(1,1,28)) # 14 * 8 cols
        self.nn = keras.layers.Dense(28, activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
        self.nn = keras.layers.Dropout(0.1)(self.nn)
        keras.regularizers.l1(0.01)
        keras.regularizers.l2(0.02)
        self.nn = keras.layers.Dense(12,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
        self.nn2 = keras.layers.Dense(2,activation='tanh')(self.nn)
        self.nn = keras.Model(inputs=self.nn_input,outputs=[self.nn2])
        self.nn.compile(optimizer=keras.optimizers.Adam(lr=0.005,beta_1=0.9,beta_2=0.999), loss='mae',metrics=['MeanAbsoluteError'])
        return self.nn   
    def run_model(self):
        sampler = Sample()
        models = {}
        # Retrieve all necessary data into training data
        for i in range(1,self.EPOCHS):
            print(f'\n\n\nEPOCH {i}\n\n\n')
            train= []
            train_targets=[]
            models[i] = 1
            for j in range(1,self.BATCHES):
                train= []
                train_targets=[]
                try:
                    print(sampler.generate_sample())
                    # sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)
                except:
                    continue
                try:
                    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,28)))# Retrieve all except for last data to be analyzed/predicted
                    train_targets.append(np.reshape(sampler.normalizer.normalized_data.iloc[-1:].to_numpy(),(1,2)))
                except:
                    continue
                disp = self.nn.train_on_batch(np.stack(train), np.stack(train_targets))
                model_info = {'model' : self.nn, 'history' : disp[1], 'loss' : disp[0]}
                models[i] = (model_info['loss'] + models[i] )
                try:
                    self.nn.evaluate(np.stack(train),np.stack(train_targets))
                except:
                    continue
            models[i] = models[i] / self.BATCHES
                # print(f'{self.nn.predict(np.stack(train))}\n{np.stack(train_targets)}')
            self.save_model()

        return models
    def save_model(self):
        self.nn.save(f'{self.path}/data/divergence')
    def load_model(self):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/divergence')
        except:
            print("No model exists, creating new model...")
listLock = threading.Lock()
def load_divergence(ticker:str=None,has_actuals:bool=False,force_generation=False,device_opt='/device:CPU:0'):        
    # Connect to local DB
    path=Path(os.getcwd()).parent.absolute()
    tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(path))
    root = tree.getroot()
    try:
        db_con = mysql.connector.connect(
          host="127.0.0.1",
          user=root[0].text,
          password=root[1].text,
          raise_on_warnings = True,
          database='stocks',
          charset = 'latin1'
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
            
    cnx = db_con.cursor(buffered=True)

    
    # Before inserting data, check cached data, verify if there is data there...
    from_date_id=None
    to_date_id=None
    stock_id=None
    predicted=None
    
    # First, get to date id
    check_cache_tdata_db_stmt = """SELECT `stocks`.`data`.`data-id`,`stocks`.`data`.`stock-id` 
     FROM stocks.`data` INNER JOIN stocks.`stock`
     ON stocks.`data`.`stock-id` = stocks.`stock`.`id` 
       AND `stocks`.`stock`.`stock` = %(stock)s
       AND stocks.`data`.`date` = DATE(%(date)s)
        """
    # check if currently weekend/holiday
    valid_datetime=datetime.datetime.today()
    holidays=USFederalHolidayCalendar().holidays(start=valid_datetime,end=(valid_datetime + datetime.timedelta(days=7))).to_pydatetime()
    valid_date=valid_datetime.date()
    if datetime.datetime.utcnow().hour < 13: # if current time is before 9:30 AM EST, go back a day
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date in holidays and valid_date.weekday() >= 0 and valid_date.weekday() <= 4: #week day holiday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday()==5: # if saturday
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if valid_date.weekday()==6: # if sunday
        valid_datetime = (valid_datetime - datetime.timedelta(days=2))
        valid_date = (valid_date - datetime.timedelta(days=2))

    retrieve_tdata_result = cnx.execute(check_cache_tdata_db_stmt,{'stock':f'{ticker.upper()}',
                                                            'date':valid_datetime.strftime('%Y-%m-%d')},multi=True)
    
    for retrieve_result in retrieve_tdata_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            if not force_generation:
                print(f'[INFO] Failed to locate a to data-id and stock-id for {ticker} on {valid_datetime.strftime("%Y-%m-%d")}')
            break
        else:
            stock_id = id_res[0][1].decode('latin1')
            to_date_id = id_res[0][0].decode('latin1')

    
    # Check nn-data table after retrieval of from-date and to-date id's
    check_cache_fdata_db_stmt = """SELECT `stocks`.`data`.`data-id` 
     FROM stocks.`data` 
     WHERE stocks.`data`.`stock-id` = %(stock-id)s
       AND stocks.`data`.`date` = DATE(%(date)s)
        """
    # 75 days ago max -- check if weekday or holiday before proceeding
    valid_datetime=datetime.datetime.today() - datetime.timedelta(days=75)
    holidays=USFederalHolidayCalendar().holidays(start=valid_datetime,end=(valid_datetime + datetime.timedelta(days=7)).strftime('%Y-%m-%d')).to_pydatetime()
    valid_date=valid_datetime.date()
    if valid_date in holidays:
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))
    if valid_date.weekday()==5: # if saturday
        valid_datetime = (valid_datetime + datetime.timedelta(days=2))
        valid_date = (valid_date + datetime.timedelta(days=2))
    if valid_date.weekday()==6: # if sunday
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))
    if valid_date in holidays and valid_date.weekday()==0: # if monday and a holiday
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))


    retrieve_data_result = cnx.execute(check_cache_fdata_db_stmt,{'stock-id':stock_id,
                                    'date':valid_date},multi=True)
    for retrieve_result in retrieve_data_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            if not force_generation:
                print(f'[INFO] Failed to locate a from data-id  for {ticker} on {valid_datetime.strftime("%Y-%m-%d")}')
            break
        else:
            from_date_id = id_res[0][0].decode('latin1')
        
        
    # Check nn-data table after retrieval of from-date and to-date id's
    check_cache_nn_db_stmt = """SELECT `stocks`.`nn-data`.`open`,`stocks`.`nn-data`.`close`,
    `stocks`.`nn-data`.`range` 
     FROM stocks.`nn-data` WHERE
    `stock-id` = %(stock-id)s
       AND `stocks`.`nn-data`.`from-date-id` = %(from-date-id)s
       AND `stocks`.`nn-data`.`to-date-id` = %(to-date-id)s
        AND `stocks`.`nn-data`.`model` = %(model)s

        """        
    try:
        check_cache_studies_db_result = cnx.execute(check_cache_nn_db_stmt,{'stock-id':stock_id,    
                                                                        'from-date-id': from_date_id,
                                                                        'to-date-id':to_date_id,
                                                                        'model':'divergence'},
                                                                        multi=True)
        # Retrieve date, verify it is in date range, remove from date range
        for result in check_cache_studies_db_result:   
            result= result.fetchall()
            for res in result:        
                # Set predicted value
                predicted = pd.DataFrame({'Open':float(res[0]),'Close':float(res[1]),'Range':float(res[2])},index=[0]) 
    except mysql.connector.errors.IntegrityError: # should not happen
        cnx.close()
        pass
    except Exception as e:
        print('[ERROR] Failed to check cached nn-data!\nException:\n',str(e))
        cnx.close()
        raise mysql.connector.errors.DatabaseError()
        
    
    sampler = Sample(ticker)
    train = []
    sampler.generate_divergence_sample(False,has_actuals)
    
    if predicted is None:
        neural_net = Neural_Divergence(0,0)
        neural_net.load_model()
    
        with listLock:
            if has_actuals:
                train.append(np.reshape(sampler.normalizer.normalized_data.iloc[-15:-1].to_numpy(),(1,1,28)))
            else:
                train.append(np.reshape(sampler.normalizer.normalized_data[-14:].to_numpy(),(1,1,28)))
            prediction = neural_net.nn.predict(np.stack(train))
        predicted = pd.DataFrame((np.reshape((prediction),(1,2))),columns=['Divergence','Gain/Loss']) #NORMALIZED
    return (sampler.normalizer.unnormalize_divergence(predicted),sampler.normalizer.unnormalized_data.iloc[-1:],sampler.normalizer.keltner,sampler.normalizer.fib)
def run(epochs,batch_size):
    neural_net = Neural_Divergence(epochs,batch_size)
    neural_net.load_model()
    neural_net.create_model()
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
# run(50,100)
# run(30,100)
# run(80,100)
# run(80,100)

# print(load_divergence("spy/2021-05-26--2021-07-16_data",name='divergence_3',has_actuals=True))
