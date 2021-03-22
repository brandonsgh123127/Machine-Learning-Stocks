import numpy as np
from matplotlib import pyplot as plt
import yfinance as yf
import datetime
from pandas_datareader import data as pdr
import twitter

'''Class Used for Gathering data through yfinance...
'''
class Gather():
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
        
    def set_indicator(self,indicator):
        self.indicator = indicator
    def get_indicator(self):
        return self.indicator    
    #For ease of data automation, we want to pass in randomized numbers without any special characters (mmddyyyy)
    def _convert_mdY_Ymd(self,date):
        return datetime.datetime.strptime(date,"%m%d%Y").strftime("%Y-%m-%d")
    # retrieve pandas_datareader object of data mmddyyyy to yyyymmdd
    def get_data_from_range(self,start_date,end_date):
        formatted_dates = (self._convert_mdY_Ymd(start_date),self._convert_mdY_Ymd(end_date))
        return pdr.get_data_yahoo(self.indicator,start=formatted_dates[0],end=formatted_dates[1])
    # Twitter API Web Scraper for data on specific stocks
    def get_recent_news(self,term,date,amt=100):
        print(f'Retrieving news using Twitter API... {term} {date} {amt}') 
        format_date=self._convert_mdY_Ymd(date)
        results = self.api.GetSearch(
            raw_query=f'q=%24{term}%20min_faves%3A0%20&result_type=mixed%20&since={format_date}%20&count={amt}'
            )
        return results
        
    