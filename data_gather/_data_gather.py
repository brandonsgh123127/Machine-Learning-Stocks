import numpy as np
from matplotlib import pyplot as plt
import yfinance as yf
import datetime
from pandas_datareader import data as pdr
import twitter
import random

'''Class Used for Gathering data through yfinance...
'''
class Gather():
    MAX_DATE = datetime.datetime.now().date()
    MIN_DATE = datetime.datetime(2013,1,1).date()
    MIN_RANGE = 5 # at least 5 days generated
    DAYS_IN_MONTH = {1:31,
                     2:28,
                     2:31,
                     4:30,
                     5:31,
                     6:30,
                     7:31,
                     8:31,
                     9:30,
                     10:31,
                     11:30,
                     12:31}
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
        self.data = []
        self.date_set = ()
        
    def set_indicator(self,indicator):
        self.indicator = indicator
    def get_indicator(self):
        return self.indicator    
    #For ease of data automation, we want to pass in randomized numbers without any special characters (mmddyyyy)
    def _convert_mdY_Ymd(self,date):
        return datetime.datetime.strptime(date,"%m%d%Y").strftime("%Y-%m-%d")
    # retrieve pandas_datareader object of data mmddyyyy to yyyymmdd
    def set_data_from_range(self,start_date,end_date):
        formatted_dates = (self._convert_mdY_Ymd(start_date),self._convert_mdY_Ymd(end_date))
        self.data = pdr.get_data_yahoo(self.indicator,start=formatted_dates[0],end=formatted_dates[1])
        return self.data
    # Generate random date for data generation
    def gen_random_dates(self):
        calc_leap_day = lambda year_month: random.randint(1,29) if year_month[1]==2 and ((year_month[0]%4==0 and year_month[0]%100==0 and year_month[0]%400==0) or (year_month[0]%4==0 and year_month[0]%100!=0)) else random.randint(1,28) if year_month[1]==2 else random.randint(1,self.DAYS_IN_MONTH[year_month[1]])
        set1 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year),random.randint(1,12))
        set2 = (random.randint(self.MAX_DATE.year,self.MAX_DATE.year),random.randint(1,12))
        self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1)).date(),datetime.datetime(set2[0],set2[1],calc_leap_day(set2)).date())
        while abs(self.date_set[0].timetuple().tm_yday - self.date_set[1].timetuple().tm_yday) < self.MIN_RANGE: # abs value 
            print("Calculating new day, less than range")
            self.date_set[0].replace(day=calc_leap_day(set1))
        return self.date_set
    def get_data(self):
        return self.data
    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self,term,date,amt=100):
        print(f'Retrieving news using Twitter API... {term} {date} {amt}') 
        format_date=self._convert_mdY_Ymd(date)
        results = self.api.GetSearch(
            raw_query=f'q=%24{term}%20min_faves%3A0%20&result_type=mixed%20&since={format_date}%20&count={amt}'
            )
        return results
        
    