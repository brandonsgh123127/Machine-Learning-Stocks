from pathlib import Path
import os
import keras
import tensorflow as tf


class Neural_Framework():
    def __init__(self,epochs,batch_size):
        self.nn_input = None
        self.nn = None
        self.EPOCHS=epochs
        self.BATCHES=batch_size
        self.path = Path(os.getcwd()).parent.absolute() 
    def create_model(self,model_choice=None):
        pass
    def run_model(self):
        pass
    def save_model(self):
        pass
    def load_model(self,name=None):
        try:
            self.nn = keras.models.load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():        
                if(name == name_loc):
                    self.model_choice = model_choice
        except:
            print("No model exists, creating new model...")