from google.appengine.ext import webapp
from google.appengine.api.labs import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app

from model.image import *

import logging
import re

WORKER_URL='/migrateImages'
ITEMS_TO_FETCH=30

class MigrationWorker(webapp.RequestHandler):
    def get(self):
        taskqueue.add(url=WORKER_URL)

    def post(self):
        if self.request.get('start'):
            self.startKey = self.request.get('start')
        else:
            self.startKey = None
        self.work()

    def work(self):
        query = self.kind.all()
        if self.startKey:
          query.filter('__key__ >', db.Key(self.startKey))
        items = query.fetch(ITEMS_TO_FETCH)
        if not items:
          logging.info('Finished migrating %s' % self.kindName)
          return
        
        last_key = items[-1].key()
        modified = [self.migrateItem(x) for x in items]
        db.put(modified)

        taskqueue.add(
            url=WORKER_URL, params=dict(start=last_key))
        logging.info('Added another task to queue for %s starting at %s' % (self.kindName, last_key))
    
    """Override this method to do some work for each item
    """
    def migrateItem(self, item):
        logging.info("processing %s %s" % (self.kindName, item.key()))
        return item

class ImageWorker(MigrationWorker):
    kind=Image
    kindName="Image"
    def migrateItem(self, item):
        logging.info("processing %s %s" % (self.kindName, item.key()))
        pattern = re.compile("(http://reddit.com/r/[a-zA-Z0-9]+)/.*")
	cbImage = CBImage()
        cbImage.imageData = item.imageData
        cbImage.title = item.title
        cbImage.source = pattern.search(item.source).group(1)
        cbImage.permalink = item.source
        cbImage.url = item.url
        cbImage.date = item.date
        cbImage.rating = 0.0
        return cbImage

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/migrateImages',ImageWorker)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
