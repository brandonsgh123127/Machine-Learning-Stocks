from abc import ABC, abstractmethod
from pathlib import Path
import os
import keras
import tensorflow as tf
from tensorflow.python.client import device_lib
import random


class Neural_Framework(ABC):
    def __init__(self, epochs, batch_size):
        self.model_choice = None
        self.nn_input = None
        self.EPOCHS = epochs
        self.BATCHES = batch_size
        self.path = Path(os.getcwd()).absolute()
        self.model_name = None
        # tf.debugging.set_log_device_placement(True)
        # print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
        # print(device_lib.list_local_devices())

    @abstractmethod
    def create_model(self, model_choice="relu_multilayer_l2"):
        pass

    @abstractmethod
    def run_model(self, nn: keras.models.Model):
        pass

    def save_model(self, nn: keras.models.Model):
        nn.save(f'{self.path}/data/{self.model_name}')

    @staticmethod
    def choose_random_ticker(self, csv_file:str):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker

    def load_model(self, name=None):
        try:
            self.model_name = name
            nn = keras.models.load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():
                if name == name_loc:
                    self.model_choice = model_choice
            return nn
        except:
            print(f'[INFO] No model exists for {name}, creating new model...')

    @abstractmethod
    def run_model(self, nn: keras.models.Model, rand_date=False):
        pass
