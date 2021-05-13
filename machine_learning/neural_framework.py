from pathlib import Path
import os

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
        pass