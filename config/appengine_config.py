'''
Created on Jan 13, 2011

@author: simonlevy
'''
from gaesessions import SessionMiddleware
import os

DEBUG = False

# If we are in a development setting (app engine dev server) then set debug to True
if os.environ['SERVER_SOFTWARE'].find('Development') > -1:
    DEBUG = True

def add_middleware(app):
    app = SessionMiddleware(app, cookie_key="R\xc6z\x87\xc2\xe5\r~\xc3\x95\xf9\x17Ip\xc0|\xfax\xf5?u\xfdJ\xdc\r\xb0Mc\x95\x8a\xf6\x1e\xc7\xda\x1bK\xf0\xcb\x81\x9d\xeb\xd7\xba\xb3\x14\xb1\xb85\x17\x1d\xc7\x96\xe5\x1e\x14\xc8\xa7K\xe8\xcdE#\xc0\xe2")
    return app

def isDebug():
    return DEBUG