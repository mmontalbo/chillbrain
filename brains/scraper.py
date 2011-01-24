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
from brains.feed import *
from model import cbmodel
from config import sources

class Scraper(object):
    def __init__(self, url):
        Scraper.MAX_DEQUE_LENGTH = 20
        Scraper.MAX_IMGS_TO_FETCH = 25
        Scraper.MAX_FIELD_LENGTH = 500
        Scraper.MAX_RETRY_COUNT = 2
        Scraper.skipWords = ["nsfw","nsfl","reddit"]

        self.scrapeURL = url
        self.pattern = re.compile("([^\s]+(\.(?i)(jpg|png|gif|bmp))$)")

    def startScraping(self):
        count = 0
        links = deque()
        links.append(self.scrapeURL)
        retry = 0

        while(len(links) > 0 and count < Scraper.MAX_IMGS_TO_FETCH):
            link = links.pop()
            logging.debug("Requesting url: "+link+"...");
            response = urlfetch.Fetch(link).content
            (nextLinks, dlCount) = self.parse(response)
            count += dlCount
            if (not nextLinks or len(nextLinks) == 0) and retry < Scraper.MAX_RETRY_COUNT:
                links.append(link)
                retry = retry + 1
                time.sleep(1)
            else:
                retry = 0
                if nextLinks:
                    links.extend(nextLinks)

    def download(self, params):
        for k,v in params.iteritems():
            params[k] = self.truncateField(v)

        if self.pattern.search(params['url']):
            if self.isUnsavedURL(params['url']) and self.isValidTitle(params['title']):
                logging.debug("Queueing download of "+params['url']+"...")
                taskqueue.add(url='/worker', params=params)
            else:
                logging.debug("Skipping invalid link: "+params['url']);

    def truncateField(self, field):
        if len(field) > Scraper.MAX_FIELD_LENGTH:
            return field[:Scraper.MAX_FIELD_LENGTH-1]
        else:
            return field

    def filterTitle(self, title):
        filterWords = ["[pic]","(pic)","{pic}",]
        for word in filterWords:
            title = title.replace(word.lower(),"")
            title = title.replace(word.upper(),"")
        return title

    def isValidTitle(self, title):
        for word in Scraper.skipWords:
            if title.lower().find(word) != -1:
                logging.debug(">>Filtering out "+title+"<<<")
                return False
        return True

    def isUnsavedURL(self, url):
        return (len(cbmodel.Image.gql("WHERE url=:1",url).fetch(1)) == 0)

class RedditScraper(Scraper):
    def __init__(self, subreddit):
        RedditScraper.REDDIT_URL = "http://reddit.com"
        RedditScraper.SUBREDDIT_URL = RedditScraper.REDDIT_URL + "/r/"
        RedditScraper.REDDIT_JSON = "/.json?&after="

        self.subredditURL = subreddit+RedditScraper.REDDIT_JSON
        super(RedditScraper, self).__init__(self.subredditURL)

    def parse(self, response):
        try:
            responseDict = json.loads(response)
            nextLinks = []
            dlCount = 0
            for child in responseDict["data"]["children"]:
                params = {'url':child['data']['url'],
                'source':RedditScraper.SUBREDDIT_URL + child['data']['subreddit'],
                'title':self.filterTitle(child['data']['title']),
                'permalink':RedditScraper.REDDIT_URL + child['data']['permalink']}
                self.download(params)
                dlCount += 1
                time.sleep(0.2)
                nextLinks.append(self.subredditURL+child['data']['name'])
            return (nextLinks, dlCount)
        except ValueError, e:
            logging.error("Failed to decode JSON: " +response)
        except URLError, e:
            logging.error("Failed to reach a server.")
        except NameError, e:
            logging.error("Failed to request url: " +str(e))
        except Exception, e:
            logging.error("Failed to request url: "+str(type(e)))
    
class ScrapeWorker(webapp.RequestHandler):
    def __init__(self):
        ScrapeWorker.validContentTypes = ['image/jpeg',
                                          'image/jpg',
                                          'image/png',
                                          'image/gif']

    def post(self):
        def txn():
            try:
                url = self.request.get('url')
                response = urlfetch.Fetch(url)
                if ScrapeWorker.validContentTypes.count(response.headers['Content-Type']) > 0:
                    data = response.content
                    img = cbmodel.Image()
                    img.imageData = cbmodel.db.Blob(data)
                    img.url = url
                    img.title = self.request.get('title')
                    img.source = self.request.get('source')
                    img.permalink = self.request.get('permalink')
                    img.put()
                    logging.info("Successfully saved: "+url)
                else:
                    logging.debug("Skipping non-jpeg file: "+response.headers['Content-Type'])
            except urlfetch.Error, e:
                logging.error("Failed to request image url:"+str(type(e)))
            except db.Error, e:
                logging.error("Failed to put image url:"+str(type(e))) 
            except Exception, e:
                logging.error("Failed to put image url:"+str(type(e))) 
        cbmodel.db.run_in_transaction(txn)

class ScrapeService(webapp.RequestHandler):
    def post(self):
        logging.info("Starting scraper...")
        redditScraper = RedditScraper(self.request.get('scrapeURL'))
        redditScraper.startScraping()

    def get(self):
        # TODO change to use config file for scraping urls
        subReddits = ["pics","funny","wtf","adviceanimals"]
        count = 0
        for source in sources.all:
            taskqueue.add(url='/scrape',
            params={'scrapeURL':source},countdown=(count*30)+3)
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
