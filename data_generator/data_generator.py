from pathlib import Path
import os
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
import random

'''
    This class allows for unification of data, studies and news for future machine learning training.
    data formatting 
'''
class Generator():
    def __init__(self,ticker,path):
        print(ticker)
        self.studies = Studies(ticker)
        self.news=News_Scraper(ticker)
        self.ticker=ticker
        self.path = path

        
    def generate_data(self):
        self.news.gen_random_dates()
        # Loop until valid data populates
        while self.studies.set_data_from_range(self.news.date_set[0],self.news.date_set[1]) != 0:
            self.news.gen_random_dates()
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
        query_param3 = {"fromDate":"{}".format(self.news.date_set[0].strftime("%Y%m%d%H%M"))}
        query_param4 = {"toDate":"{}".format(self.news.date_set[1].strftime("%Y%m%d%H%M"))}
        query_params = {}
        query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

        self.studies.data = self.studies.data.drop(['Volume'],axis=1)
        self.studies.apply_ema("14",self.news.get_date_difference())
        self.studies.apply_ema("30",self.news.get_date_difference()) 
        self.studies.save_data_csv(f'{self.path}/data/stock_no_tweets/{self.studies.get_indicator()}/{self.news.date_set[0]}--{self.news.date_set[1]}')
    
def choose_random_ticker(csv_file):
    with open(csv_file) as f:
        ticker = random.choice(f.readlines())
        ticker = ticker[0:ticker.find(',')]
        print(ticker)
        return ticker
def main():
    MAX_TICKERS=1
    MAX_ITERS=1
    path = Path(os.getcwd()).parent.absolute()
    for i in range(MAX_TICKERS):
        ticker = choose_random_ticker(f'{path}/data/watchlist/default.csv')
        generator = Generator(ticker,path)
        for j in range(MAX_ITERS):
            generator.generate_data()
        del generator
        
    
if __name__ == '__main__':
    main()