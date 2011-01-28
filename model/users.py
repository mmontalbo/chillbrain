from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from transactions import *

import logging
import hashlib

class BaseUser(polymodel.PolyModel):
    seen = db.ListProperty(str) # List of images User has seen
    votes = db.ListProperty(db.Key) # List of transaction IDs that have been votes on
    skips = db.ListProperty(db.Key) # List of transaction IDs that have been skipped
    shares = db.ListProperty(db.Key) # List of transaction IDs that have been shared (this is just reference links in the case of a BaseUser)
    reputation = db.FloatProperty(default=0.0) # Tracks this users reputation
    
    def create(self):
        self.votes = []
        self.skips = []
        self.shares = []
        self.put()
        return self
    
    def show(self, img1, img2):
        self.seen.extend([img1, img2])
        self.put()
    
    def vote(self, image):        
        vote = TemporaryVote(user=self, img=image)
        vote.put()
        self.votes.append(vote.key())
        self.put()
        return vote
        
    def skip(self, image1, image2):
        skip = TemporarySkip(user=self, img1=image1, img2=image2)
        skip.put()
        self.skips.append(skip.key())
        self.put()
        return skip
        
    # add a temporary share to a BaseUser (they can't be counted until migration to logged in state)    
    def add_temporary_clickback(self, share_ref):
        self.shares.append(share_ref.key())
        self.put()
        
    def isTemporary(self):
        return True
    
class ChillUser(BaseUser):
    id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    album = db.StringProperty() # FB ID for this users Chillbrain album
    linkbacks = db.IntegerProperty(default=0) # Tracks number of linkbacks for this user
    
    def get_linkbacks(self):
        linkbacks = self.linkbacks
        self.linkbacks = 0
        self.put()
        return linkbacks
    
    def increment_linkback(self):
        self.linkbacks += 1
        self.put()
    
    # vote with a hash of the image key and user key to prevent double voting
    # TODO: Add custom exception around this so we can message double votes
    def vote(self, id):
        # must use hexdigest to prevent unicode exceptions coming from the datastore
        hash = hashlib.sha1(str(self.key()) + str(id)).hexdigest() 
        vote = Vote(user=self, img=id, validator=hash, key_name=hash)
        vote.put()
        self.votes.append(vote.key())
        self.put()
        return vote
    
    def skip(self, image1, image2):
        skip = Skip(user=self, img1=image1, img2=image2)
        skip.put()
        self.skips.append(skip.key())
        self.put()
        return skip
        
    def share(self, image):
        share = Share(user=self, img=image)
        share.put()
        self.shares.append(share.key())
        self.put()
        return share
        
    # Cycle through the stored transactions of the temp user and migrate them
    # over to the newly created actual user
    def migrate(self, baseUser):
        for vote in baseUser.votes:
            temporary_vote = TemporaryVote.get(vote)
            self.vote(temporary_vote.img.key())
            temporary_vote.delete()
        for skip in baseUser.skips:
            temporary_skip = TemporarySkip.get(skip)
            self.skip(temporary_skip.img1.key(), temporary_skip.img2.key())
            temporary_skip.delete()
        for clickback in baseUser.shares:
            share_transaction = Share.get(clickback)
            share_transaction.add_generated_user(self)
        self.put()
        
    def isTemporary(self):
        return False