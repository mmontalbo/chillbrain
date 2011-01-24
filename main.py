from config.appengine_config import add_middleware
from brains.imgserve import *
from surface import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db

import os

DEBUG = True

import os

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/',MainPage),
                                          ('/img',ImageServe),
                                          ('/vote',ImageVote),
                                          ('/test',ImageServeScaffolding),
                                          ('/enter', Entrance),
                                          ('/data',DataHandler),
                                          ('/logout', Logout)],
                                         DEBUG)
    application = add_middleware(application)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

