from pathlib import Path
import os
import keras
import tensorflow as tf
from tensorflow.python.client import device_lib 
import random

class Neural_Framework():
    def __init__(self,epochs,batch_size):
        self.nn_input = None
        self.nn = None
        self.EPOCHS=epochs
        self.BATCHES=batch_size
        self.path = Path(os.getcwd()).parent.absolute() 
        self.model_name=None
        # tf.debugging.set_log_device_placement(True)
        # print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
        # print(device_lib.list_local_devices())
        
    def create_model(self,model_choice="model_relu"):
        pass
    def run_model(self):
        pass
    def save_model(self):
        self.nn.save(f'{self.path}/data/{self.model_name}')
    def choose_random_ticker(self,csv_file):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker
    def load_model(self,name=None):
        try:
            self.model_name=name
            self.nn = keras.models.load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():        
                if(name == name_loc):
                    self.model_choice = model_choice
        except:
            print(f'[INFO] No model exists for {name}, creating new model...')