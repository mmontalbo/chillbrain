from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson as json

from model.users import *
from model import transactions
from net.handlers import ChillRequestHandler, FACEBOOK_APP_ID
from brains.feed import *
from brains import reputation_manager
from config import appengine_config
from config.chill_constants import *

import logging
import os

# Request parameter constants
REQUEST_IMG_ID = 'img'
REQUEST_IMG_ID2 = 'img2'
REQUEST_ACTION = 'action'
REQUEST_SHARE_ID = 'r'

# URL configuration
if appengine_config.isDebug():
    BASE_URL = 'http://localhost:8080/'
else:
    BASE_URL = 'http://chillbrain.com/'

SHARE_URL = BASE_URL + "enter?"
IMG_URL = BASE_URL + "img?"
LOGIN_REDIRECT_URL = BASE_URL + "tests/login"

FEED_SIZE = 20
        
class MainPage(ChillRequestHandler):
    def get(self):
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["url"] = { "share" : SHARE_URL, "img" : IMG_URL, "login" : LOGIN_REDIRECT_URL }
        
        user = self.current_user
        if not user.isTemporary():
            context["uid"] = user.id
        
        feed = ImageFeed(FEED_SIZE)

        initialImages  = feed.initial_images([REDDIT_FUNNY])
        context["img1"] = initialImages.pop()
        context["img2"] = initialImages.pop()
        context["imgs"] = initialImages
        
        path = os.path.join(os.path.dirname(__file__), 'template/index2.html')
        self.response.out.write(template.render(path, context))
        
class LoginScaffolding(ChillRequestHandler):
    def get(self):
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["url"] = { "share" : SHARE_URL, "img" : IMG_URL }
        
        
        user = self.current_user
        
        if not user.isTemporary():
            context["uid"] = user.id
        
        feed = ImageFeed(FEED_SIZE)

        initialImages = feed.initial_images([REDDIT_FUNNY])
        context["img1"] = initialImages.pop()
        context["img2"] = initialImages.pop()     
        context["imgs"] = initialImages
        
        path = os.path.join(os.path.dirname(__file__), 'template/usertest.html')
        self.response.out.write(template.render(path, context))
        
class ImageServeScaffolding(webapp.RequestHandler):
    def get(self):
        feed = ImageFeed(FEED_SIZE)

        initialImages = feed.initial_images([REDDIT_FUNNY])
        
        self.response.out.write([image.permalink for image in initialImages])
        
        initialImages = feed.next_images()
        self.response.out.write([image.permalink for image in initialImages])
        
class DataHandler(ChillRequestHandler):        
    def __init__(self):
        self.repManager = reputation_manager.RepManager()

    def post(self):         
        img = None
        img2 = None
        if self.request.get(REQUEST_IMG_ID):
            img = db.Key(self.request.get(REQUEST_IMG_ID))
        if self.request.get(REQUEST_IMG_ID2):
            img2 = db.Key(self.request.get(REQUEST_IMG_ID2))        

        action = self.request.get(REQUEST_ACTION)
        user = self.current_user

        # process the data request and setup the response
        response_data = {}
        try: 
            if action == REQUEST_ACTION_VOTE:
                response_data['vote'] = str(user.vote(img))
            if action == REQUEST_ACTION_SKIP: 
                response_data['skip'] = str(user.skip(img, img2))
            if action == REQUEST_ACTION_SHARE:
                response_data['share'] = str(user.share(img))
        except Exception:
            response_data['error'] = "Problem processing data request"

        self.response.out.write(json.dumps(response_data))
   
'''
    Handle shared link redirects and tracking
'''   
class Entrance(ChillRequestHandler):
    def get(self):
         share_id = self.request.get(REQUEST_SHARE_ID) 
         
         # get the share transaction from the information and add a generated user (user clicks on their link)
         share_transaction = transactions.Share.get(db.Key(share_id))
         if share_transaction:
            share_transaction.add_generated_user(self.current_user)
         
         self.redirect(LOGIN_REDIRECT_URL)
        
'''
    Handle logging out by terminating the current session
'''
class Logout(ChillRequestHandler):
    def post(self):
        self.terminate_session()
     
