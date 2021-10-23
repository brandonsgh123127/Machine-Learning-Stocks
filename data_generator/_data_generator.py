from pathlib import Path
import os
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
import random
from threading_impl.Thread_Pool import Thread_Pool
import threading
import time
import datetime
'''
    This class allows for unification of data, studies and news for future machine learning training.
    data formatting 
'''
class Generator():
    def __init__(self,ticker,path=None):
        # print(ticker)
        self.studies = Studies(ticker)
        self.news=News_Scraper(ticker)
        self.ticker=ticker
        if path is not None:
            self.path = path
        else:
            self.path = Path(os.getcwd()).parent.absolute()

        
    def generate_data(self):
        # studies.__init__()
        with threading.Lock():
            studies = Studies(self.ticker)
            dates = studies.gen_random_dates()
            # Loop until valid data populates
            try:
                while studies.get_data(studies.date_set[0],studies.date_set[1]) != 0 or studies.data.isnull().values.any() or len(studies.data) < 16:
                    # print("looping...",flush=True)
                    studies.gen_random_dates()
            except RuntimeError:
                pass

            # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
            query_param1 = {"query": "{}".format(self.ticker)}
            query_param2 = {"maxResults":"500"}
            query_param3 = {"fromDate":"{}".format(studies.date_set[0].strftime("%Y%m%d%H%M"))}
            query_param4 = {"toDate":"{}".format(studies.date_set[1].strftime("%Y%m%d%H%M"))}
            query_params = {}
            query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)
        try:
            studies.data = studies.data.drop(['Volume'],axis=1)
            studies.reset_data()
            studies.load_data_mysql(dates[0],dates[1])
            studies.apply_ema("14",self.studies.get_date_difference())
            studies.load_data_mysql(dates[0],dates[1])
            studies.apply_ema("30",self.studies.get_date_difference())
            studies.keltner_channels(20, 1.3, None)
        except Exception as e:
            # raise Exception("[ERROR] Exception:\n{}".format(str(e)))
            return  
        try:
            os.remove(f'{self.path}/data/stock_no_tweets/{studies.get_indicator()}/{studies.date_set[0]}--{studies.date_set[1]}')
        except:
            pass
        studies.save_data_csv(f'{self.path}/data/stock_no_tweets/{studies.get_indicator()}/{studies.date_set[0]}--{studies.date_set[1]}')
        del studies
        
        # Generates the P/L and percent of current day
    def generate_quick_data(self):
        if datetime.date.today().weekday() == 5:
            self.studies.set_data_from_range(datetime.datetime.today() - datetime.timedelta(days=2) , datetime.datetime.today()- datetime.timedelta(days=1))
        elif datetime.date.today().weekday() == 6:
            self.studies.set_data_from_range(datetime.datetime.today() - datetime.timedelta(days=3) , datetime.datetime.today()- datetime.timedelta(days=2))
        else:
            self.studies.set_data_from_range(datetime.datetime.today() - datetime.timedelta(days=1) , datetime.datetime.today())
        return [self.studies.data[['Close']].diff().iloc[1].to_list()[0],f'{round(self.studies.data[["Close"]].pct_change().iloc[1].to_list()[0]*100,3)}%']
    def generate_data_with_dates(self,date1=None,date2=None,is_not_closed=False,vals:tuple=None):
        self.studies.date_set = (date1,date2)
        # Loop until valid data populates
        try:
            # self.studies.get_data(date1,date2)
            self.studies.get_data(self.studies.date_set[0],self.studies.date_set[1])
            self.studies.data = self.studies.data.reset_index()
            # self.studies.data = self.studies.data.drop(['Date'],axis=1)
        except Exception as e:
            print(f'[ERROR] Failed to generate data!',str(e))
            raise Exception
        if is_not_closed:
            self.studies.data = self.studies.data.append({'Open': f'{vals[0]}','High': f'{vals[1]}','Low': f'{vals[2]}','Close': f'{vals[3]}','Adj Close': f'{vals[3]}'}, ignore_index=True)
        # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
        query_param1 = {"query": "{}".format(self.ticker)}
        query_param2 = {"maxResults":"500"}
        query_param3 = {"fromDate":"{}".format(self.studies.date_set[0].strftime("%Y%m%d%H%M"))}
        query_param4 = {"toDate":"{}".format(self.studies.date_set[1].strftime("%Y%m%d%H%M"))}
        query_params = {}
        query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

        self.studies.data = self.studies.data.drop(['Volume'],axis=1)
        # print(self.studies.data)
        
        self.studies.apply_ema("14",self.studies.get_date_difference())
        self.studies.apply_ema("30",self.studies.get_date_difference()) 
        self.studies.apply_fibonacci()
        self.studies.keltner_channels(20, 1.3, None)
        self.studies.reset_data()
        self.studies = Studies(self.ticker)
    def get_ticker(self):
        return self.ticker
    def set_ticker(self,ticker):
        self.ticker = ticker
def choose_random_ticker(csv_file):
    with open(csv_file) as f:
        ticker = random.choice(f.readlines())
        ticker = ticker[0:ticker.find(',')]
        print(ticker)
        return ticker
def main():
    MAX_TICKERS=500
    MAX_ITERS=1
    path = Path(os.getcwd()).parent.absolute()
    for i in range(MAX_TICKERS):
        ticker = choose_random_ticker(f'{path}/data/watchlist/default.csv')
        # ticker="SPY"
        generator = Generator(ticker,path)
        try:
            with threading.Lock():
                try:
                    os.mkdir("{0}/data/tweets".format(path))
                except:
                    pass
                try:
                    os.mkdir("{0}/data/stock_no_tweets".format(path))
                except:
                    pass 
                try:
                    os.mkdir(f'{path}/data/stock_no_tweets/{ticker}/')
                except:
                    pass 
                os.mkdir("{0}/data/stock".format(path))
        except:
            pass
        # generator.generate_data_with_dates(datetime.datetime(2021,3,3),datetime.datetime(2021,4,22))
        s_time = time.time()
        for j in range(MAX_ITERS):
            generator.generate_data()
        e_time = time.time() - s_time
        print(e_time)
        del generator
        
    
if __name__ == '__main__':
    main()
    # generator = Generator("SPY",None)
    # print(generator.generate_quick_data())