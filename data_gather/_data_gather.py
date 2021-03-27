import numpy as np
from matplotlib import pyplot as plt
import yfinance as yf
import datetime
from pandas_datareader import data as pdr
import twitter
import random
import pytz

import requests
import os
import json
'''Class Used for Gathering data through yfinance...
'''
class Gather():
    MAX_DATE = datetime.datetime.now().date()
    MIN_DATE = datetime.datetime(2013,1,1).date()
    MIN_RANGE = 5 # at least 5 days generated
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
    search_url = "https://api.twitter.com/1.1/search/fullarchive/dev/counts.json"

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
        self.bearer="AAAAAAAAAAAAAAAAAAAAAJdONwEAAAAAzi2H1WrnhmAddAQKwveAfRN1DAY%3DdSFsj3bTRnDqqMxNmnxEKTG6O6UN3t3VMtnC0Y7xaGxqAF1QVq"
        self.headers = {"Authorization": "Bearer {0}".format(self.bearer)}
    def set_indicator(self,indicator):
        self.indicator = indicator
    def get_indicator(self):
        return self.indicator    
    # retrieve pandas_datareader object of datetime
    def set_data_from_range(self,start_date,end_date):
        try:
            self.data = pdr.get_data_yahoo(self.indicator,start=start_date.strftime("%Y-%m-%d"),end=end_date.strftime("%Y-%m-%d"))
        except:
            return 1
        return 0
    def _reorder_dates(self,date1,date2):
        if date1 < date2:
            return (date1,date2) 
        else:
            return (date2,date1)
    # Generate random date for data generation
    def gen_random_dates(self):
        calc_leap_day = lambda year_month: random.randint(1,29) if year_month[1]==2 and ((year_month[0]%4==0 and year_month[0]%100==0 and year_month[0]%400==0) or (year_month[0]%4==0 and year_month[0]%100!=0)) else random.randint(1,28) if year_month[1]==2 else random.randint(1,self.DAYS_IN_MONTH[year_month[1]])
        set1 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year),random.randint(1,12))
        set2 = (random.randint(self.MIN_DATE.year,self.MAX_DATE.year),random.randint(1,12))
        self.date_set = (datetime.datetime(set1[0],set1[1],calc_leap_day(set1),tzinfo=pytz.utc),datetime.datetime(set2[0],set2[1],calc_leap_day(set2),tzinfo=pytz.utc))
        while abs(self.date_set[0].timestamp() - self.date_set[1].timestamp()) < self.MIN_RANGE: # abs value 
            print(self.date_set[0],self.date_set[1])
            print("Calculating new day, less than range")
            self.date_set[0].replace(day=calc_leap_day(set1))
        self.date_set=self._reorder_dates(self.date_set[0].date(),self.date_set[1].date())
        return self.date_set
    def get_data(self):
        return self.data
    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self,query):
        response = requests.request("GET", self.search_url, headers=self.headers, params=query)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()
