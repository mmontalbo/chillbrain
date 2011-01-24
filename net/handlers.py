from google.appengine.ext import webapp
from model.users import ChillUser
from facebook.facebook import *
from config import appengine_config

import logging
import os

if appengine_config.isDebug():
    FACEBOOK_APP_ID = "688b1ffd024a472d1a14cc9fd5b3c1e0"
    FACEBOOK_APP_SECRET = "5d3c956fb414068031fb6a9209d5e4d5"
else:
    FACEBOOK_APP_ID = "6a87e922ddbb11627214a595cfa25d14"
    FACEBOOK_APP_SECRET = "a635afa552d5cdf29153664ef87ebc19"

class BaseRequest(webapp.RequestHandler):
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
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
        return self._current_user
    
    @property
    def graph(self):
        if not hasattr(self, "_graph"):
            self._graph = None
            cookie = get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                self._graph = GraphAPI(cookie["access_token"])
        return self._graph
    
    def album_share(self):
        user = self.current_user()
        if user:
            album = user.album
            if album:
                graph.put_object(album, "photos")