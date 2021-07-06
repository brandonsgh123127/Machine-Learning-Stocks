from data_generator.normalize_data import Normalizer
import pandas as pd
import numpy as np
import os,random
import datetime
from pathlib import Path
import pytz

'''
This class will retrieve any file given, and take a sample of data, and retrieve only a static subset for prediction analysis
'''
class Sample(Normalizer):
    def __init__(self,ticker=None):
        self.normalizer = Normalizer()
        self.normalizer.__init__()
        self.file_list = list()
        self.DAYS_SAMPLED = 15
        self.MIN_DATE = datetime.datetime(2013,1,1).date()
        self.MAX_DATE = datetime.datetime.now().date()
        self.path = Path(os.getcwd()).parent.absolute()
        self.DAYS_IN_MONTH = {1:31,
                 2:28,
                 3:31,
                 4:30,
                 5:31,
                 6:30,
                 7:31,
                 8:31,
                 9:30,
                 10:31,
                 11:30,
                 12:31}
        if ticker is None:
            with open(f'{self.path}/data/watchlist/default.csv') as f:
                ticker = random.choice(f.readlines())
                ticker = ticker[0:ticker.find(',')]
    def generate_sample(self,ticker=None,is_predict=False):
        if ticker is None:
            with open(f'{self.path}/data/watchlist/default.csv') as f:
                rand = random.choice(f.readlines())
                rand = rand[0:rand.find(',')]
        else:
            rand = ticker
        print(rand)
        if is_predict:
            # print("Predict Mode")
            self.DAYS_SAMPLED = 14
            
        calc_leap_day = lambda year_month: random.randint(1,29) if year_month[1]==2 and ((year_month[0]%4==0 and year_month[0]%100==0 and year_month[0]%400==0) or (year_month[0]%4==0 and year_month[0]%100!=0)) else random.randint(1,28) if year_month[1]==2 else random.randint(1,self.DAYS_IN_MONTH[year_month[1]])
        set1 = (random.randint(2016,self.MAX_DATE.year - 1),random.randint(1,12))
        set1 = datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc)
        
        try:
            self.normalizer.read_data(set1,rand) # Get ticker and date from path
            # Iterate through dataframe and retrieve random sample
            self.normalizer.convert_derivatives()
            self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[-(self.DAYS_SAMPLED):]
        except RuntimeWarning:
            return
            
        # print(self.normalizer.normalized_data)
        # print(len(self.normalizer.normalized_data))
        rc = self.normalizer.normalize()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalizer.normalized_data) < self.DAYS_SAMPLED:
            set1 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year - 1),random.randint(1,12))
            set1 = datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc)
            self.normalizer.read_data(set1,rand) # Get ticker and date from path
            self.normalizer.convert_derivatives()
        return (self.path,set1)
    def generate_divergence_sample(self,ticker=None,is_predict=False):
        if ticker is None:
            rand = random.choice(self.file_list)
        else:
            rand = ticker
        if is_predict:
            self.DAYS_SAMPLED = 14
        self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
        # Iterate through dataframe and retrieve random sample
        self.normalizer.convert_divergence()
        self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[-(self.DAYS_SAMPLED):]
            
        # print(self.normalizer.normalized_data)
        # print(len(self.normalizer.normalized_data))
        rc = self.normalizer.normalize_divergence()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalizer.normalized_data) < self.DAYS_SAMPLED:
            self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
            self.normalizer.convert_derivatives()
        return (rand[0:rand.index('/')],rand[rand.index('/')+1:rand.index('_')])
    def unnormalize(self, data):
        self.normalizer.unnormalize(data)
sampler = Sample()
for i in range(1,21000):
    indicator = sampler.generate_sample()
    # if len(sampler.normalizer.normalized_data) < 15:
        # print(indicator,len(sampler.normalizer.normalized_data))

# sampler.normalizer.display_line()