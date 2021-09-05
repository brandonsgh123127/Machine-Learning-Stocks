import yfinance as yf
import datetime
from pandas_datareader import data as pdr
import pandas as pd
import twitter
import random
import pytz
import os,sys
import requests
import threading
import mysql.connector
import time


'''CORE CLASS IMPLEMENTATION--

    Gather class allows for basic functions within other modules, these functions are:
    date retrieval
    stock retrieval
    news retrieval through twitter api
    
'''
class Gather():
    
    MAX_DATE = datetime.datetime.now().date()
    MIN_DATE = datetime.datetime(2013,1,1).date()
    MIN_RANGE = 50 # at least 7 days generated
    MAX_RANGE = 75 # at most 1 month to look at trend
    DAYS_IN_MONTH = {1:31,
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
    search_url = "https://api.twitter.com/1.1/tweets/search/fullarchive/dev.json"

    def __repr__(self):
        return 'stock_data.gather_data object <%s>' % ",".join(self.indicator)
    def __init__(self):
        yf.pdr_override()
        # Local API Key for twitter account
        self.api = twitter.Api(consumer_key="wQ6ZquVju93IHqNNW0I4xn4ii",
                          consumer_secret="PorwKI2n1VpHznwyC38HV8a9xoDMWko4mOIDFfv2q7dQsFn2uY",
                          access_token_key="1104618795115651072-O3LSWBFVEPENGiTnXqf7cTtNgmNqUF",
                          access_token_secret="by7SUTtNPOYgAws0yliwk9YdiWIloSdv8kYX0YKic28UE",
                          sleep_on_rate_limit="true")
        self.indicator = ""
        self.data : pdr.DataReader= None
        self.options : pd.DataFrame = None
        self.date_set = ()
        self.bearer="AAAAAAAAAAAAAAAAAAAAAJdONwEAAAAAzi2H1WrnhmAddAQKwveAfRN1DAY%3DdSFsj3bTRnDqqMxNmnxEKTG6O6UN3t3VMtnC0Y7xaGxqAF1QVq"
        self.headers = {"Authorization": "Bearer {0}".format(self.bearer), "content-type": "application/json",'Accept-encoding': 'gzip',
               'User-Agent': 'twitterdev-search-tweets-python/'}
    def set_indicator(self,indicator):
        with threading.Lock():
            self.indicator = indicator
    def get_indicator(self):
        with threading.Lock():
            return self.indicator    
    # retrieve pandas_datareader object of datetime
    def get_data(self,start_date,end_date):
        # print(self.indicator,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"))
        # print(pdr.get_data_yahoo("SPY",start=start_date.strftime("%Y-%m-%d"),end=end_date.strftime("%Y-%m-%d")))
        with threading.Lock():
            try:
                sys.stdout = open(os.devnull, 'w')
                self.data = pdr.get_data_yahoo(self.indicator,start=start_date.strftime("%Y-%m-%d"),end=end_date.strftime("%Y-%m-%d"))
                sys.stdout = sys.__stdout__
            except:
                time.sleep(300) # Sleep since API is does not want to communicate
        if self.data.empty:
            raise Exception("[ERROR] Data is empty!\nDates:{} -- {}".format(start_date,end_date))
        return 0
    def _reorder_dates(self,date1,date2):
        if date1 < date2:
            return (date1,date2) 
        else:
            return (date2,date1)
    def get_option_data(self):
        with threading.Lock():
            try:
                # sys.stdout = open(os.devnull, 'w')
                ticker = yf.Ticker(self.indicator)
                exps = ticker.options
                # Get options for each expiration
                options = pd.DataFrame()
                for e in exps:
                    if (datetime.datetime.strptime(e,'%Y-%m-%d') - datetime.datetime.today()).days < 7:
                        opt = ticker.option_chain(e)
                        opt = pd.DataFrame().append(opt.calls).append(opt.puts)
                        opt['expirationDate'] = e
                        options = options.append(opt, ignore_index=True)
                    else:
                        break
                # Bizarre error in yfinance that gives the wrong expiration date
                # Add 1 day to get the correct expiration date
                options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days = 1)
                options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
                
                # Boolean column if the option is a CALL
                options['CALL'] = options['contractSymbol'].str[4:].apply(
                    lambda x: "C" in x)
                
                options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
                options['mark'] = (options['bid'] + options['ask']) / 2 # Calculate the midpoint of the bid-ask
                
                # Drop unnecessary and meaningless columns
                self.options = options.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])
                # sys.stdout = sys.__stdout__
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(str(e))
                time.sleep(300) # Sleep since API is does not want to communicate
        return 0
    # Generate random date for data generation
    def gen_random_dates(self):
        with threading.Lock():
            calc_leap_day = lambda year_month: random.randint(1,29) if year_month[1]==2 and ((year_month[0]%4==0 and year_month[0]%100==0 and year_month[0]%400==0) or (year_month[0]%4==0 and year_month[0]%100!=0)) else random.randint(1,28) if year_month[1]==2 else random.randint(1,self.DAYS_IN_MONTH[year_month[1]])
            set1 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year - 1),random.randint(1,12))
            set2 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year - 1),(set1[1]+2)%12 + 1)
            self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc),datetime.datetime(set2[0],set2[1],calc_leap_day(set2),tzinfo=pytz.utc))
            # date difference has to be in between range 
            while abs(self.date_set[0].timestamp() - self.date_set[1].timestamp()) < (self.MIN_RANGE *86400) or abs(self.date_set[0].timestamp() - self.date_set[1].timestamp()) > (self.MAX_RANGE * 86400):
                n_list= (set1[0],random.randint(1,12))
                self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc),datetime.datetime(n_list[0],n_list[1],calc_leap_day(n_list),tzinfo=pytz.utc))
            if self.date_set[0] > datetime.datetime.now().replace(tzinfo=pytz.utc):
                self.date_set = (datetime.datetime.now().replace(month = 1, day=1,tzinfo=pytz.utc),self.date_set[1])
            if self.date_set[1] > datetime.datetime.now().replace(tzinfo=pytz.utc):
                self.date_set = (self.date_set[0],datetime.datetime.now().replace(month=3,day=int(datetime.datetime.today().strftime('%d')), tzinfo=pytz.utc))
            self.date_set=self._reorder_dates(self.date_set[0].date(),self.date_set[1].date())
            return self.date_set
    def get_date_difference(self,date1=None,date2=None):
        with threading.Lock():
            if date1 is None:
                return (self.date_set[0] - self.date_set[1]).days
            else:
                return (date2 - date1).days
    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self,query):
        response = requests.post(self.search_url,json=query, headers=self.headers)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()


g = Gather()
g.set_indicator('SPY')
g.get_option_data()
print(g.options.columns)