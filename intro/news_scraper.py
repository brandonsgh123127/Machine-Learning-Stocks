from intro._data_gather import Gather
import re
import pandas as pd
import csv,os,sys

''' Class used for news data utilization from twitter api'''
class News_Scraper(Gather):
    def __repr__(self):
        return 'stock_data.news_scraper object <%s>' % ",".join(self.indicator)

    def __init__(self):
        Gather.__init__(self)
        self.filtered_results=pd.DataFrame(columns=['hash','text'])
    # Simple regex filter for disregard values
    def _filter_terms(self,tweets):
        _list = {}
        pattern = re.compile(".*?(\\bRobinhood\\b|%|\\bmembers\\b).*")
        for tweet in tweets:
            if not pattern.match(tweet.text) and not self.filtered_results.hash.isin([hash(tweet.id)]).any().any():
                self.filtered_results=self.filtered_results.append({'hash':hash(tweet.id),'text':tweet.text.replace('\n','')},ignore_index=True)
            else:
                pass
    def load_tweet_csv(self,path):
        try:
            self.filtered_results = pd.read_csv(path)
        except:
            print("CSV empty, continuing...")
        return 0
    def save_tweet_csv(self,path):
        self.filtered_results.to_csv(path,index=False,sep=',')
        return 0
    ##start_date - mmddyyyy
    def get_news(self,term,start_date):
        self.set_indicator(term)
        self._filter_terms(self.get_recent_news(term,start_date,amt=10))
    def _append_data(self):
        pass

news=News_Scraper()
news.load_tweet_csv(f':\\Users\\i-pod\\git\\{news.indicator.upper()}.csv')
news.get_news("AMD","01022021")
print(news.get_indicator())
news.save_tweet_csv(f'C:\\Users\\i-pod\\git\\{news.indicator.upper()}.csv')
print('done')