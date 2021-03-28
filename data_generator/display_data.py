import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os

class Display():
    def __init__(self):
        print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
    def read_studies(self,date):
        self.data_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/MU/{date}_data.csv')
        self.study_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/MU/{date}_studies.csv',index_col=0)
        pd.set_option("display.max.columns", None)
        print(self.data_display.head(),self.study_display.head())
        print(self.study_display.index.names)
    def display_box(self):
        self.study_display.plot.box()
        plt.show()
    def display_line(self):
        plt.figure()
        self.study_display['index'] = range(1, len(self.study_display) + 1)
        self.study_display.reset_index().plot(x='index')
        plt.show()

dis = Display()
dis.read_studies("2014-12-05--2014-12-12")
dis.display_line()