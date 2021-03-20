from intro._data_gather import Gather
import re
import pandas as pd
import csv

class News_Scraper(Gather):
    def __init__(self):
        Gather.__init__(self)
        self.filtered_results=pd.DataFrame(columns=['hash','text'])
    def _filter_terms(self,tweets):
        _list = {}
        pattern = re.compile(".*?(\\bRobinhood\\b|%|\\bmembers\\b).*")
        for tweet in tweets:
            if not pattern.match(tweet.text):
                self.filtered_results=self.filtered_results.append({'hash':[hash(tweet.id)],'text':[tweet.text]},ignore_index=True)
            else:
                pass
        print(self.filtered_results)
    def load_tweet_csv(self):
        pass
    def save_tweet_csv(self,name):
        pass
    ##start_date - mmddyyyy
    def get_news(self,term,start_date):
        self.filtered_results = self._filter_terms(self.get_recent_news(term,start_date,10))
    def _append_data(self):
        pass

News_Scraper=News_Scraper()
News_Scraper.get_news("SPY","01022021")