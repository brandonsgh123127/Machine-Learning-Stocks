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
    def __init__(self,ticker=None,force_generate=False):
        super().__init__(ticker,force_generate=force_generate)
        self.DAYS_SAMPLED = 15
        self.ticker=ticker
        self.path = Path(os.getcwd()).parent.absolute()
    def generate_sample(self,out=8,_has_actuals=False,rand_date=False,is_divergence=False):
        self.cnx = self.db_con.cursor(buffered=True)
        if not _has_actuals:
            # print("Predict Mode")
            self.DAYS_SAMPLED = 14
        else:
            self.DAYS_SAMPLED = 15
        # If data has been set via neural_network, don't read data
        if self.data is not None:
            pass
        else:
            # Read the current ticker data
            try:
                self.read_data(self.ticker,rand_dates=rand_date) 
            except Exception as e:
                print(f'[ERROR] Failed to read sample data for ticker {self.ticker}\nException:\n{str(e)}')
                raise Exception(str(e))
        # Iterate through dataframe and retrieve random sample
        if not is_divergence:
            self.convert_derivatives(out=out)
        else:
            self.convert_divergence()
        self.normalized_data = self.normalized_data.iloc[-(self.DAYS_SAMPLED):]
        try:
            if not is_divergence:
                rc = self.normalize()
            else:
                rc = self.normalize_divergence()
            if rc == 1:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                self.cnx.close()            
                raise Exception("[Error] Normalize did not return exit code 1")

        except Exception as e:
            print('[ERROR] Failed to Normalize data!\nException:\n',str(e))
            raise Exception(e)
        try:
            if len(self.normalized_data) < self.DAYS_SAMPLED:
                self.read_data(self.ticker,rand_dates=rand_date) # Get ticker and date from path
                if not is_divergence:
                    self.convert_derivatives(out=out)
                else:
                    self.convert_divergence()
        except Exception as e:
            print("[ERROR] FAILED to GENERATE SAMPLE\n",str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.cnx.close()
            return 1
        self.cnx.close()
        return 0
    
    
    
    def generate_divergence_sample(self,_has_actuals=False,rand_date=False):
        self.cnx = self.db_con.cursor(buffered=True)

        if not _has_actuals:
            self.DAYS_SAMPLED = 14
        else:
            self.DAYS_SAMPLED = 15
        if self.data is not None and self.keltner is not None:
            pass
        else:
            # Read the current ticker data
            try:
                self.read_data(self.ticker,rand_dates=rand_date) # Get ticker and date from path
            except Exception as e:
                print(f'[ERROR] Failed to read sample data for ticker {self.ticker}\nException:\n{str(e)}')
                raise Exception(str(e))
        # Iterate through dataframe and retrieve random sample
        self.convert_divergence()
        self.normalized_data = self.normalized_data.iloc[-(self.DAYS_SAMPLED):]

        rc = self.normalize_divergence()
        if rc == 1:
            raise Exception("Normalize did not return exit code 1")
        if len(self.normalized_data) < self.DAYS_SAMPLED:
            self.read_data(self.to_date,self.ticker) # Get ticker and date from path
            self.convert_derivatives()
        self.cnx.close()
        return 0
    def unnormalize(self, data):
        return super().unnormalize(data)
    
    '''
     Getters/Setters
    '''
    def set_ticker(self,ticker):
        self.ticker=ticker
    def get_ticker(self):
        return self.ticker
    def set_sample_data(self,data:pd.DataFrame,studies:pd.DataFrame,fib:pd.DataFrame,keltner:pd.DataFrame):
        self.data=data
        self.studies=studies
        self.fib=fib
        self.keltner=keltner
# for i in range(1,21000):
    # sampler = Sample()
# sampler = Sample()
# for i in range(1,100000):
    # indicator = sampler.generate_sample()
    # if len(sampler.normalizer.normalized_data) < 15:
        # print(indicator,len(sampler.normalizer.normalized_data))

# sampler.normalizer.display_line()