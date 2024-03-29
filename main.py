from config import chill_config
from brains.imgserve import *
from surface import *
#from util import datastore_cache

#datastore_cache.DatastoreCachingShim.Install()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db

# import custom template tags
webapp.template.register_template_library('config.taglib')

import os

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    publish_urls = [('/', MainPage),
                       ('/img', ImageServe),
                       ('/vote', Vote),
                       ('/skip', Skip),
                       ('/share', Share),
                       ('/feed', Feed),
                       ('/enter', Entrance),
                       ('/data', DataHandler),
                       ('/logout', Logout)]
    
    # in pre-production extend the publish list with the test URLs
    if chill_config.isDebug():
        publish_urls.extend([('/tests/login', LoginScaffolding),
                             ('/tests/image', ImageServeScaffolding)])
    
    application = webapp.WSGIApplication(publish_urls, chill_config.isDebug())
    application = chill_config.add_middleware(application)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

