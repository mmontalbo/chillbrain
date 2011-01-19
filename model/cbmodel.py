from google.appengine.ext import db
from google.appengine.ext import blobstore

class Image(db.Model):
    imageData = db.BlobProperty(default=None)
    source = db.StringProperty(multiline=False)
    permalink = db.LinkProperty()
    url = db.LinkProperty()
    title = db.StringProperty(multiline =True)
    date = db.DateTimeProperty(auto_now_add=True)
    skips = db.IntegerProperty(default=0)
    votes = db.IntegerProperty(default=0)