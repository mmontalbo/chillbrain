from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson as json

from gaesessions import *
from model.users import *
from model import transactions
from net.handlers import *
from brains.feed import *
from config import sources, appengine_config
import logging
import os


SESS_KEY_VISIT = 'v'
SESS_KEY_USER = 'u'
SESS_TEMP_USER = 'tmp'

# Request parameter constants
REQUEST_IMG_ID = 'img'
REQUEST_IMG_ID2 = 'img2'
REQUEST_ACTION = 'action'
REQUEST_SHARE_ID = 'r'

# Request action constants
REQUEST_ACTION_VOTE = 'vote'
REQUEST_ACTION_SKIP = 'skip'
REQUEST_ACTION_SHARE = 'share'
REQUEST_ACTION_REPORT = 'report'
REQUEST_ACTION_UPLOAD = 'upload'
# ... More achievments to come (history, image stats)

# URL configuration
if appengine_config.isDebug():
    BASE_URL = 'http://localhost:8080/'
else:
    BASE_URL = 'http://chillbrain.com/'

SHARE_URL = BASE_URL + "enter?"
IMG_URL = BASE_URL + "img?"
LOGIN_REDIRECT_URL = BASE_URL + "tests/login"

FEED_SIZE = 20

class RepManager():
    def __init__(self):
        RepManager.REP_REQ = { REQUEST_ACTION_SKIP: 0.0,
                               REQUEST_ACTION_VOTE:0.0,
                               REQUEST_ACTION_SHARE : 20.0,
                               REQUEST_ACTION_REPORT: 100.0,
                               REQUEST_ACTION_UPLOAD: 500.0}
        
        RepManager.ACHIEVMENT_MSGS = { REQUEST_ACTION_SHARE : "Sharing is now enabled.",
                                       REQUEST_ACTION_REPORT: "Reporting images is now enabled.",
                                       REQUEST_ACTION_UPLOAD: "Uploading images is now enabled."}
        
        RepManager.LINKBACK_FACTOR = 0.25

    def update_rep(self, action, reputation, linkbacks = 0):
        # get rep increase for linkbacks
        inc_rep = RepManager.LINKBACK_FACTOR * linkbacks
        
        # update reputation if voting
        if action == REQUEST_ACTION_VOTE:
            inc_rep += 1.0
            
        # message if new achievment is unlocked
        msg = self.get_achievment_msg(reputation, inc_rep)
        reputation += inc_rep
        return (reputation, msg)

    # Check if the given action can be performed based on the given reputation
    def check_permission(self, action, reputation):
        if action in RepManager.REP_REQ:
            hasPermission = reputation >= RepManager.REP_REQ[action]
            if not hasPermission:
                return (hasPermission,self.get_permission_denied_msg(action))
            else:
                return(hasPermission,None)
        else:
            logging.error("No reputation requirement defined for: "+action)
            return (False,None)

    # Get any new achievment messages
    def get_achievment_msg(self,reputation,inc_rep):
        msg = None
        for action,req in RepManager.REP_REQ.iteritems():
            if reputation < req and (reputation + inc_rep) >= req:
                return RepManager.ACHIEVMENT_MSGS[action]
        return msg

    # Construct an appropriate permission denied error message
    def get_permission_denied_msg(self, action):
        return "Need "+str(RepManager.REP_REQ[action])+" rep to "+action+"."
        
class MainPage(BaseRequest):
    def get(self):
        session = get_current_session()
        user = get_user(self.current_user, session)
        
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["permissions"] = get_permissions(user)
        context["url"] = { "share" : SHARE_URL, "img" : IMG_URL, "login" : LOGIN_REDIRECT_URL }
        
        if not user.isTemporary():
            context["uid"] = user.id
        
        feed = ImageFeed(FEED_SIZE)

        initialImages, feedSources = feed.initialImages([sources.all[0]])
        context["img1"] = initialImages.pop()
        context["img2"] = initialImages.pop()
        context["imgs"] = initialImages
        
        path = os.path.join(os.path.dirname(__file__), 'template/index2.html')
        self.response.out.write(template.render(path, context))
        
class LoginScaffolding(BaseRequest):
    def get(self):
        session = get_current_session()
        user = get_user(self.current_user, session)
        
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["permissions"] = get_permissions(user)
        context["url"] = { "share" : SHARE_URL, "img" : IMG_URL }
        
        if not user.isTemporary():
            context["uid"] = user.id
        
        feed = ImageFeed(FEED_SIZE)

        initialImages, feedSources = feed.initialImages([sources.all[0]])
        context["img1"] = initialImages[0]
        context["img2"] = initialImages[1]        
        
        path = os.path.join(os.path.dirname(__file__), 'template/usertest.html')
        self.response.out.write(template.render(path, context))
        
class ImageServeScaffolding(BaseRequest):
    def get(self):
        outie = None
        feed = ImageFeed(FEED_SIZE)

        initialImages, feedSources = feed.initialImages([sources.all[0]])
        
        self.response.out.write([image.permalink for image in initialImages])
        
        initialImages, feedSources = feed.nextImages(feedSources)
        self.response.out.write([image.permalink for image in initialImages])
        
class DataHandler(BaseRequest):        
    def __init__(self):
        self.repManager = RepManager()

    def post(self):
        session = get_current_session()
        user = get_user(self.current_user, session)
        
        # New Session: Initialize visit counter and temp user id
        if not session.is_active():                    
            session[SESS_KEY_VISIT] = 1
            session[SESS_KEY_USER] = user.key()
            session.set_quick(SESS_TEMP_USER, user.isTemporary())
        # Existing Session: Increment Visit Counter
        else:
            session[SESS_KEY_VISIT] = session[SESS_KEY_VISIT] + 1
            # if this is a temporary user that has logged in migrate their cache over
            if session.get(SESS_TEMP_USER) and not user.isTemporary():
                migrate_session(user, session)
                
        img = None
        img2 = None
        if self.request.get(REQUEST_IMG_ID):
            img = db.Key(self.request.get(REQUEST_IMG_ID))
        if self.request.get(REQUEST_IMG_ID2):
            img2 = db.Key(self.request.get(REQUEST_IMG_ID2))        

        response = process_request(self.request.get(REQUEST_ACTION), user, img, img2)
        self.response.out.write(json.dumps(response))
   
'''
    Handle shared link redirects and tracking
'''   
class Entrance(BaseRequest):
    def get(self):
         share_id = self.request.get(REQUEST_SHARE_ID)
         
         session = get_current_session()
         user = get_user(self.current_user, session)
         
         # get the share transaction from the information and add a generated user (user clicks on their link)
         share_transaction = transactions.Share.get(db.Key(share_id))
         share_transaction.add_generated_user(user)
         
         self.redirect('/usr/')
        
'''
    Handle logging out by terminating the current session
'''
class Logout(webapp.RequestHandler):
    def post(self):
        session = get_current_session()
        session.terminate()
     
'''
    Utility methods for user management
'''            
# Get a User object from the current user retrieved from the BaseRequest and session  
def get_user(user, session):
    if user:
        return user
    elif session.is_active():
        return BaseUser.get(session[SESS_KEY_USER])
    else:
        user = BaseUser()
        user.create()
        return user
    
# Get permissions for this specific user. These are to be placed into the context
def get_permissions(user):
    permissions = {}
    permissions["share"] = user.isTemporary() == False
    return permissions
    
# Process a data request
def process_request(action, user, img, img2):
    response_data = {}
    if action == REQUEST_ACTION_VOTE:
        response_data['vote'] = user.vote(img)
    if action == REQUEST_ACTION_SKIP: 
        response_data['skip'] = user.skip(img, img2)
    if action == REQUEST_ACTION_SHARE:
        response_data['share'] = user.share(img)
    return response_data

# Migrate a temporary user to ChillUser object 
# and migrate all temporary transactions
def migrate_session(user, session):
    session.set_quick(SESS_TEMP_USER, False)
    temp = BaseUser.get(session[SESS_KEY_USER])
    user.migrate(temp)
    temp.delete()
    session[SESS_KEY_USER] = user.key()    
