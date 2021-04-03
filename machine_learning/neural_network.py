import keras
import tensorflow as tf
import numpy as np
from data_generator.generate_sample import Sample
from pathlib import Path
import os

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
        self.nn_input = keras.Input(shape=(1,1,78)) # 14 * 6 cols
        self.nn = keras.layers.Dense(78, activation='sigmoid',kernel_initializer=keras.initializers.RandomNormal(stddev=0.1),bias_initializer=keras.initializers.Zeros())(self.nn_input)
        #self.nn = keras.layers.Dropout(0.3)(self.nn)
        self.nn = keras.layers.Dense(24, activation='sigmoid')(self.nn)
        self.nn = keras.layers.Dense(24, activation='sigmoid')(self.nn)
        self.nn = keras.layers.Dropout(0.1)(self.nn)
        # upscale values back up for predicted output
        #self.nn = keras.layers.Dense(24, activation=keras.layers.LeakyReLU(alpha=-0.1))(self.nn)

        self.nn2 = keras.layers.Dense(6)(self.nn)
        #self.nn2 = keras.layers.Flatten()(self.nn2)

        self.nn = keras.Model(inputs=self.nn_input,outputs=self.nn2)
        self.nn.compile(optimizer=keras.optimizers.Adam(lr=0.0021,clipnorm=1,beta_1=0.001,beta_2=0.5), loss=keras.losses.BinaryCrossentropy(from_logits=True),metrics=['MeanAbsoluteError'])
        return self.nn
    def run_model(self):
        sampler = Sample()
        models = {}
        # Retrieve all necessary data into training data
        for i in range(1,self.EPOCHS):
            print(f'\n\n\nEPOCH {i}\n\n\n')
            train= []
            train_targets=[]
            validate_outputs=[]
            validate = []
            for j in range(1,self.BATCHES):
                train= []
                train_targets=[]
                validate_outputs=[]
                validate = []
                sampler.generate_sample()
                train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-2].to_numpy(),(1,1,78)))# Retrieve all except for last data to be analyzed/predicted
                train_targets.append(np.reshape(sampler.normalizer.normalized_data.tail(1).to_numpy(),(1,6)))
                sampler.generate_sample()
                validate.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-2].to_numpy(),(1,1,78)))
                validate_outputs.append(np.reshape(sampler.normalizer.normalized_data.tail(1).to_numpy(),(1,6)))
                disp = self.nn.train_on_batch(np.stack(train), np.stack(train_targets))
                model_info = {'model' : self.nn, 'history' : disp[1], 'loss' : disp[0]}
                models[i] = model_info
                # print(f'Loss: {models[i]["loss"]}')
                self.nn.evaluate(np.stack(train),np.stack(train_targets))
                print(f'{self.nn.predict(np.stack(train))}\n{np.stack(train_targets)}')

        # disp = self.nn.fit(np.stack(train),np.stack(train_targets),
                  # epochs=self.EPOCHS,
                  # batch_size=self.BATCHES,
                  # validation_data=(np.stack(validate), np.stack(validate_outputs)))
        return models
    def save_model(self):
        self.nn.save(f'{self.path}/data/model')
    def load_model(self):
        self.nn = keras.models.load_model(
            f'{self.path}/data/model')

def load():        
    sampler = Sample()
    neural_net = Network()
    neural_net.load_model()
    train = []
    sampler.generate_sample()
    train.append(np.reshape(sampler.normalizer.normalized_data.iloc[:-2].to_numpy(),(1,1,78)))
    print(neural_net.nn.predict(np.stack(train)))
def run(epochs,batch_size):
    neural_net = Network(epochs,batch_size)
    neural_net.load_model()
    neural_net.create_model()
    model = neural_net.run_model()
    for i in range(1,neural_net.EPOCHS):
        train_history = model[i]
        print(train_history)
    neural_net.save_model()
    loss = train_history['loss'][-1]
    val_loss = train_history['val_loss'][-1]
run(20,1000)
#load()