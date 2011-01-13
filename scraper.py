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

class ScrapeWorker(webapp.RequestHandler):
    def post(self):
        def txn():
            try:
                url = self.request.get('url')
                response = urlfetch.Fetch(url)
                if(response.headers['Content-Type'] == 'image/jpeg' or
                   response.headers['Content-Type'] == 'image/jpg'):
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
        self.fetchURLs(self.request.get('subreddit'))

    def get(self):
        subReddits = ["pics","funny","wtf","adviceanimals"]
        count = 0
        for subReddit in subReddits:
            taskqueue.add(url='/scrape',params={'subreddit':subReddit},countdown=(count*30)+3)
            count = count + 1
        self.response.out.write("<html><body>Started scraping...")
        self.response.out.write("</body></html>")

    def filterOut(self, title):
        filterWords = ["nsfw","reddit"]
        for word in filterWords:
            if(title.lower().find(word) != -1):
                logging.debug(">>Filtering out "+title+"<<<")
                return True
        return False

    def truncateField(self, field):
        if(len(field) > 500):
            return field[:499]
        else:
            return field

    def filterTitle(self, title):
        filterWords = ["[pic]","(pic)","{pic}"]
        for word in filterWords:
            title = title.replace(word.lower(),"")
            title = title.replace(word.upper(),"")
        return title

    def fetchURLs(self,subReddit):
        MAX_IMGS_TO_FETCH = 75
        MAX_LEN = 25
        count = 0
        redditURL = "http://www.reddit.com/r/"+subReddit+"/.json?&after="
        links = deque()
        links.append(redditURL)
        retry = 0

        while(len(links) > 0 and count < MAX_IMGS_TO_FETCH):
            try:
                link = links.pop()
                logging.info("Requesting url: "+link+"...");
                response = urlfetch.Fetch(link).content
                time.sleep(0.2)
                redditDict = json.loads(response)
                retry = 0

                for child in redditDict["data"]["children"]:
                    links.append(redditURL+child["data"]["name"])
                    if(len(links) > MAX_LEN):
                        links.popleft()
                    imgURL = self.truncateField(child["data"]["url"])
                    title = self.truncateField(self.filterTitle(child["data"]["title"]))
                    permaLink = self.truncateField("http://reddit.com" + child["data"]["permalink"])
                    m = re.search("(.*).jpg", imgURL)
                    if(m):
                        count = count + 1
                        ti = m.group(0).rsplit("/")
                        img = ti[len(ti)-1]
                        result = efpmodel.db.GqlQuery("SELECT * FROM Image WHERE url = :1 LIMIT 1",imgURL).fetch(1)
                        if (len(result) == 0 and not(self.filterOut(title))):
                            logging.debug("Queueing download of "+imgURL+"...")
                            taskqueue.add(url='/worker', params={'url': imgURL,'source': permaLink,'title': title})
                        else:
                            logging.debug("Skipping redundant link: "+imgURL);

            except ValueError, e:
                logging.error('Failed to decode JSON: '+response)
                if(len(links) == 0 and retry < 5):
                    links.append(link)
                    retry = retry + 1
                    logging.debug("Retrying "+str(retry)+"...")
                    time.sleep(1)
            except URLError, e:
                logging.error("Failed to reach a server.")
            except Exception, e:
                logging.error("Failed to request url: "+str(type(e)))

        logging.debug("Downloading "+str(count)+" images.")
                
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/scrape',ScrapeService),
                                          ('/worker',ScrapeWorker)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
