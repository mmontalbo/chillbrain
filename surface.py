from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from django.utils import simplejson as json

from model import users, transactions, image
from net.handlers import ChillRequestHandler, FACEBOOK_APP_ID
from brains import feed
from brains import reputation_manager
from config import chill_config
from config.error import *
from config.chill_constants import *
from net.response import *

import logging
import os

SESSION_IMAGE_FEED = 'feed'

# Request parameter constants
REQUEST_IMG_ID = 'img'
REQUEST_IMG_ID2 = 'img2'
REQUEST_NUM_IMAGES = 'n'
REQUEST_ACTION = 'action'
REQUEST_SHARE_ID = 'r'
REQUEST_FETCH = 'fetch'
REQUEST_DATA = 'data'

FEED_SIZE = 20
        
class MainPage(ChillRequestHandler):
    def get(self):
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["url"] = { "base" : BASE_URL, "share" : SHARE_URL, "img" : IMG_URL, "login" : LOGIN_REDIRECT_URL }
        
        user = self.current_user
        if user and not user.isTemporary():
            context["uid"] = user.id
        
        image_feed = feed.ImageFeed(FEED_SIZE)
        self.current_session.set_quick(SESSION_IMAGE_FEED, image_feed)

        initialImages  = image_feed.initial_images(sources_list)
        
        logging.debug("Path of URL: %s" % self.request.url)

        # make sure there are initial images to put into the request
        # TODO: Decide what error to throw if this is empty
        if initialImages:
            context["img1"] = initialImages[0]
            context["img2"] = initialImages[1]
        
        context["img"] = format_images_to_json(initialImages)
        
        path = os.path.join(os.path.dirname(__file__), 'template/index2.html')
        self.response.out.write(template.render(path, context))
        
class LoginScaffolding(ChillRequestHandler):
    def get(self):
        context = {}
        context["app_id"] = FACEBOOK_APP_ID
        context["url"] = { "base" : BASE_URL, "share" : SHARE_URL, "img" : IMG_URL }
        
        
        user = self.current_user
        
        if not user.isTemporary():
            context["uid"] = user.id
        
        image_feed = feed.ImageFeed(FEED_SIZE)
        self.current_session.set_quick(SESSION_IMAGE_FEED, image_feed)

        initialImages = image_feed.initial_images([REDDIT_FUNNY])
        
        context["img1"] = initialImages[0]
        context["img2"] = initialImages[1]
        context["img"] = format_images_to_json(initialImages)
        
        path = os.path.join(os.path.dirname(__file__), 'template/usertest.html')
        self.response.out.write(template.render(path, context))
        
class ImageServeScaffolding(webapp.RequestHandler):
    def get(self):
        image_feed = feed.ImageFeed(FEED_SIZE)

        initialImages = image_feed.initial_images([REDDIT_FUNNY])
        
        self.response.out.write([image.permalink for image in initialImages])
        
        initialImages = image_feed.next_images()
        self.response.out.write([image.permalink for image in initialImages])
  
#
# Base Image Request Handler
# 
# This class subclasses ChillRequestHandler and creates a prototype
# that retrieves the images from the post and delegates that to a 
# common method to handle them
#
class ImageRequestHandler(ChillRequestHandler):
    def __init__(self):
        self.repManager = reputation_manager.RepManager()
    def post(self):
        img = None
        img2 = None
        try:
            if self.request.get(REQUEST_IMG_ID):
                img = db.Key(self.request.get(REQUEST_IMG_ID))
            if self.request.get(REQUEST_IMG_ID2):
                img2 = db.Key(self.request.get(REQUEST_IMG_ID2))   
            self.handle_images(img, img2)
        except PermissionError:
            self.response.out.write(PermissionError.asJSON())
        
    def handle_images(self, img, img2):
        pass

# Vote on stuff      
class Vote(ImageRequestHandler):
    def handle_images(self, img, img2):
        vote_key = self.current_user.vote(img).key()
        self.response.out.write(ChillResponse(str(vote_key), str(img)).toJSON())
    
# Skip stuff
class Skip(ImageRequestHandler):
    def handle_images(self, img, img2):
        skip_key = self.current_user.skip(img,img2).key()
        self.response.out.write(ChillResponse(str(skip_key), str(img)).toJSON())
    
# Share with friends
class Share(ImageRequestHandler):
    def handle_images(self, img, img2):
        share = self.current_user.share(img)
        self.response.out.write(ShareResponse(str(share.key()), str(img)).toJSON())  

# Fetch more images
class Feed(ChillRequestHandler):
    def get(self):
        # If this invalid then just return nothing
        if not self.request.get(REQUEST_NUM_IMAGES):
            return
        feed = self.current_session.get(SESSION_IMAGE_FEED)
        feed.set_feed_size(int(self.request.get(REQUEST_NUM_IMAGES)))
        self.response.out.write(format_images_to_json(feed.next_images()))
  
def format_images_to_json(images):
    return json.dumps([{'id' : str(feedElement.key()), 'title' : feedElement.title, 'permalink': feedElement.permalink, 'src' : IMG_URL_TEMPLATE % str(feedElement.key()) } for feedElement in images]) 
        
class DataHandler(ChillRequestHandler):        
    def __init__(self):
        self.repManager = reputation_manager.RepManager()

    def get(self):         
        # Put the logic to return a JSON array of image metadata
        keys = self.request.get(REQUEST_DATA)
        
        if keys:
            key_array = json.loads(keys)
            logging.debug(key_array)
            images = []
            for key in key_array:
                images.append(image.CBImage.get(db.Key(key)))
            self.response.out.write(format_images_to_json(images))
        else:
            logging.debug("No keys...")
            # Put a 500 error here
            
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
     
