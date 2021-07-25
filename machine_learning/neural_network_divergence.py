import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import threading
from machine_learning.neural_framework import Neural_Framework

class Neural_Divergence(Neural_Framework):
    def __init__(self,epochs,batch_size):
        super().__init__(epochs, batch_size)
        self.model_map_names = {1:"divergence",2:"divergence_2",3:"divergence_3",4:"divergence_4"} # model is sigmoid tan function combo, model_new_2 is original relu leakyrelu combo, model_new_3 is tanh sigmoid combo
    def create_model(self,model_choice=1):
        self.model_choice =model_choice
        self.nn_input = keras.Input(shape=(1,1,28)) # 14 * 8 cols
        if model_choice == 1:
            self.nn = keras.layers.Dense(28, activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            # self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(12,activation='sigmoid',kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(12,activation='tanh')(self.nn)
            self.nn = keras.layers.Dense(12,activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(8,activation='relu')(self.nn)
            self.nn2 = keras.layers.Dense(2,activation='relu')(self.nn)
        elif model_choice == 2:
            self.nn = keras.layers.Dense(28, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(12,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(12,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(8,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn2 = keras.layers.Dense(2,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
        elif model_choice == 3:
            self.nn = keras.layers.Dense(28, activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(12,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(12,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(8,activation='sigmoid')(self.nn)
            self.nn2 = keras.layers.Dense(2,activation='linear')(self.nn)
        elif model_choice == 4:
            self.nn = keras.layers.Dense(28, keras.layers.LeakyReLU(alpha=0.92),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(12,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(12,activation=keras.layers.LeakyReLU(alpha=1.45),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(12,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn2 = keras.layers.Dense(2,activation='linear')(self.nn)    
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
        self.nn.save(f'{self.path}/data/{self.model_map_names.get(self.model_choice)}')
    def load_model(self,name="divergence"):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/{name}')
        except:
            print("No model exists, creating new model...")
listLock = threading.Lock()
def load_divergence(ticker:str=None,has_actuals:bool=False,name:str="divergence",device_opt='/device:CPU:0'):        
    sampler = Sample(ticker)
    # sampler.__init__(ticker)
    neural_net = Neural_Divergence(0,0)
    neural_net.load_model(name)
    train = []
    # print(sampler.generate_sample(ticker,is_predict=(not has_actuals)))
    with tf.device('/device:GPU:0'):
        sampler.generate_divergence_sample(ticker,is_predict=(not has_actuals))
    # sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)
    with tf.device(device_opt):
        with listLock:
            if has_actuals:
                train.append(np.reshape(sampler.normalizer.normalized_data.iloc[-15:-1].to_numpy(),(1,1,28)))
            else:
                train.append(np.reshape(sampler.normalizer.normalized_data[-14:].to_numpy(),(1,1,28)))
            with tf.device(device_opt):
                prediction = neural_net.nn.predict(np.stack(train))
        # print(prediction)
        # unnormalized_predict_values = pd.DataFrame((prediction[:,0] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Open')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('High')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Low')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Close')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Adj Close')]),columns=['Open','High','Low','Close','Adj Close'])
        predicted = pd.DataFrame((np.reshape((prediction),(1,2))),columns=['Divergence','Gain/Loss']) #NORMALIZED
    # print(sampler.normalizer.unnormalize_divergence(predicted),sampler.normalizer.unnormalized_data.tail(1))
    return (sampler.normalizer.unnormalize_divergence(predicted),sampler.normalizer.unnormalized_data.iloc[-1:],sampler.normalizer.keltner)
def run(epochs,batch_size,name="divergence",model=1):
    neural_net = Neural_Divergence(epochs,batch_size)
    neural_net.load_model(name)
    neural_net.create_model(model_choice=model)
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
# run(100,100,"divergence",1)
# run(100,100,"divergence_2",2)
# run(100,100,"divergence_3",3)
# run(100,100,"divergence_4",4)

# print(load_divergence("spy/2021-05-26--2021-07-16_data",name='divergence_3',has_actuals=True))
