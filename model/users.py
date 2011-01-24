from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from transactions import *

class BaseUser(polymodel.PolyModel):
    seen = db.ListProperty(str) # List of images User has seen
    votes = db.ListProperty(db.Key) # List of transaction IDs that have been votes on
    skips = db.ListProperty(db.Key) # List of transaction IDs that have been skipped
    
    def create(self):
        self.votes = []
        self.skips = []
        self.shares = []
        self.put()
    
    def show(self, img1, img2):
        self.seen.extend([img1, img2])
        self.put()
    
    def vote(self, image):        
        vote = TemporaryVote(user=self, img=image)
        vote.put()
        self.votes.append(vote.key())
        self.put()
        
    def skip(self, image1, image2):
        skip = TemporarySkip(user=self, img1=image1, img2=image2)
        skip.put()
        self.skips.append(skip.key())
        self.put()
        
    def isTemporary(self):
        return True
    
class ChillUser(BaseUser):
    id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    shares = db.ListProperty(db.Key) # List of transaction IDs that have been shared
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
    
    def vote(self, id):
        vote = Vote(user=self, img=id)
        vote.put()
        key = vote.key()
        self.votes.append(key)
        self.put()
        return key
    
    def skip(self, image1, image2):
        skip = Skip(user=self, img1=image1, img2=image2)
        skip.put()
        key = skip.key()
        self.skips.append(key)
        self.put()
        return key
        
    def share(self, image):
        share = Share(user=self, img=image)
        share.put()
        key = share.key()
        self.shares.append(key)
        self.put()
        return str(key)
        
    # Cycle through the stored transactions of the temp user and migrate them
    # over to the newly created actual user
    def migrate(self, baseUser):
        for vote in baseUser.votes:
            temporary_vote = TemporaryVote.get(vote)
            self.vote(temporary_vote.img)
            temporary_vote.delete()
        for skip in baseUser.skips:
            temporary_skip = TemporarySkip.get(skip)
            self.skip(temporary_skip.img1, temporary_skip.img2)
            temporary_skip.delete()
        self.put()
        
    def isTemporary(self):
        return False