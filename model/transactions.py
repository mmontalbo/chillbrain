from google.appengine.ext import db
from google.appengine.ext.db import polymodel

import logging

class Transaction(polymodel.PolyModel):
    time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(required=True)

class Vote(Transaction):
    img = db.ReferenceProperty(required=True, collection_name="vote_img")
    
class Skip(Transaction):
    img1 = db.ReferenceProperty(required=True, collection_name="skip_img1")
    img2 = db.ReferenceProperty(required=True, collection_name="skip_img2")
    
class Share(Transaction):
    img = db.ReferenceProperty(required=True, collection_name="share_img")
    generated_users = db.ListProperty(db.Key)
    generated_hits = db.IntegerProperty(default=0)
    
    def add_generated_user(self, user):
        # If this is a temporary user then add it as a temporary clickback and return
        if user.isTemporary():
            user.add_temporary_clickback(self)
            return
        # Reject motherfuckers trying to get reputation by their own clickbacks... those bastards
        elif user.key() == self.user.key():
            return
        
        # otherwise generate a hit for this clickback and increment the linkback counter
        self.generated_hits += 1
        self.generated_users.append(user.key())
        self.user.increment_linkback()
        self.put()
    
class AlbumShare(Transaction):
    img = db.ReferenceProperty(required=True, collection_name="album_img")
    
'''
    Temporary transaction tables for holding information
    related to temporary users to not cause lots of read/write
    operations to the actual transaction tables
'''
class TemporaryTransaction(polymodel.PolyModel):
    time = db.DateTimeProperty(auto_now_add=True)
    user = db.ReferenceProperty(required=True)

class TemporaryVote(TemporaryTransaction):
    img = db.ReferenceProperty(required=True, collection_name="tmp_vote_img")
    
class TemporarySkip(TemporaryTransaction):
    img1 = db.ReferenceProperty(required=True, collection_name="tmp_skip_img1")
    img2 = db.ReferenceProperty(required=True, collection_name="tmp_skip_img2")
    
# Storage for a temporary click back that holds onto the share reference
class TemporaryClickback(TemporaryTransaction):
    share_reference = db.ReferenceProperty(required=True, collection_name="tmp_share")
    