from intro._data_gather import Gather

class News_Scraper(Gather):
    def __init__(self):
        Gather.__init__(self)
        self.filtered_results=()
    def _filter_terms(self,tweets):
        for tweet in tweets:
            print(tweet.text)
    ##start_date - mmddyyyy
    def get_news(self,term,start_date):
        self.filtered_results = self._filter_terms(self.get_recent_news(term,start_date,10))

News_Scraper=News_Scraper()
News_Scraper.get_news("AMD","01022021")