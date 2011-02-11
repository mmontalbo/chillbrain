'''
Created on Jan 13, 2011

@author: simonlevy
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import images
from model.image import *
from config.chill_constants import *

import logging

class ImageServe(webapp.RequestHandler):
    def get(self):
        try:
            imgHash = self.request.get('h')
            info = self.request.get('info')
            height = self.request.get('e')
            width = self.request.get('w') 

            img = self.getImg(imgHash)
            #img = self.resize(img,height,width)

            if (img and img.imageData):
                if(info is not ""):
                    imageResponse = {"title" : img.title,
                                     "source" : img.source}
                    self.response.out.write(json.dumps(imageResponse))
                else:
                    self.response.headers['Content-Type'] = 'image/jpeg'
                    self.response.out.write(img.imageData)

        except Exception, e:
            self.response.headers['Content-Type'] = 'image/jpeg'
            from google.appengine.api import urlfetch
            logging.error("Couldn't retrieve image: "+imgHash+". Error: "+str(type(e)))
            logging.error("Returning "+BASE_URL+"static/no_image.jpg")
            self.response.out.write(urlfetch.Fetch(BASE_URL + "static/no_image.jpg").content)

    def resizeImg(self,img,height,width):
        if(height is not "" and width is not ""):
            height = int(height)
            width = int(width)
            img.imageData = images.resize(image_data=img.imageData,width=width,height=height)
        elif(width is not ""):
            width = int(width)
            img.imageData = images.resize(image_data=img.imageData,width=width)
        elif(height is not ""):
            height = int(height)
            img.imageData = images.resize(image_data=img.imageData,height=height)
        return img

    def getImg(self,imgHash):
        img = CBImage.get(db.Key(imgHash))
        return img
