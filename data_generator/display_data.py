import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os

'''
Easily display unfiltered data given the ticker and date range specified on the file
Class implements matplotlib and pandas
'''
class Display():
    def __init__(self):
        # print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.path = Path(os.getcwd()).parent.absolute() 
        self.color_map = {'blue':'b',
                        'green':'g',
                        'red':'r',
                        'cyan':'c',
                        'magenta':'m',
                        'yellow':'y',
                        'black':'k',
                        'white':'w'}
    def read_studies(self,date,ticker):
        self.data_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_data.csv').drop(['Adj Close'],axis=1)
        self.study_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_studies.csv',index_col=0)
        self.keltner_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_keltner.csv',index_col=0)
        self.ticker = ticker
        self.date = date
    def read_studies_data(self,predicted=None,actual=None):
        self.data_display = actual
        self.data_predict_display = predicted
        pd.set_option("display.max.columns", None)
    def display_box(self,data=None):
        plt.cla()
        plt.close()
        c = 'blue'
        if data is None:
            self.data_display.transpose().boxplot(patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color=c),
                                                    whiskerprops=dict(color=c),
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c),
                                                    autorange=True).set_alpha(0.3)
        else:
            data.transpose().boxplot(patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color=c),
                                                    showfliers=False,
                                                    showcaps=False,
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c),
                                                    autorange=True).set_alpha(0.3)
    def display_divergence(self,ticker=None,dates=None,color=None,has_actuals=False):
        plt.cla()
        plt.figure()
        data = self.data_predict_display.reset_index()
        # data.drop(columns='index')        
        indices_dict = {0:'Divergence',1:'Gain/Loss'}
        # data = data.transpose()
        # index = [0,0]
        # data.set_index(index)
        # ax = data['Divergence'].transpose().plot(x='Divergence',y='index',style=f'{self.color_map.get(color)}x')
        # index = [0,1]
        # data.set_index(index)
        # ax = data['Gain/Loss'].transpose().plot(x='Gain/Loss',y='index',style=f'{self.color_map.get(color)}o', ax=ax)
        data.transpose().plot(kind='line',color=color)
    def display_line(self,ticker=None,dates=None,color=None):
        indices_dict = {0:'Open',1:'Close',2:'Range',3:'Euclidean Open',4:'Euclidean Close',5:'Open EMA14 Diff',6:'Open EMA30 Diff',7:'Close EMA14 Diff',8:'Close EMA30 Diff',9:'EMA14 EMA30 Diff'}
        data = pd.concat([self.data_display.reset_index(),self.data_predict_display.reset_index()],ignore_index=False).set_flags(allows_duplicate_labels=True)
        data_orig = data
        data['index'] = [0,0]
        data = data.set_index('index')
        ax = data['Open'].plot(x='index',y='Open',style=f'{self.color_map.get(color)}x')
        data['index'] = [1,1]
        data = data.set_index('index')
        ax = data['Close'].plot(x='index',y='Close',style=f'{self.color_map.get(color)}o', ax=ax)
        data['index'] = [2,2]
        data = data.set_index('index')
        ax = data['Range'].plot(x='index',y='Range',style='mo', ax=ax)
        data['index'] = [3,3]
        # data = data.set_index('index')
        # ax = data['Derivative EMA14'].plot(x='index',y='Derivative EMA14',style='co', ax=ax)
        # data['index'] = [4,4]
        # data = data.set_index('index')
        # ax = data['Derivative EMA30'].plot(x='index',y='Derivative EMA30',style='ro', ax=ax)
        # data['index'] = [5,5]
        # data = data.set_index('index')
        # ax = data['Close EMA14 Diff'].plot(x='index',y='Close EMA14 Diff',style='go', ax=ax)
        # data['index'] = [6,6]
        # data = data.set_index('index')
        # ax = data['Close EMA30 Diff'].plot(x='index',y='Close EMA30 Diff',style='yo', ax=ax)
        # data['index'] = [7,7]
        # data = data.set_index('index')
        # ax = data['EMA14 EMA30 Diff'].plot(x='index',y='EMA14 EMA30 Diff',style='bs', ax=ax,title=f'{ticker} - {dates[1]}')
        # data['index'] = [0,1]
        # data = data.set_index('index')

        for i,row in enumerate(data_orig.index):
            for j,col in enumerate(data_orig.columns):
                if j == 8:
                    continue
                if i == 0:
                    y = round(data.iloc[i][j],2)
                    ax.text(j, y, f'{indices_dict.get(j)} - A {y}',size='x-small')
                else:
                    y = round(data.iloc[i][j],2)
                    ax.text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')
    def display_predict_only(self,ticker=None,dates=None,color=None):
        indices_dict = {0:'Open',1:'Close',2:'Range',3:'Euclidean Open',4:'Euclidean Close',5:'Open EMA14 Diff',6:'Open EMA30 Diff',7:'Close EMA14 Diff',8:'Close EMA30 Diff',9:'EMA14 EMA30 Diff'}
        data = self.data_predict_display
        data['index'] = [0]
        data = data.set_index('index')
        ax = data['Open'].plot(x='index',y='Open',style=f'{self.color_map.get(color)}x')
        data['index'] = [1]
        data = data.set_index('index')
        ax = data['Close'].plot(x='index',y='Close',style=f'{self.color_map.get(color)}o', ax=ax)
        data['index'] = [2]
        data = data.set_index('index')
        ax = data['Range'].plot(x='index',y='Range',style='mo', ax=ax)
        data['index'] = [3]
        # data = data.set_index('index')
        # ax = data['Derivative EMA14'].plot(x='index',y='Derivative EMA14',style='co', ax=ax)
        # data['index'] = [4]
        # data = data.set_index('index')
        # ax = data['Derivative EMA30'].plot(x='index',y='Derivative EMA30',style='ro', ax=ax)
        # data['index'] = [5]
        # data = data.set_index('index')
        # ax = data['Close EMA14 Diff'].plot(x='index',y='Close EMA14 Diff',style='go', ax=ax)
        # data['index'] = [6]
        # data = data.set_index('index')
        # ax = data['Close EMA30 Diff'].plot(x='index',y='Close EMA30 Diff',style='yo', ax=ax)
        # data['index'] = [7]
        # data = data.set_index('index')
        # ax = data['EMA14 EMA30 Diff'].plot(x='index',y='EMA14 EMA30 Diff',style='bs', ax=ax,title=f'{ticker} - {dates[1]}')
        # data['index'] = [0]
        # data = data.set_index('index')

        for i,row in enumerate(self.data_predict_display.index):
            for j,col in enumerate(self.data_predict_display.columns):
                if j == 8:
                    continue
                y = round(data.iloc[i][j],2)
                ax.text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')

# dis = Display()
# dis.read_studies("2021-03-23--2021-05-12","SPY")
# dis.display_divergence(ticker='SPY', dates=None, color='green')
# locs, labels = plt.xticks()
# dis.display_box()
# # plt.xticks(locs)
# plt.show()