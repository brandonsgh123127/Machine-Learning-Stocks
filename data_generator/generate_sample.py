from data_generator.normalize_data import Normalizer
import pandas as pd
import numpy as np
import os,random
'''
This class will retrieve any file given, and take a sample of data, and retrieve only a static subset for prediction analysis
'''
class Sample(Normalizer):
    def __init__(self,ticker=None):
        self.normalizer = Normalizer()
        self.normalizer.__init__()
        self.file_list = list()
        self.DAYS_SAMPLED = 15
        if ticker is None:
            dirs = os.listdir(f'{self.normalizer.path}/data/stock_no_tweets')
            for dir in dirs:
                full_path = os.path.join(f'{self.normalizer.path}/data/stock_no_tweets',dir)
                for file in os.listdir(full_path):
                    self.file_list.append(f'{str(dir)}/{file}')
    def generate_sample(self,ticker=None,is_predict=False):
        if ticker is None:
            rand = random.choice(self.file_list)
        else:
            rand = ticker
        if is_predict:
            # print("Predict Mode")
            self.DAYS_SAMPLED = 14
        self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
        # Iterate through dataframe and retrieve random sample
        self.normalizer.convert_derivatives()
        self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[-(self.DAYS_SAMPLED):]
            
        # print(self.normalizer.normalized_data)
        # print(len(self.normalizer.normalized_data))
        rc = self.normalizer.normalize()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalizer.normalized_data) < self.DAYS_SAMPLED:
            self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
            self.normalizer.convert_derivatives()
        self.normalizer.normalized_data = self.normalizer.normalized_data.tail(self.DAYS_SAMPLED)
        self.normalizer.unnormalized_data = self.normalizer.normalized_data.tail(self.DAYS_SAMPLED)
        return (rand[0:rand.index('/')],rand[rand.index('/')+1:rand.index('_')])
    def unnormalize(self, data):
        self.normalizer.unnormalize(data)
# sampler = Sample()
# for i in range(1,100000):
    # indicator = sampler.generate_sample()
    # if len(sampler.normalizer.normalized_data) < 15:
        # print(indicator,len(sampler.normalizer.normalized_data))

# sampler.normalizer.display_line()