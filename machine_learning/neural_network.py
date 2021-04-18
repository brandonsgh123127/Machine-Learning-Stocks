import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from data_generator.normalize_data import Normalizer

class Network():
    def __init__(self,epochs,batch_size):
        print("Neural Network Instantiated")
        self.nn_input = None
        self.nn = None
        self.EPOCHS=epochs
        self.BATCHES=batch_size
        self.path = Path(os.getcwd()).parent.absolute() 
        #sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))
        print(tf.test.is_built_with_cuda())

    def create_model(self):
        self.nn_input = keras.Input(shape=(1,1,112)) # 14 * 8 cols
        self.nn = keras.layers.Dense(112, activation='relu',kernel_initializer='he_uniform')(self.nn_input)
        self.nn = keras.layers.Dropout(0.1)(self.nn)
        keras.regularizers.l1(0.02)
        keras.regularizers.l2(0.02)
        self.nn = keras.layers.Dense(48,activation='relu',kernel_initializer=keras.initializers.RandomNormal(stddev=0.31))(self.nn)
        self.nn = keras.layers.Dense(48,activation='relu')(self.nn)
        self.nn = keras.layers.Dense(48,activation='relu')(self.nn)
        self.nn = keras.layers.Dense(48,activation='relu')(self.nn)
        self.nn = keras.layers.Dropout(0.2)(self.nn)
        # self.nn = keras.layers.Dense(24,activation=keras.layers.ReLU())(self.nn)
        self.nn2 = keras.layers.Dense(8,activation='linear')(self.nn)
        # self.nn21 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn22 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn23 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn24 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn25 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn26 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn27 = keras.layers.Dense(1,activation='linear')(self.nn2)
        # self.nn28 = keras.layers.Dense(1,activation='linear')(self.nn2)


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
                sampler.generate_sample()
                train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,112)))# Retrieve all except for last data to be analyzed/predicted
                train_targets.append(np.reshape(sampler.normalizer.normalized_data.iloc[-1:].to_numpy(),(1,8)))
                # sampler.generate_sample()
                # validate.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-2].to_numpy(),(1,1,78)))
                # validate_outputs.append(np.reshape(sampler.normalizer.normalized_data.tail(1).to_numpy(),(1,6)))
                disp = self.nn.train_on_batch(np.stack(train), np.stack(train_targets))
                model_info = {'model' : self.nn, 'history' : disp[1], 'loss' : disp[0]}
                models[i] = (model_info['loss'] + models[i] )
                # print(f'Loss: {models[i]["loss"]}')
                try:
                    self.nn.evaluate(np.stack(train),np.stack(train_targets))
                except:
                    continue
            models[i] = models[i] / self.BATCHES
                # print(f'{self.nn.predict(np.stack(train))}\n{np.stack(train_targets)}')
            self.save_model()

        return models
    def save_model(self):
        self.nn.save(f'{self.path}/data/model')
    def load_model(self):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/model')
        except:
            print("No model exists, creating new model...")
def load(ticker=None):        
    sampler = Sample()
    sampler.__init__()
    neural_net = Network(0,0)
    neural_net.load_model()
    train = []
    print(sampler.generate_sample(ticker))
    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-1].to_numpy(),(1,1,112)))
    prediction = neural_net.nn.predict(np.stack(train))
    # print(prediction)
    predicted = pd.DataFrame((np.reshape((prediction),(1,8))),columns=['Open Diff','Close Diff','Derivative Diff','Derivative EMA14','Derivative EMA30','Close EMA14 Diff',
                                                                                                'Close EMA30 Diff','EMA14 EMA30 Diff']) #NORMALIZED
    # print(f'difference: {np.subtract(np.reshape((prediction),(1,8)),np.reshape(sampler.normalizer.normalized_data.tail(1).to_numpy(),(1,8)))}')
    # print(pd.concat([sampler.normalizer.unnormalized_data.iloc[:-1],sampler.normalizer.unnormalize(predicted)]),sampler.normalizer.unnormalized_data)
    # print(sampler.normalizer.unnormalize(predicted),sampler.normalizer.unnormalized_data.tail(1))
    return (sampler.normalizer.unnormalize(predicted),sampler.normalizer.unnormalized_data.tail(1))
    # print(predicted)
def run(epochs,batch_size):
    neural_net = Network(epochs,batch_size)
    neural_net.load_model()
    neural_net.create_model()
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
    #loss = train_history['loss']
    # val_loss = train_history['val_loss']
# run(1000,100)
# print(load())
