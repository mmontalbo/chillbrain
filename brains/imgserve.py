'''
Created on Jan 13, 2011

@author: simonlevy
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from google.appengine.api import memcache
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import images
from model.cbmodel import *

import logging

class ImageVote(webapp.RequestHandler):
    def post(self):
        try:
            winner = self.request.get('winner')
            loser = self.request.get('loser')
            draw = self.request.get_all('draw[]')
            
            if(draw and len(draw) == 2):
                self.calcElo(0,draw[0],draw[1])
            elif(winner is not "" and loser is not ""):
                self.calcElo(1,winner,loser);

        except ValueError, e:
            logging.error("Failed to decode vote JSON: "+str(type(e)))
        except db.Error, e:
            logging.error("Failed to put vote:"+str(type(e)))
        except Exception, e:
            logging.error("Failed to process vote"+str(type(e)))
            if hasattr(e, 'reason'):
                logging.error('Reason: '+ e.reason)

    def calcElo(self,status,a,b):
        imgA = memcache.get('Image_'+a)
        imgB = memcache.get('Image_'+b)

        if(imgA is None):
            imgA = cbmodel.Image.get(db.Key.from_path('Image',a))
        if(imgB is None):
            imgB = cbmodel.Image.get(db.Key.from_path('Image',b))

        qa = pow(10.0,(imgA.rating/400.0))
        qb = pow(10.0,(imgB.rating/400.0))
        ea = qa / (qa+qb)
        eb = qb / (qa+qb)
        
        sa = 0.5
        sb = 0.5
        if(status == 1):
            sa = 1.0
            sb = 0.0

        k = 32.0
        imgA.rating = imgA.rating + (k * (sa-ea))
        imgB.rating = imgB.rating + (k * (sb-eb))

        if(sa == 1.0):
            logging.debug("Winner rating: "+str(imgA.rating))
            logging.debug("Loser rating: "+str(imgB.rating))
        else:
            logging.debug("Draw rating: "+str(imgA.rating))
            logging.debug("Draw rating: "+str(imgB.rating))        
        imgA.put()
        imgB.put()
        memcache.delete('Image'+a)
        memcache.delete('Image_'+b)
        memcache.set('Image_'+a,imgA)
        memcache.set('Image_'+b,imgB)


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
            self.response.out.write(urlfetch.Fetch("http://efpscrape.appspot.com/static/no_image.jpg").content)

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
        img = memcache.get('Image_'+imgHash)
        if(img is None):
            img = Image.get(db.Key(imgHash))
            if(img):
                memcache.set('Image_'+imgHash,img)
        return img