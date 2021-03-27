from data_gather._data_gather import Gather
import re
import pandas as pd
import os,sys
from pathlib import Path
import json
from pandas.io.json import json_normalize

''' Class used for news data utilization from twitter api'''
class News_Scraper(Gather):
    def __repr__(self):
        return 'stock_data.news_scraper object <%s>' % ",".join(self.indicator)

    def __init__(self,ticker):
        Gather.__init__(self)
        self.filtered_results=pd.DataFrame(columns=['hash','text','date','user'])
        self.set_indicator(ticker)
        self.is_empty=True
    def get_results(self):
        return self.filtered_results
    def reset_results(self):
        self.filtered_results=pd.DataFrame()
    def load_tweet_csv(self,path):
        try:
            self.filtered_results = pd.read_csv(path)
        except:
            print("CSV empty, continuing...")
        return 0
    def save_tweet_csv(self,path):
        self.filtered_results.to_csv("{0}_tweets.csv".format(path),index=False,sep=',')
        return 0
    ##start_date - mmddyyyy
    def get_news(self,query):
        self.is_empty=True
        return self._filter_terms(self.get_recent_news(query))
    # Simple regex filter for disregard values
    def _filter_terms(self,tweets):
        pattern = re.compile(".*?(\\brobinhood\\b|%|\\bmembers\\b|@|\\blist\\b|\\bpicks\\b).*")
        print(tweets)
        if not tweets:
            self.filtered_results = pd.DataFrame(columns=['hash','text','ext_tweet','date','user'])
            self.is_empty=False
        for tweet in tweets["results"]:
            if not pattern.match(tweet["text"].lower()) and not self.filtered_results.hash.isin([hash(tweet['id_str'])]).any().any() and len(tweet["extended_tweet"]["full_text"]) < 225 and len(tweet["entities"]["symbols"]["text"])>0:
                self.filtered_results=self.filtered_results.append({'hash':hash(tweet["id_str"]),'tweet':tweet["text"].replace('\n',''),'ext_tweet':tweet["extended_tweet"]["full_text"].replace('\n',''),'date':tweet["created_at"],'user':tweet["user"]["id_str"]},ignore_index=True)
            else:
                pass
        return self.filtered_results
