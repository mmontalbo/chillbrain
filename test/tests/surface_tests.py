from google.appengine.ext import webapp

import unittest
import logging
from webtest import TestApp
from config import appengine_config
from surface import *

class SurfaceSessionTests(unittest.TestCase):

    def setUp(self):
        logging.info('In setUp()')
        self.application = webapp.WSGIApplication([('/', MainPage)], debug=True)
        self.application = appengine_config.add_middleware(self.application)
        
    def tearDown(self):
        logging.info('In tearDown()')
        
    # Make sure the page compiles (sanity test)
    def test_page_compile(self):
        app = TestApp(self.application)
        response = app.get('/')
        self.assertTrue('200 OK', response.status)
        
    