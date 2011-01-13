from google.appengine.ext import db
from google.appengine.ext import blobstore

class Image(db.Model):
    imageData = db.BlobProperty(default=None)
    source = db.StringProperty(multiline=False)
    url = db.StringProperty(multiline=False)
    title = db.StringProperty(multiline =True)
    date = db.DateTimeProperty(auto_now_add=True)
    rating = db.FloatProperty(default=1500.0)
    
class Session(db.Model):
    history = db.StringListProperty()
    cursor = db.StringProperty(multiline=True)
