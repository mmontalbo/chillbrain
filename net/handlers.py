from google.appengine.ext import webapp
from model.users import ChillUser, BaseUser
from facebook.facebook import *
from config import chill_config
from gaesessions import get_current_session

import logging
import os

if chill_config.isDebug():
    FACEBOOK_APP_ID = "688b1ffd024a472d1a14cc9fd5b3c1e0"
    FACEBOOK_APP_SECRET = "5d3c956fb414068031fb6a9209d5e4d5"
else:
    FACEBOOK_APP_ID = "6a87e922ddbb11627214a595cfa25d14"
    FACEBOOK_APP_SECRET = "a635afa552d5cdf29153664ef87ebc19"
    
SESS_KEY_VISIT = 'v'
SESS_KEY_USER = 'u'
SESS_TEMP_USER = 'tmp'

class ChillRequestHandler(webapp.RequestHandler):
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            current_session = self.current_session       
            cookie = get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = ChillUser.get_by_key_name(cookie["uid"])
                if not user:
                    graph = GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    album_id = str(graph.put_object("me", "albums", name="Chillbrain Photos")["id"])
                    user = ChillUser(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                access_token=cookie["access_token"],
                                album=album_id)
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
            # if there is no FB cookie then try to pull the temp user from the active session
            elif current_session.is_active():
                self._current_user = BaseUser.get(current_session[SESS_KEY_USER])
            # otherwise create a new temporary user
            else:
                self._current_user = BaseUser().create()
        return self._current_user
    
    @property
    def graph(self):
        if not hasattr(self, "_graph"):
            self._graph = None
            cookie = get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                self._graph = GraphAPI(cookie["access_token"])
        return self._graph
    
    @property
    def current_session(self):
        if not hasattr(self, "_current_session"):
            self._current_session = get_current_session()
        return self._current_session
    
    # This is a method to put a picture into a FB user's photo album in the chillbrain album created
    # when they became a user
    def album_share(self):
        user = self.current_user()
        if user:
            album = user.album
            if album:
                graph.put_object(album, "photos")
                
    # Override the initialize method of webapp.RequestHandler to setup the session and user data
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)   
        self.process_session()
        
    '''
        Setup the session for a BaseRequestHandler. 
        
        This will activate an unactive session and populate all of the required base 
        session data that will be used
    '''
    def process_session(self):
        session = self.current_session
        user = self.current_user
        
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
        self._current_session = session
        
    # Clear up the current session by flushing the session and clearing the current user
    def terminate_session(self):
        self._current_session.terminate()
        del self._current_session
        del self._current_user
        del self.request.cookies
                      
# Migrate a temporary user to ChillUser object 
# and migrate all temporary transactions.
# ** This is a utility method for handlers **
def migrate_session(user, session):    
    session.set_quick(SESS_TEMP_USER, False)
    temp = BaseUser.get(session[SESS_KEY_USER])
    user.migrate(temp)
    temp.delete()
    session[SESS_KEY_USER] = user.key()    
