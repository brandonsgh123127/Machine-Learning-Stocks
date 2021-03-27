from pathlib import Path
import os
from data_gather.news_scraper import News_Scraper
from data_gather.studies import Studies
import random
import pytz
import datetime
from tzlocal import get_localzone

class Generator():
    def __init__(self,ticker):
        print("Generator instance")
        self.studies = Studies(ticker)
        self.news=News_Scraper(ticker)
        self.ticker=ticker
        
    def generate_data(self,iters):
        for iter in range(iters):
            self.news.gen_random_dates()
            # Loop until valid data populates
            while self.studies.set_data_from_range(self.news.date_set[0],self.news.date_set[1]) != 0:
                self.news.gen_random_dates()
            path = Path(os.getcwd()).parent.absolute()
            try:
                os.mkdir("{0}/data/tweets".format(path))
            except:
                pass
            try:
                os.mkdir("{0}/data/stock".format(path))
            except:
                pass
            try:
                os.mkdir(f'{path}/data/tweets/{self.news.indicator.upper()}/')
            except:
                pass
            try:
                os.mkdir(f'{path}/data/stock/{self.studies.get_indicator()}/')
            except:
                pass
            try:
                os.mkdir("{0}/data/stock".format(path))
            except:
                pass
            query_param1 = {"query": "{}".format(self.ticker)}
            query_param2 = {"maxResults":"500"}
            query_param3 = {"fromDate":"{}".format(self.news.date_set[0].strftime("%Y%m%d%H%M"))}
            query_param4 = {"toDate":"{}".format(self.news.date_set[1].strftime("%Y%m%d%H%M"))}
            query_params = {}
            query_params.update(query_param1);query_params.update(query_param2);query_params.update(query_param3);query_params.update(query_param4)

            print(self.news.get_news(query_params))
            if self.news.is_empty:
                pass
            else:
                self.news.save_tweet_csv(f'{path}/data/tweets/{self.news.indicator.upper()}/{self.news.date_set[0]}--{self.news.date_set[1]}')
                self.studies.apply_ema("14")
                self.studies.apply_ema("30") 
                self.studies.save_data_csv(f'{path}/data/stock/{self.studies.get_indicator()}/{self.news.date_set[0]}--{self.news.date_set[1]}')
            self.news.reset_results()
    
def choose_random_ticker(csv_file):
    with open(csv_file) as f:
        ticker = random.choice(f.readlines())
        ticker = ticker[0:ticker.find(',')]
        print(ticker)
        return ticker
def main():
    MAX_TICKERS=1
    MAX_ITERS=1
    for i in range(MAX_ITERS):
        ticker = choose_random_ticker("C:\\Users\\i-pod\\git\\Intro--Machine-Learning-Stock\\data\\watchlist\\default.csv")
        generator = Generator(ticker)
        generator.generate_data(MAX_ITERS)
        del generator
        
    
if __name__ == '__main__':
    main()