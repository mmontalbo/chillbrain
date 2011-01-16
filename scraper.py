from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from urllib2 import Request, urlopen, URLError
from StringIO import StringIO
from django.utils import simplejson as json

from collections import deque
import re
import logging
import hashlib
import time
import efpmodel

class Scraper():
    MAX_IMGS_TO_FETCH = 50
    MAX_FIELD_LENGTH = 500
    MAX_RETRY_COUNT = 5
    skipWords = ["nsfw","nsfl","reddit"]

    def __init__(self, url):
        self.scrapeURL = url
        self.pattern = re.compile("(.*).jpg|gif|png")

    def startScraping(self):
        count = 0
        links = deque()
        links.append(self.scrapeURL)
        retry = 0

        while(len(links) > 0 and count < MAX_IMGS_TO_FETCH):
            time.sleep(0.2)
            link = links.pop()
            logging.debug("Requesting url: "+link+"...");
            response = urlfetch.Fetch(link).content
            nextLinks = self.parse(response)
            if len(nextLinks) == 0 and retry < MAX_RETRY_COUNT:
                links.append(link)
                retry = retry + 1
                time.sleep(1)
            else:
                retry = 0
                links.extend(nextLinks)

    def download(self, params):
        for k,v in params:
            params[k] = self.truncateField(v)
            
        if(self.pattern.search(params['url'])):
            if (self.isUnsavedURL(params['url']) and self.isValidTitle(params['title'])):
                logging.debug("Queueing download of "+params['url']+"...")
                taskqueue.add(url='/worker', params})
            else:
                logging.debug("Skipping invalid link: "+params['title']);

    def truncateField(self, field):
        if(len(field) > MAX_FIELD_LENGTH):
            return field[:MAX_FIELD_LENGTH-1]
        else:
            return field

    def filterTitle(self, title):
        filterWords = ["[pic]","(pic)","{pic}"]
        for word in filterWords:
            title = title.replace(word.lower(),"")
            title = title.replace(word.upper(),"")
        return title

    def isValidTitle(self, title):
        for word in self.skipWords:
            if(title.lower().find(word) != -1):
                logging.debug(">>Filtering out "+title+"<<<")
                return False
        return True

    def isUnsavedURL(self, url):
        return len(Image.gql("WHERE url=:1",params['url']).fetch(1)) == 0

class RedditScraper(Scraper):
    MAX_LEN = 25
    REDDIT_URL = "http://reddit.com"
    SUBREDDIT_URL = REDDIT_URL + "/r/"
    REDDIT_JSON = "/.json?&after="

    def __init__(self, subreddit):
        super(SUBREDDIT_URL+subreddit+REDDIT_JSON)

    def parse(self, response):
        responseDict = json.loads(response)
        nextLinks = []
        for child in responseDict["data"]["children"]:
            try:
                params {'url':child['data']['url'],
                'source':SUBREDDIT_URL + child['data']['subreddit'],
                'title':self.filterTitle(child['data']['title']),
                'permalink':REDDIT_URL + child['data']['permalink']
                }
                self.download(params)
                nextLinks.append(child['data']['name'])
            except ValueError, e:
                logging.error("Failed to decode JSON: "+response)
            except URLError, e:
                logging.error("Failed to reach a server.")
            except Exception, e:
                logging.error("Failed to request url: "+str(type(e)))
        return nextLinks
    
class ScrapeWorker(webapp.RequestHandler):
    validContentTypes = ['jpeg','jpg','png','gif']

    def post(self):
        def txn():
            try:
                url = self.request.get('url')
                response = urlfetch.Fetch(url)
                if response.headers['Content-Type'] is in validContentTypes:
                    data = response.content
                    hashKey = hashlib.sha1(data).hexdigest()
                    k = db.Key.from_path('Image', hashKey)

                    if(efpmodel.Image.get(k) is None):
                        img = efpmodel.Image(key=k)
                        img.imageData = efpmodel.db.Blob(data)
                        img.url = url
                        img.title = self.request.get('title')
                        img.source = self.request.get('source')
                        img.put()
                        logging.info("Successfully saved: "+url)
                    else:
                        logging.info("Skipping already stored image: "+url)
                else:
                    logging.debug("Skipping non-jpeg file: "+url)
            except urlfetch.Error, e:
                logging.error("Failed to request image url:"+str(type(e)))
            except db.Error, e:
                logging.error("Failed to put image url:"+str(type(e)))
                   
        efpmodel.db.run_in_transaction(txn)

class ScrapeService(webapp.RequestHandler):
    def post(self):
        logging.info("Starting scraper...")
        redditScraper = RedditScraper(self.request.get('subreddit'))
        redditScraper.startScraping()

    def get(self):
        subReddits = ["pics","funny","wtf","adviceanimals"]
        count = 0
        for subReddit in subReddits:
            taskqueue.add(url='/scrape',params={'subreddit':subReddit},countdown=(count*30)+3)
            count = count + 1
        self.response.out.write("<html><body>Started scraping...")
        self.response.out.write("</body></html>")
                
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/scrape',ScrapeService),
                                          ('/worker',ScrapeWorker)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
