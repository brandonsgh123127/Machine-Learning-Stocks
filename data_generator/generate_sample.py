from data_generator.normalize_data import Normalizer
import pandas as pd
import numpy as np
import os,random
'''
This class will retrieve any file given, and take a sample of data, and retrieve only a static subset for prediction analysis
'''
class Sample(Normalizer):
    def __init__(self):
        self.normalizer = Normalizer()
        self.file_list = list()
        self.DAYS_SAMPLED = 15
        dirs = os.listdir(f'{self.normalizer.path}/data/stock_no_tweets')
        for dir in dirs:
            full_path = os.path.join(f'{self.normalizer.path}/data/stock_no_tweets',dir)
            for file in os.listdir(full_path):
                self.file_list.append(f'{str(dir)}/{file}')
    def generate_sample(self):
        rand = random.choice(self.file_list)
        self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
        self.normalizer.convert_derivatives()
        # Iterate through dataframe and retrieve random sample
        self.normalizer.normalized_data = [self.normalizer.normalized_data.iloc[x:x+self.DAYS_SAMPLED] for x in np.random.randint(len(self.normalizer.normalized_data), size=self.DAYS_SAMPLED)]
        if len(self.normalizer.normalized_data[0]) < self.DAYS_SAMPLED:
            self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
            self.normalizer.convert_derivatives()
            self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[0:self.DAYS_SAMPLED]
        else:
            self.normalizer.normalized_data = self.normalizer.normalized_data[0]
        # self.normalizer.normalized_data = pd.DataFrame(self.normalizer.normalized_data,columns=[''])
            # try:
        # self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[0:self.DAYS_SAMPLED+1]
            # except:
                # self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[0:self.DAYS_SAMPLED+1]
        return (rand[0:rand.index('/')],rand[rand.index('/')+1:rand.index('_')])
# sampler = Sample()
# for i in range(1,100000):
    # indicator = sampler.generate_sample()
    # if len(sampler.normalizer.normalized_data) < 15:
        # print(indicator,len(sampler.normalizer.normalized_data))

# sampler.normalizer.display_line()