from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Transaction(polymodel.PolyModel):
    time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(required=True)

class Vote(Transaction):
    image = db.StringProperty(required=True)
    
class Skip(Transaction):
    image1 = db.StringProperty(required=True)
    image2 = db.StringProperty(required=True)
    
class Share(Transaction):
    image = db.StringProperty(required=True)
    generated_hits = db.IntegerProperty()
    
class AlbumShare(Transaction):
    image = db.StringProperty(required=True)
    
'''
    Temporary transaction tables for holding information
    related to temporary users to not cause lots of read/write
    operations to the actual transaction tables
'''
class TemporaryTransaction(polymodel.PolyModel):
    time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(required=True)

class TemporaryVote(TemporaryTransaction):
    image = db.StringProperty(required=True)
    
class TemporarySkip(TemporaryTransaction):
    image1 = db.StringProperty(required=True)
    image2 = db.StringProperty(required=True)