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
        # print("Neural Network Instantiated")
        super().__init__(epochs, batch_size)
        self.model_map_names = {1:"model",2:"model_new_2",3:"model_new_3",4:"model_new_4",5:"model_new_5",
                                6:"model_out_new",7:"model_out_new_2",8:"model_out_new_3",9:"model_out_new_4",10:"model_out_new_5"} # model is sigmoid tan function combo, model_new_2 is original relu leakyrelu combo, model_new_3 is tanh sigmoid combo
    def create_model(self,model_choice=2):
        tf.function()
        self.model_choice =model_choice
        self.nn_input = keras.Input(shape=(1,1,112)) # 14 * 8 cols
        if model_choice == 1:
            self.nn = keras.layers.Dense(112, activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            # self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation='sigmoid',kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(48,activation='tanh')(self.nn)
            self.nn = keras.layers.Dense(48,activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation='relu')(self.nn)
            self.nn2 = keras.layers.Dense(8,activation='relu')(self.nn)
        elif model_choice == 2:
            self.nn = keras.layers.Dense(112, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn2 = keras.layers.Dense(8,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
        elif model_choice == 3:
            self.nn = keras.layers.Dense(112, activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation='sigmoid')(self.nn)
            self.nn2 = keras.layers.Dense(8,activation='linear')(self.nn)
        elif model_choice == 4:
            self.nn = keras.layers.Dense(112, keras.layers.LeakyReLU(alpha=0.92),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=1.45),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.75))(self.nn)
            self.nn2 = keras.layers.Dense(8,activation='linear')(self.nn)       
        elif model_choice == 5:
            self.nn = keras.layers.Dense(112, keras.layers.LeakyReLU(alpha=0.92),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.75))(self.nn)
            self.nn2 = keras.layers.Dense(8,activation='linear')(self.nn)
        
        
        
        elif model_choice == 6:
            self.nn = keras.layers.Dense(112, activation='relu',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            # self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(48,activation='sigmoid',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(2,activation='linear')(self.nn)
        elif model_choice == 7:
            self.nn = keras.layers.Dense(112, activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer='he_uniform')(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(24,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
            self.nn2 = keras.layers.Dense(2,activation=keras.layers.LeakyReLU(alpha=0.5))(self.nn)
        elif model_choice == 8:
            self.nn = keras.layers.Dense(112, activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.04)
            self.nn = keras.layers.Dense(48,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.5),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(8,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)
            self.nn2 = keras.layers.Dense(2,activation='linear')(self.nn)
        elif model_choice == 9:
            self.nn = keras.layers.Dense(112, keras.layers.LeakyReLU(alpha=0.92),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l1(0.01)
            keras.regularizers.l2(0.01)
            self.nn = keras.layers.Dense(48,activation='tanh',kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=1.45),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(24,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(16,activation=keras.layers.LeakyReLU(alpha=0.75))(self.nn)
            self.nn2 = keras.layers.Dense(2,activation=keras.layers.LeakyReLU(alpha=0.3))(self.nn)       
        elif model_choice == 10:
            self.nn = keras.layers.Dense(112, keras.layers.LeakyReLU(alpha=0.92),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn_input)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            keras.regularizers.l2(0.03)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(48,activation=keras.layers.LeakyReLU(alpha=0.3),kernel_initializer=tf.keras.initializers.GlorotNormal(seed=None))(self.nn)
            self.nn = keras.layers.Dense(24,activation='sigmoid')(self.nn)
            self.nn = keras.layers.Dropout(0.1)(self.nn)
            self.nn = keras.layers.Dense(12,activation=keras.layers.LeakyReLU(alpha=0.75))(self.nn)
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
                    sampler.generate_sample()
                    sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)
                except RuntimeError:
                    continue
                except Exception as e:
                    print(str(e))
                    continue
                try:
                    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,112)))# Retrieve all except for last data to be analyzed/predicted
                    if self.model_choice == 1 or self.model_choice == 2 or self.model_choice == 3 or self.model_choice == 4 or self.model_choice == 5:
                        train_targets.append(np.reshape(sampler.normalizer.normalized_data.iloc[-1:].to_numpy(),(1,8)))
                    else:
                        tmp = sampler.normalizer.normalized_data.iloc[-1:]
                        # print(tmp)
                        tmp = pd.concat([pd.DataFrame([tmp['Open Diff'].to_numpy()]),pd.DataFrame([tmp['Close Diff'].to_numpy()])])
                        # print('y')
                        train_targets.append(np.reshape(tmp.to_numpy(),(1,2)))
                except:
                    print('failed to specify train_target value')
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
    def load_model(self,name="model_new_2"):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():        
                if(name == name_loc):
                    self.model_choice = model_choice
        except:
            print("No model exists, creating new model...")
listLock = threading.Lock()
def load(ticker:str=None,has_actuals:bool=False,name:str="model_new_2"):        
    sampler = Sample(ticker)
    # sampler.__init__(ticker)
    neural_net = Network(0,0)
    neural_net.load_model(name=name)
    train = []
    # print(sampler.generate_sample(ticker,is_predict=(not has_actuals)))
    sampler.generate_sample(ticker,is_predict=(not has_actuals))
    sampler.normalizer.data = sampler.normalizer.data.drop(['High','Low'],axis=1)

    with listLock:
        if has_actuals:
            train.append(np.reshape(sampler.normalizer.normalized_data.iloc[-15:-1].to_numpy(),(1,1,112)))
        else:
            train.append(np.reshape(sampler.normalizer.normalized_data[-14:].to_numpy(),(1,1,112)))
        prediction = neural_net.nn.predict(np.stack(train))
    # print(prediction)
    # unnormalized_predict_values = pd.DataFrame((prediction[:,0] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Open')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('High')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Low')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Close')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Adj Close')]),columns=['Open','High','Low','Close','Adj Close'])
    if neural_net.model_choice == 1 or neural_net.model_choice == 2 or neural_net.model_choice == 3 or neural_net.model_choice == 4 or neural_net.model_choice == 5:
        predicted = pd.DataFrame((np.reshape((prediction),(1,8))),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED
    else:
        predicted = pd.DataFrame((np.reshape((prediction),(1,2))),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED

    unnormalized_prediction = sampler.normalizer.unnormalize(predicted).to_numpy()
    space = pd.DataFrame([[0,0]],columns=['Open','Close'])
    unnormalized_predict_values = sampler.normalizer.data.append(pd.DataFrame([[unnormalized_prediction[0,0] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Open')],unnormalized_prediction[0,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Close')]]],columns=['Open','Close']),ignore_index=True)
    # print(unnormalized_prediction[0,0],unnormalized_prediction[0,1],"\npredicted dataframe")

    predicted_unnormalized = pd.concat([sampler.normalizer.data,space,unnormalized_predict_values])
    return (sampler.normalizer.unnormalize(predicted),sampler.normalizer.unnormalized_data.tail(1),predicted_unnormalized)
def run(epochs,batch_size,name="model",model=1):
    neural_net = Network(epochs,batch_size)
    neural_net.load_model(name)
    neural_net.create_model(model_choice=model)
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
# run(100,100,"model_out_new_2",6)
# run(100,100,"model_out_new",6)
# run(100,100,"model_out_new_2",7)
# run(100,100,"model_out_new_3",8)
# run(100,100,"model_out_new_4",9)
# run(100,100,"model_out_new_5",10)
run(100,100,"model",1)
# run(100,100,"model_new_2",2)
# run(100,100,"model_new_3",3)
# run(100,100,"model_new_4",4)
# run(100,100,"model_new_5",5)

# print(load("spy/2021-03-23--2021-05-12_data"))
