from django.http import HttpResponse

from google.appengine.api.labs import taskqueue

from models.image import *
import logging

WORKER_URL='/worker/migrate1To2/%s'
ITEMS_TO_FETCH=30
#General Migration 
def migrateModel(request, model_name):
    #create the worker class and tell it to work
    workerName = '%sWorker' % model_name
    if not workerName in globals():
        logging.info("no worker for %s" % model_name)
        return HttpResponse("no worker for %s" % model_name)
    Worker =  globals()[workerName]
    if "start" in request.REQUEST:
        Worker(request.REQUEST['start']).work()
    else:
        Worker().work()
    return HttpResponse("ok")

class MigrationWorker(object):
    def __init__(self, startKey=None):
        self.startKey=startKey
    
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
            url=WORKER_URL % self.kindName, params=dict(start=last_key))
        logging.info('Added another task to queue for %s starting at %s' % (self.kindName, last_key))
    
    """Override this method to do some work for each item
    """
    def migrateItem(self, item):
        logging.info("processing %s %s" % (self.kindName, item.key()))
        return item


"""migrate from version 1 to version 2"""
def migrate1To2(request):
    modelsToMigrate = ['Image']
    [taskqueue.add(url=WORKER_URL % i) for i in modelsToMigrate]
    return HttpResponse("created all tasks for processing")

class ImageWorker(MigrationWorker):
    kind=Image
    kindName="Image"
    def migrateItem(self, item):
        logging.info("processing %s %s" % (self.kindName, item.key()))
	cbImage = CBImage()
        cbImage.imageData = item.imageData
        cbImage.title = item.title
        cbImage.source = item.source
        cbImage.permalink = item.source
        cbImage.url = item.url
        cbImage.date = item.date
        cbImage.rating = 0.0
        return cbImage
