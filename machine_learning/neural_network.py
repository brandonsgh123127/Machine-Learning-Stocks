import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import threading
class Network():
    def __init__(self,epochs,batch_size):
        # print("Neural Network Instantiated")
        self.nn_input = None
        self.nn = None
        self.EPOCHS=epochs
        self.BATCHES=batch_size
        self.path = Path(os.getcwd()).parent.absolute() 
        self.model_map_names = {1:"model",2:"model_new_2",3:"model_new_3",4:"model_new_4",5:"model_new_5"} # model is sigmoid tan function combo, model_new_2 is original relu leakyrelu combo, model_new_3 is tanh sigmoid combo
        # print(tf.test.is_built_with_cuda())

    def create_model(self,model_choice=2):
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
                except:
                    continue
                try:
                    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,112)))# Retrieve all except for last data to be analyzed/predicted
                    train_targets.append(np.reshape(sampler.normalizer.normalized_data.iloc[-1:].to_numpy(),(1,8)))
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
    def load_model(self,name="model_new_2"):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/{name}')
        except:
            print("No model exists, creating new model...")
listLock = threading.Lock()
def load(ticker:str=None,has_actuals:bool=False,name:str="model_new_2"):        
    sampler = Sample(ticker)
    # sampler.__init__(ticker)
    neural_net = Network(0,0)
    neural_net.load_model(name)
    train = []
    # print(sampler.generate_sample(ticker,is_predict=(not has_actuals)))
    sampler.generate_sample(ticker,is_predict=(not has_actuals))
    with listLock:
        if has_actuals:
            train.append(np.reshape(sampler.normalizer.normalized_data.iloc[-15:-1].to_numpy(),(1,1,112)))
        else:
            train.append(np.reshape(sampler.normalizer.normalized_data[-14:].to_numpy(),(1,1,112)))
        prediction = neural_net.nn.predict(np.stack(train))
    # print(prediction)
    # unnormalized_predict_values = pd.DataFrame((prediction[:,0] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Open')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('High')],prediction[:,2]/2 + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Low')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Close')],prediction[:,1] + sampler.normalizer.data.iloc[-1,sampler.normalizer.data.columns.get_loc('Adj Close')]),columns=['Open','High','Low','Close','Adj Close'])
    predicted = pd.DataFrame((np.reshape((prediction),(1,8))),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
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
# run(100,100,"model",1)
# print(load("nvda/2021-03-18--2021-05-07_data"))
