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
class Network(Neural_Framework):
    def __init__(self,epochs,batch_size):
        super().__init__(epochs, batch_size)
        self.model_map_names = {1:"model_relu",2:"model_leaky",3:"model_sigmoid",4:"model_relu2",5:"model_leaky2",
                                6:"model_sigmoid2"}

    @tf.function
    def create_model(self,model_choice=2):
        # tf.function()
        self.model_choice =model_choice
        self.nn_input = keras.Input(shape=(1,1,140)) # 14 * 10 cols
        # Relu Model
        if model_choice == 1:
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
        elif model_choice == 2:
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.74))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(10,activation='linear')(self.nn)
        # Sigmoid 
        elif model_choice == 3:
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
        elif model_choice == 4:
            self.nn = keras.layers.Dense(140, activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            keras.regularizers.l1(0.02 )
            keras.regularizers.l2(0.07)
            self.nn = keras.layers.Dense(48,activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.5)(self.nn)
            self.nn2 = keras.layers.Dense(3,activation='linear')(self.nn)
        # Leaky Relu - Out 3
        elif model_choice == 5:
            self.nn = keras.layers.Dense(140, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(3,activation='linear')(self.nn)
        # Sigmoid - Out 3
        elif model_choice == 6:
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
    def run_model(self):
        sampler = Sample()
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
                try:
                    if self.model_choice < 6:
                        sampler.generate_sample()
                    else:
                        sampler.generate_sample(out=2)
                    sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)
                except Exception as e:
                    print('[Error] Failed batch!\nException:\n',str(e))
                except Exception as e:
                    print(str(e))
                    continue
                try:
                    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,140)))# Retrieve all except for last data to be analyzed/predicted
                    if self.model_choice <= 3:
                        train_targets.append(np.reshape(sampler.normalizer.normalized_data.iloc[-1:].to_numpy(),(1,10)))
                    else:
                        tmp = sampler.normalizer.normalized_data.iloc[-1:]
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
        self.nn.save(f'{self.path}/data/{self.model_map_names.get(self.model_choice)}')
    def load_model(self,name="model_relu"):
        super().load_model(name)
listLock = threading.Lock()



"""Load Specified Model"""
def load(ticker:str=None,has_actuals:bool=False,name:str="model_relu",_is_predict=False,device_opt:str='/device:GPU:0'):        
    sampler = Sample(ticker)
    # sampler.__init__(ticker)
    neural_net = Network(0,0)
    neural_net.load_model(name=name)
    train = []
    # print(sampler.generate_sample(ticker,is_predict=(not has_actuals)))
    sampler.generate_sample(is_predict=_is_predict)
    try: # verify there is no extra 'index' column
        sampler.normalizer.data = sampler.normalizer.data.drop(['index'],axis=1)
    except Exception as e:
        print('[ERROR] Failed to drop "index" from sampler data',str(e))
    try:
        sampler.normalizer.data = sampler.normalizer.data.drop(['Date','High','Low'],axis=1)
    except:
        try:
            sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)
        except Exception as e:
            print('[ERROR] Failed to drop "High" and "Low" from sampler data!',str(e))
    with listLock:
        if has_actuals:
            train.append(np.reshape(sampler.normalizer.normalized_data.iloc[-15:-1].to_numpy(),(1,1,140)))
        else:
            train.append(np.reshape(sampler.normalizer.normalized_data[-14:].to_numpy(),(1,1,140)))
        prediction = neural_net.nn.predict(np.stack(train))
    if neural_net.model_choice <= 3:
        predicted = pd.DataFrame((np.reshape((prediction),(1,10))),columns=['Open','Close','Range','Euclidean Open','Euclidean Close','Open EMA14 Diff','Open EMA30 Diff','Close EMA14 Diff',
                                                                                                              'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED
    else:
        predicted = pd.DataFrame((np.reshape((prediction),(1,3))),columns=['Open','Close','Range']) #NORMALIZED
    unnormalized_prediction = sampler.normalizer.unnormalize(predicted).to_numpy()
    # space = pd.DataFrame([[0,0]],columns=['Open','Close'])
    unnormalized_predict_values = sampler.normalizer.data.append(pd.DataFrame([[unnormalized_prediction[0,0] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Open')],unnormalized_prediction[0,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Close')]]],columns=['Open','Close']),ignore_index=True)
    predicted_unnormalized = pd.concat([unnormalized_predict_values])
    return (sampler.normalizer.unnormalize(predicted),sampler.normalizer.unnormalized_data.tail(1),predicted_unnormalized,sampler.normalizer.keltner,sampler.normalizer.fib)


"""Run Specified Model"""
def run(epochs,batch_size,name="model_relu",model=1):
    neural_net = Network(epochs,batch_size)
    neural_net.load_model(name)
    neural_net.create_model(model_choice=model)
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
try:
            self.keltner = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_keltner.csv',index_col=False)
            self.fib = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_fib.csv',index_col=False)



# run(100,100,"model_relu",1)
# run(100,100,"model_leaky",2)
# run(100,100,"model_sigmoid",3)
# run(100,100,"model_relu2",4)
# run(100,100,"model_leaky2",5)
# run(100,100,"model_sigmoid2",6)


# print(load("spy/2021-06-18--2021-08-08_data",name="model_relu"))
