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
        vote = TemporaryVote(user=self, image=image)
        vote.put()
        self.votes.append(vote.key())
        self.put()
        
    def skip(self, image1, image2):
        skip = TemporarySkip(user=self, image1=image1, image2=image2)
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
    
    def vote(self, id):
        vote = Vote(user=self, image=id)
        vote.put()
        self.votes.append(vote.key())
        self.put()
    
    def skip(self, image1, image2):
        skip = Skip(user=self, image1=image1, image2=image2)
        skip.put()
        self.skips.append(skip.key())
        self.put()
        
    def share(self, image):
        share = Share(user=self, image=image)
        share.put()
        self.shares.append(share.key())
        self.put()
        
    # Cycle through the stored transactions of the temp user and migrate them
    # over to the newly created actual user
    def migrate(self, baseUser):
        for vote in baseUser.votes:
            temporary_vote = TemporaryVote.get(vote)
            self.vote(temporary_vote.image)
            temporary_vote.delete()
        for skip in baseUser.skips:
            temporary_skip = TemporarySkip.get(skip)
            self.skip(temporary_skip.image1, temporary_skip.image2)
            temporary_skip.delete()
        self.put()
        
    def isTemporary(self):
        return False