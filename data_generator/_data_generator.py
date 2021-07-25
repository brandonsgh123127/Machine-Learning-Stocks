from pathlib import Path
import os
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
import random
import datetime
from json.decoder import JSONDecodeError
'''
    This class allows for unification of data, studies and news for future machine learning training.
    data formatting 
'''
class Generator():
    def __init__(self,ticker,path):
        # print(ticker)
        self.studies = Studies(ticker)
        self.news=News_Scraper(ticker)
        self.ticker=ticker
        self.path = path

        
    def generate_data(self):
        self.studies.gen_random_dates()
        # Loop until valid data populates
        while self.studies.set_data_from_range(self.studies.date_set[0],self.studies.date_set[1]) != 0 or self.studies.data.isnull().values.any() or len(self.studies.data) < 16:
            self.studies.gen_random_dates()
        try:
            os.mkdir("{0}/data/tweets".format(self.path))
        except:
            pass
        try:
            os.mkdir("{0}/data/stock_no_tweets".format(self.path))
        except:
            pass
        try:
            os.mkdir(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/')
        except:
            pass
        try:
            os.mkdir("{0}/data/stock".format(self.path))
        except:
            pass
        # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
        query_param1 = {"query": "{}".format(self.ticker)}
        query_param2 = {"maxResults":"500"}
        query_param3 = {"fromDate":"{}".format(self.studies.date_set[0].strftime("%Y%m%d%H%M"))}
        query_param4 = {"toDate":"{}".format(self.studies.date_set[1].strftime("%Y%m%d%H%M"))}
        query_params = {}
        query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

        self.studies.data = self.studies.data.drop(['Volume'],axis=1)

        self.studies.apply_ema("14",self.studies.get_date_difference())
        self.studies.apply_ema("30",self.studies.get_date_difference()) 
        self.studies.keltner_channels(20, 1.3, None)

        try:
            os.remove(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/{self.studies.date_set[0]}--{self.studies.date_set[1]}')
        except:
            pass
        self.studies.save_data_csv(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/{self.studies.date_set[0]}--{self.studies.date_set[1]}')
        self.studies.reset_data()
        
    def generate_data_with_dates(self,date1=None,date2=None,is_not_closed=False,vals:tuple=None):
        self.studies.date_set = (date1,date2)
        # Loop until valid data populates
        try:
            # self.studies.set_data_from_range(date1,date2)
            self.studies.set_data_from_range(self.studies.date_set[0],self.studies.date_set[1])
        except Exception as e:
            print(f'[ERROR] Failed to generate data!',str(e))
            raise Exception
        if is_not_closed:
            self.studies.data = self.studies.data.append({'Open': f'{vals[0]}','High': f'{vals[1]}','Low': f'{vals[2]}','Close': f'{vals[3]}','Adj Close': f'{vals[3]}'}, ignore_index=True)
        try:
            os.mkdir("{0}/data/tweets".format(self.path))
        except:
            pass
        try:
            os.mkdir("{0}/data/stock_no_tweets".format(self.path))
        except:
            pass
        try:
            os.mkdir(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/')
        except:
            pass
        try:
            os.mkdir("{0}/data/stock".format(self.path))
        except:
            pass
        # JSON PARAMETERS NEEDED TO BE PASSED TO TWITTER API
        query_param1 = {"query": "{}".format(self.ticker)}
        query_param2 = {"maxResults":"500"}
        query_param3 = {"fromDate":"{}".format(self.studies.date_set[0].strftime("%Y%m%d%H%M"))}
        query_param4 = {"toDate":"{}".format(self.studies.date_set[1].strftime("%Y%m%d%H%M"))}
        query_params = {}
        query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

        self.studies.data = self.studies.data.drop(['Volume'],axis=1)
        
        self.studies.apply_ema("14",self.studies.get_date_difference())
        self.studies.apply_ema("30",self.studies.get_date_difference()) 
        self.studies.keltner_channels(20, 1.3, None)
        
        try:
            os.remove(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/{date1.strftime("%Y-%m-%d")}--{date2.strftime("%Y-%m-%d")}')
        except:
            pass
        self.studies.save_data_csv(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/{date1.strftime("%Y-%m-%d")}--{date2.strftime("%Y-%m-%d")}')
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
    MAX_TICKERS=10
    MAX_ITERS=50
    path = Path(os.getcwd()).parent.absolute()
    for i in range(MAX_TICKERS):
        ticker = choose_random_ticker(f'{path}/data/watchlist/default.csv')
        # ticker="SPY"
        generator = Generator(ticker,path)
        # generator.generate_data_with_dates(datetime.datetime(2021,3,3),datetime.datetime(2021,4,22))
        for j in range(MAX_ITERS):
            try:
                generator.generate_data()
            except:
                pass
        del generator
        
    
if __name__ == '__main__':
    main()