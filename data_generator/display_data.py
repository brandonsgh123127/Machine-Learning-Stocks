import matplotlib.pyplot as plt
import pandas as pd
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
from pathlib import Path
import os
import gc
import numpy as np

'''
Easily display unfiltered data given the ticker and date range specified on the file
Class implements matplotlib and pandas
'''
class Display():
    def __init__(self):
        # print("Display instance initialized!")
        self.data_display = pd.DataFrame()
        self.study_display = pd.DataFrame()
        self.keltner_display = pd.DataFrame()
        self.fib_display = pd.DataFrame()
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
        self.fib_display = pd.read_csv(f'{self.path}/data/stock_no_tweets/{ticker}/{date}_fib.csv',index_col=0)
        self.ticker = ticker
        self.date = date
    def read_studies_data(self,predicted=None,actual=None,keltner=None,fib=None):
        self.data_display = actual
        self.data_predict_display = predicted
        if keltner is not None and fib is not None:
            self.keltner_display=keltner
            self.fib_display = fib
        pd.set_option("display.max.columns", None)
    def display_box(self,data=None):
        plt.cla()
        plt.close()
        plt.figure()

        c = 'blue'
        if data is None:
            self.fib_display = pd.DataFrame([self.fib_display.reset_index().to_numpy().reshape(14)],columns={'0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'}).reset_index()
            # self.fib_display = self.fib_display.loc[self.fib_display.index.repeat(len(self.keltner_display.index) + 2)]
            self.fib_display = self.fib_display.reset_index().astype('float')
            self.fib_display['0.202'].transpose().plot.line(color='green',x='0.202',y='0.202')
            self.fib_display['0.236'].transpose().plot.line()
            self.fib_display['0.241'].transpose().plot.line()
            self.fib_display['0.273'].transpose().plot.line()
            self.fib_display['0.283'].transpose().plot.line()
            self.fib_display['0.316'].transpose().plot.line()
            self.fib_display['0.382'].transpose().plot.line()
            self.fib_display['0.5'].transpose().plot.line()
            self.fib_display['0.618'].transpose().plot.line()
            self.fib_display['0.796'].transpose().plot.line()
            self.fib_display['1.556'].transpose().plot.line()
            self.fib_display['3.43'].transpose().plot.line()
            self.fib_display['3.83'].transpose().plot.line()
            self.fib_display['5.44'].transpose().plot.line()

            self.data_display.drop(['Date'],axis=1).transpose().boxplot(patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color=c),
                                                    whiskerprops=dict(color=c),
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c),
                                                    autorange=True).set_alpha(0.3)
            # print(self.keltner_display)
            # self.keltner_display = pd.DataFrame([self.keltner_display.reset_index().to_numpy()],columns={'middle','upper','lower'})
            self.keltner_display = self.keltner_display.reset_index().astype('float').set_axis(['middle','upper','lower'], 1)
            self.keltner_display['middle'].transpose().plot.line()
            self.keltner_display['upper'].transpose().plot.line()
            self.keltner_display['lower'].transpose().plot.line()
        else:
            # print(data)
            # self.fib_display = pd.DataFrame([self.fib_display.reset_index().to_numpy().reshape(15)],columns={'0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'}).reset_index()
            # print(self.fib_display.reset_index(),self.fib_display.columns,self.fib_display.index,flush=True)
            self.fib_display = self.fib_display.reset_index().set_axis(['index','0.202','0.236','0.241','0.273','0.283','0.316','0.382','0.5','0.618','0.796','1.556','3.43','3.83','5.44'], 1)
            # self.fib_display = self.fib_display.loc[self.fib_display.index.repeat(len(self.keltner_display.index) + 2)]
            self.fib_display = self.fib_display.reset_index().astype('float')
            self.fib_display['0.202'].transpose().plot.line(color='green',x='0.202',y='0.202')
            self.fib_display['0.236'].transpose().plot.line()
            self.fib_display['0.241'].transpose().plot.line()
            self.fib_display['0.273'].transpose().plot.line()
            self.fib_display['0.283'].transpose().plot.line()
            self.fib_display['0.316'].transpose().plot.line()
            self.fib_display['0.382'].transpose().plot.line()
            self.fib_display['0.5'].transpose().plot.line()
            self.fib_display['0.618'].transpose().plot.line()
            self.fib_display['0.796'].transpose().plot.line()
            self.fib_display['1.556'].transpose().plot.line()
            self.fib_display['3.43'].transpose().plot.line()
            self.fib_display['3.83'].transpose().plot.line()
            self.fib_display['5.44'].transpose().plot.line()
            data.transpose().boxplot(patch_artist=True,
                                              boxprops=dict(facecolor=(0.1,0.5,0.4,0.5)),
                                                    capprops=dict(color=c),
                                                    showfliers=False,
                                                    showcaps=False,
                                                    flierprops=dict(color=c, markeredgecolor=c),
                                                    medianprops=dict(color=c),
                                                    autorange=True).set_alpha(0.3)
            self.keltner_display = self.keltner_display.astype('float')
            self.keltner_display['middle'].transpose().plot.line()
            self.keltner_display['upper'].transpose().plot.line()
            self.keltner_display['lower'].transpose().plot.line()
            # self.fib_display.reindex_like(self.data_display).transpose().plot.line()

    def display_divergence(self,ticker=None,dates=None,color=None,has_actuals=False):
        plt.cla()
        plt.figure()
        data = self.data_predict_display.reset_index()
        data.transpose().plot(kind='line',color=color)
    def display_line(self,ticker=None,dates=None,color='g'):
        indices_dict = {0:'Open',1:'Close',2:'Range'}
        self.data_display = pd.concat([self.data_display.reset_index(),self.data_predict_display.reset_index()],ignore_index=False).set_flags(allows_duplicate_labels=True)
        self.data_display['index'] = [0,0]
        self.data_display = self.data_display.set_index('index')
        ax = self.data_display['Open'].plot(x='index',y='Open',style=f'{self.color_map.get(color)}x')
        self.data_display['index'] = [1,1]
        self.data_display = self.data_display.set_index('index')
        ax = self.data_display['Close'].plot(x='index',y='Close',style=f'{self.color_map.get(color)}o', ax=ax)
        self.data_display['index'] = [2,2]
        self.data_display = self.data_display.set_index('index')
        ax = self.data_display['Range'].plot(x='index',y='Range',style='mo', ax=ax)
        self.data_display['index'] = [3,3]

        for i,row in enumerate(self.data_display.index):
            for j,col in enumerate(self.data_display.columns):
                if j == 8:
                    continue
                if i == 0:
                    y = round(self.data_display.iloc[i][j],2)
                    ax.text(j, y, f'{indices_dict.get(j)} - A {y}',size='x-small')
                else:
                    y = round(self.data_display.iloc[i][j],2)
                    ax.text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')
    def display_predict_only(self,ticker=None,dates=None,color=None):
        indices_dict = {0:'Open',1:'Close',2:'Range'}
        self.data_predict_display['index'] = [0]
        self.data_predict_display = self.data_predict_display.set_index('index')
        ax = self.data_predict_display['Open'].plot(x='index',y='Open',style=f'{self.color_map.get(color)}x')
        self.data_predict_display['index'] = [1]
        self.data_predict_display = self.data_predict_display.set_index('index')
        ax = self.data_predict_display['Close'].plot(x='index',y='Close',style=f'{self.color_map.get(color)}o', ax=ax)
        self.data_predict_display['index'] = [2]
        data = self.data_predict_display.set_index('index')
        ax = data['Range'].plot(x='index',y='Range',style='mo', ax=ax)
        data['index'] = [3]

        for i,row in enumerate(self.data_predict_display.index):
            for j,col in enumerate(self.data_predict_display.columns):
                if j == 8:
                    continue
                y = round(data.iloc[i][j],2)
                ax.text(j, y, f'{indices_dict.get(j)} - P {y}',size='x-small')

# dis = Display()
# dis.read_studies("2021-06-22--2021-08-12","SPY")
# dis.display_divergence(ticker='SPY', dates=None, color='green')
# locs, labels = plt.xticks()
# dis.display_box()
# # plt.xticks(locs)
# plt.show()