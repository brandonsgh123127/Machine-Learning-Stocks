import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import threading
from machine_learning.neural_framework import Neural_Framework
from pandas.tseries.holiday import USFederalHolidayCalendar
from pathlib import Path
from mysql.connector import errorcode
import mysql.connector
import xml.etree.ElementTree as ET
import datetime
import random

class Network(Neural_Framework):
    def __init__(self,epochs,batch_size):
        super().__init__(epochs, batch_size)
        self.model_map_names = {"model_relu":1,"model_leaky":2,"model_sigmoid":3,"model_relu2":4,"model_leaky2":5,
                                "model_sigmoid2":6}
        self.model_choice:int = None

    def get_mapping(self,choice:int):
        return self.model_map_names.keys()[self.model_map_names.values().index(choice)]
    def create_model(self,model_choice="model_relu"):
        self.model_name = model_choice
        self.model_choice = self.model_map_names.get(model_choice)
        self.nn_input = keras.Input(shape=(1,1,140)) # 14 * 10 cols
        # Relu Model
        if self.model_choice == 1:
            self.nn = keras.layers.Dense(140, activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            # self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.09)
            keras.regularizers.l2(0.1)
            self.nn = keras.layers.Dense(48,activation='relu',kernel_initializer=tf.keras.initializers.GlorotUniform())(self.nn)
            self.nn = keras.layers.Dense(48,activation='relu')(self.nn)
            self.nn = keras.layers.Dropout(0.5)(self.nn)
            self.nn = keras.layers.Dense(24,activation='relu')(self.nn)
            self.nn2 = keras.layers.Dense(10,activation='linear')(self.nn)
        #  Leaky Relu no Dropout
        elif self.model_choice == 2:
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.74))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(10,activation='linear')(self.nn)
        # Sigmoid 
        elif self.model_choice == 3:
            self.nn = keras.layers.Dense(140, activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            # self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(56,activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.5)(self.nn) # Residual layer
            self.nn = keras.layers.Dense(48,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dense(20,activation='sigmoid')(self.nn)
            self.nn2 = keras.layers.Dense(10,activation='linear')(self.nn)        
        # Relu - Out 3
        elif self.model_choice == 4:
            self.nn = keras.layers.Dense(140, activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            keras.regularizers.l1(0.02 )
            keras.regularizers.l2(0.07)
            self.nn = keras.layers.Dense(48,activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.5)(self.nn)
            self.nn2 = keras.layers.Dense(3,activation='linear')(self.nn)
        # Leaky Relu - Out 3
        elif self.model_choice == 5:
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(3,activation='linear')(self.nn)
        # Sigmoid - Out 3
        elif self.model_choice == 6:
            self.nn = keras.layers.Dense(140, activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dense(140, activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.6)(self.nn) # Residual
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(8,activation='sigmoid')(self.nn)
            self.nn2 = keras.layers.Dense(3,activation='linear')(self.nn)
        self.nn = keras.Model(inputs=self.nn_input,outputs=[self.nn2])
        self.nn.compile(optimizer=keras.optimizers.Adam(lr=0.0005,beta_1=0.95,beta_2=0.999), loss='mse',metrics=['MeanAbsoluteError','MeanAbsolutePercentageError'])
        return self.nn
    
    def generate_sample(self,_has_actuals=False,rand_date=None):
        path = Path(os.getcwd()).parent.absolute()
        self.sampler.set_ticker(self.choose_random_ticker(f'{path}/data/watchlist/default.csv'))
        try:
            if self.model_choice < 4:
                self.sampler.generate_sample(_has_actuals=_has_actuals,rand_date=rand_date)
            else:
                self.sampler.generate_sample(_has_actuals=_has_actuals,out=2,rand_date=rand_date)
            self.sampler.data = self.sampler.data.drop(['High','Low'],axis=1)
        except Exception as e:
            print('[Error] Failed batch!\nException:\n',str(e))
            raise Exception()
        except Exception as e:
            print(str(e))
            raise Exception()

    def run_model(self,rand_date=False):
        self.sampler = Sample()
        models = {}
        # Retrieve all necessary data into training data
        for i in range(1,self.EPOCHS):
            print(f'\n\n\nEPOCH {i} -- {self.model_choice}')
            train= []
            train_targets=[]
            models[i] = 1
            for j in range(1,self.BATCHES):
                train= []
                train_targets=[]
                self.generate_sample(True, rand_date)
                try:
                    train.append(np.reshape(self.sampler.normalized_data.iloc[:-1].to_numpy(),(1,1,140)))# Retrieve all except for last data to be analyzed/predicted
                    if self.model_choice <= 3:
                        train_targets.append(np.reshape(self.sampler.normalized_data.iloc[-1:].to_numpy(),(1,10)))
                    else:
                        tmp = self.sampler.normalized_data.iloc[-1:]
                        tmp = pd.concat([pd.DataFrame([tmp['Open'].to_numpy()]),pd.DataFrame([tmp['Close'].to_numpy()]),pd.DataFrame([tmp['Range'].to_numpy()])])
                        train_targets.append(np.reshape(tmp.to_numpy(),(1,3)))
                except Exception as e:
                    print('[ERROR] Failed to specify train_target value!\nException:\n',str(e))
                    continue
                disp = self.nn.train_on_batch(np.stack(train), np.stack(train_targets))
                model_info = {'model' : self.nn, 'history' : disp[1], 'loss' : disp[0]}
                models[i] = (model_info['loss'] + models[i] )
                try:
                    self.nn.evaluate(np.stack(train),np.stack(train_targets),verbose=1)
                    # print(f'loss : {loss}\t accuracy : {acc}')
                except:
                    print('[ERROR] Could not evaluate model')
                    continue
            models[i] = models[i] / self.BATCHES
            self.save_model()

        return models
    def save_model(self):
        self.nn.save(f'{self.path}/data/{self.model_name}')
    def load_model(self,name="model_relu"):
        self.model_choice = self.model_map_names.get(name)
        super().load_model(name)
listLock = threading.Lock()

def check_db_cache(cnx:mysql.connector.connect=None,ticker:str=None,has_actuals:bool=False,name:str="model_relu",force_generation:bool=False):    
    # Before inserting data, check cached data, verify if there is data there...
    from_date_id=None
    to_date_id=None
    stock_id=None
        
    # First, get to date id
    check_cache_tdata_db_stmt = """SELECT `stocks`.`data`.`data-id`,`stocks`.`data`.`stock-id` 
     FROM stocks.`data` USE INDEX (`id-and-date`) INNER JOIN stocks.`stock`
     ON stocks.`data`.`stock-id` = stocks.`stock`.`id` 
       AND `stocks`.`stock`.`stock` = %(stock)s
       AND stocks.`data`.`date` = DATE(%(date)s)
        """
    # check if currently weekend/holiday
    valid_datetime=datetime.datetime.utcnow()
    holidays=USFederalHolidayCalendar().holidays(start=valid_datetime,end=(valid_datetime + datetime.timedelta(days=7))).to_pydatetime()
    valid_date=valid_datetime.date()
    if (datetime.datetime.utcnow().hour <= 14 and datetime.datetime.utcnow().minute < 30): # if current time is before 9:30 AM EST, go back a day
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
    if valid_date in holidays:
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
    if has_actuals: # go back a day
        valid_datetime = (valid_datetime - datetime.timedelta(days=1))
        valid_date = (valid_date - datetime.timedelta(days=1))
        if valid_date.weekday()==5: # if saturday
            valid_datetime = (valid_datetime - datetime.timedelta(days=1))
            valid_date = (valid_date - datetime.timedelta(days=1))
        if valid_date.weekday()==6: # if sunday
            valid_datetime = (valid_datetime - datetime.timedelta(days=2))
            valid_date = (valid_date - datetime.timedelta(days=2))
        if valid_date in holidays:
            valid_datetime = (valid_datetime - datetime.timedelta(days=1))
            valid_date = (valid_date - datetime.timedelta(days=1))

    retrieve_tdata_result = cnx.execute(check_cache_tdata_db_stmt,{'stock':f'{ticker.upper()}',
                                                            'date':valid_datetime.strftime('%Y-%m-%d')},multi=True)
    
    for retrieve_result in retrieve_tdata_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            print(f'[INFO] Failed to locate a to data-id and stock-id for {ticker} on {valid_datetime.strftime("%Y-%m-%d")} with has_actuals: {has_actuals}')
            print(f'[INFO] Retrieving just stock-id...')
            check_stockid_db_stmt = """SELECT `stocks`.`stock`.`id` 
             FROM stocks.`stock` USE INDEX (`stockid`) WHERE
               `stocks`.`stock`.`stock` = %(stock)s
                """
            result = cnx.execute(check_stockid_db_stmt,{'stock':f'{ticker.upper()}'
                                                        },multi=True)
                
            for retrieve_result in retrieve_tdata_result:
                id_res = retrieve_result.fetchall()
                if len(id_res) == 0:
                    print('[ERROR] No stock id found! Breaking!!')
                    raise Exception('[ERROR] Could not find stock id!')
                else:
                    stock_id = id_res[0][0].decode('latin1')
                    print('[INFO] Retrieved stock ID')

            break
        else:
            stock_id = id_res[0][1].decode('latin1')
            to_date_id = id_res[0][0].decode('latin1')

    # Check nn-data table after retrieval of from-date and to-date id's
    check_cache_fdata_db_stmt = """SELECT `stocks`.`data`.`data-id` 
     FROM stocks.`data` USE INDEX (`stockid-and-date`)
     WHERE stocks.`data`.`stock-id` = %(stock-id)s
       AND stocks.`data`.`date` = DATE(%(date)s)
        """
    # 75 days ago max -- check if weekday or holiday before proceeding
    valid_datetime=datetime.datetime.utcnow() - datetime.timedelta(days=75)
    holidays=USFederalHolidayCalendar().holidays(start=valid_datetime,end=(valid_datetime + datetime.timedelta(days=7)).strftime('%Y-%m-%d')).to_pydatetime()
    valid_date=valid_datetime.date()
    
    if valid_date in holidays and valid_date.weekday() >= 0 and valid_date.weekday() <= 4:
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))
    if valid_date.weekday()==5: # if saturday
        valid_datetime = (valid_datetime + datetime.timedelta(days=2))
        valid_date = (valid_date + datetime.timedelta(days=2))
    if valid_date.weekday()==6: # if sunday
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))
    if valid_date in holidays and valid_date.weekday()>=0 and valid_date.weekday() < 4:
        valid_datetime = (valid_datetime + datetime.timedelta(days=1))
        valid_date = (valid_date + datetime.timedelta(days=1))


    retrieve_data_result = cnx.execute(check_cache_fdata_db_stmt,{'stock-id':stock_id,
                                    'date':valid_date},multi=True)
    for retrieve_result in retrieve_data_result:
        id_res = retrieve_result.fetchall()
        if len(id_res) == 0:
            if not force_generation:
                print(f'[INFO] Failed to locate a from data-id  for {ticker} on {valid_datetime.strftime("%Y-%m-%d")} with has_actuals: {has_actuals}')
            break
        else:
            from_date_id = id_res[0][0].decode('latin1')
    # Check nn-data table after retrieval of from-date and to-date id's
    check_cache_nn_db_stmt = """SELECT `stocks`.`nn-data`.`open`,`stocks`.`nn-data`.`close`,
    `stocks`.`nn-data`.`range` 
     FROM stocks.`nn-data` USE INDEX (`from-to-model`,`stockid`) WHERE
    `stock-id` = %(stock-id)s
       AND `stocks`.`nn-data`.`from-date-id` = %(from-date-id)s
       AND `stocks`.`nn-data`.`to-date-id` = %(to-date-id)s
        AND `stocks`.`nn-data`.`model` = %(model)s

        """        
    try:
        check_cache_studies_db_result = cnx.execute(check_cache_nn_db_stmt,{'stock-id':stock_id,    
                                                                        'from-date-id': from_date_id,
                                                                        'to-date-id':to_date_id,
                                                                        'model':name},
                                                                        multi=True)
        # Retrieve date, verify it is in date range, remove from date range
        for result in check_cache_studies_db_result:   
            result= result.fetchall()
            for res in result:        
                # Set predicted value
                if not force_generation:
                    return (pd.DataFrame({'Open':float(res[0]),'Close':float(res[1]),'Range':float(res[2])},index=[0]),stock_id,from_date_id,to_date_id)
    except mysql.connector.errors.IntegrityError: # should not happen
        cnx.close()
        pass
    except Exception as e:
        print('[ERROR] Failed to check cached nn-data!\nException:\n',str(e))
        cnx.close()
        raise mysql.connector.errors.DatabaseError()
    return None












"""Load Specified Model"""
def load(ticker:str=None,has_actuals:bool=False,name:str="model_relu",force_generation=False,device_opt:str='/device:GPU:0',rand_date=False,data:tuple=None):        
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
    predicted=None
    from_date_id=None
    to_date_id=None
    stock_id=None

    try:
        vals=check_db_cache(cnx,ticker,has_actuals,name,force_generation)
        predicted=vals[0]
        stock_id=vals[1]
        from_date_id=vals[2]
        to_date_id=vals[3]
    except Exception as e:
        print('[INFO] Failed to gather predicted value from DB!')
        pass
    
    # Start ML calculations
    if predicted is None or force_generation:
        neural_net = Network(0,0)
        neural_net.load_model(name=name)
        
        # Actually gather data and insert if query is not met
        sampler = Sample(ticker=ticker,force_generate=force_generation)
        # sampler.__init__(ticker)
        # If data is populated, go ahead and utilize it, skip over data check for normalizer...
        if data is not None:
            sampler.set_sample_data(data[0],data[1],data[2],data[3])
        train = []
        sampler.generate_sample(_has_actuals=has_actuals,rand_date=rand_date)
    
        try: # verify there is no extra 'index' column
            sampler.data = sampler.data.drop(['index'],axis=1)
        except Exception as e:
            # print('[ERROR] Failed to drop "index" from sampler data',str(e))
            pass
        try:
            sampler.data = sampler.data.drop(['Date','High','Low'],axis=1)
        except:
            try:
                sampler.data = sampler.data.drop(['High','Low'],axis=1)
            except Exception as e:
                print('[ERROR] Failed to drop "High" and "Low" from sampler data!',str(e))


        if not force_generation:
            print(f'[INFO] Did not query all specified dates within range for nn-data retrieval!')
        with listLock:
            if has_actuals:
                train.append(np.reshape(sampler.normalized_data.iloc[-15:-1].to_numpy(),(1,1,140)))
            else:
                train.append(np.reshape(sampler.normalized_data[-14:].to_numpy(),(1,1,140)))
            prediction = neural_net.nn.predict(np.stack(train))
        if neural_net.model_choice <= 3:
            predicted = pd.DataFrame((np.reshape((prediction),(1,10))),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                                  'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED
        else:
            predicted = pd.DataFrame((np.reshape((prediction),(1,3))),columns=['Open','Close','Range']) #NORMALIZED
            
        # Upload data to DB given prediction has finished
        check_cache_nn_db_stmt = """REPLACE INTO `stocks`.`nn-data` (`nn-id`, `stock-id`, 
                                                                `from-date-id`,`to-date-id`,
                                                                `model`,`open`,`close`,`range`)
                                                        VALUES (AES_ENCRYPT(%(id)s, UNHEX(SHA2(%(id)s,512))),%(stock-id)s,%(from-date-id)s,
                                                        %(to-date-id)s,%(model)s,%(open)s,%(close)s,%(range)s)
            """        
        try:
            check_cache_studies_db_result = cnx.execute(check_cache_nn_db_stmt,{'id':f'{from_date_id}{to_date_id}{ticker.upper()}{name}',
                                                                                'stock-id':stock_id,    
                                                                            'from-date-id': from_date_id,
                                                                            'to-date-id':to_date_id,
                                                                                'model':name,
                                                                                'open':str(predicted['Open'].iloc[0]),
                                                                                'close':str(predicted['Close'].iloc[0]),
                                                                                'range':str(predicted['Range'].iloc[0])})
            db_con.commit()
        except mysql.connector.errors.IntegrityError:
            cnx.close()
            pass
        except Exception as e:
            print(f'[ERROR] Failed to insert nn-data element {predicted} for model {name}!\nException:\n',str(e))
            cnx.close()
            pass
        cnx.close()

        
    unnormalized_prediction = sampler.unnormalize(predicted).to_numpy()
    # space = pd.DataFrame([[0,0]],columns=['Open','Close'])
    unnormalized_predict_values = sampler.data.append(pd.DataFrame([[unnormalized_prediction[0,0] + sampler.data['Open'].iloc[-1],unnormalized_prediction[0,1] + sampler.data['Close'].iloc[-1]]],columns=['Open','Close']),ignore_index=True)
    predicted_unnormalized = pd.concat([unnormalized_predict_values])
    return (sampler.unnormalize(predicted),sampler.unnormalized_data.tail(1),predicted_unnormalized,sampler.keltner,sampler.fib)


"""
Run Specified Model by creating model and running batches/epochs.

"""
def run(epochs,batch_size,name="model_relu"):
    neural_net = Network(epochs,batch_size)
    neural_net.load_model(name)
    neural_net.create_model(model_choice=name)
    model = neural_net.run_model(rand_date=True)
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()


# run(10,50,"model_relu")
# run(100,100,"model_leaky",2)
# run(100,100,"model_sigmoid",3)
# run(100,100,"model_relu2",4)
# run(100,100,"model_leaky2",5)
# run(100,100,"model_sigmoid2",6)