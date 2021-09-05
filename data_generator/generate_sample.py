from data_generator.normalize_data import Normalizer
import pandas as pd
import numpy as np
import os,random
import datetime
from pathlib import Path
import pytz
import sys
import mysql.connector
from mysql.connector import errorcode
import binascii
import uuid
import xml.etree.ElementTree as ET


'''
This class will retrieve any file given, and take a sample of data, and retrieve only a static subset for prediction analysis
'''
class Sample(Normalizer):
    def __init__(self,ticker=None):
        self.normalizer = Normalizer()
        self.normalizer.__init__()
        self.DAYS_SAMPLED = 15
        self.ticker=ticker
        self.path = Path(os.getcwd()).parent.absolute()
    def generate_sample(self,is_predict=False,out=8):
        try:
            file_list:list = []
            if self.ticker is None:
                dirs = os.listdir(f'{self.normalizer.path}/data/stock_no_tweets')
                for dir in dirs:
                    full_path = os.path.join(f'{self.normalizer.path}/data/stock_no_tweets',dir)
                    for file in os.listdir(full_path):
                        file_list.append(f'{str(dir)}/{file}')
                rand = random.choice(file_list)
                del file_list
            else:
                rand = self.ticker
        except AttributeError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise Exception("AttributeError:\n",str(e))
        tree = ET.parse("{0}/data/mysql/mysql_config.xml".format(self.path))
        root = tree.getroot()
        self.normalizer.cnx = self.normalizer.db_con.cursor(buffered=True)

        if is_predict:
            # print("Predict Mode")
            self.DAYS_SAMPLED = 14
        self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
        # Iterate through dataframe and retrieve random sample
        self.normalizer.convert_derivatives(out=out)
        self.normalizer.normalized_data = self.normalizer.normalized_data.iloc[-(self.DAYS_SAMPLED):]
        try:
            rc = self.normalizer.normalize()
            if rc == 1:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                self.normalizer.cnx.close()            
                raise Exception("[Error] Normalize did not return exit code 1")

        except Exception as e:
            print('[ERROR] Failed to Normalize data!\nException:\n',str(e))
        try:
            if len(self.normalizer.normalized_data) < self.DAYS_SAMPLED:
                self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
                self.normalizer.convert_derivatives()
        except Exception as e:
            print("[ERROR] FAILED to GENERATE SAMPLE\n",str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.normalizer.cnx.close()
            return 1
        return (rand[0:rand.index('/')],rand[rand.index('/')+1:rand.index('_')])
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

        rc = self.normalizer.normalize_divergence()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalizer.normalized_data) < self.DAYS_SAMPLED:
            self.normalizer.read_data(rand[rand.index('/')+1:rand.index('_')],rand[0:rand.index('/')]) # Get ticker and date from path
            self.normalizer.convert_derivatives()
        return (rand[0:rand.index('/')],rand[rand.index('/')+1:rand.index('_')])
    def unnormalize(self, data):
        self.normalizer.unnormalize(data)
# for i in range(1,21000):
    # sampler = Sample()
# sampler = Sample()
# for i in range(1,100000):
    # indicator = sampler.generate_sample()
    # if len(sampler.normalizer.normalized_data) < 15:
        # print(indicator,len(sampler.normalizer.normalized_data))

# sampler.normalizer.display_line()