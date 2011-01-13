from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from google.appengine.api import memcache
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.api import images

import os
import logging
import efpmodel
import random
import sys

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
            imgA = efpmodel.Image.get(db.Key.from_path('Image',a))
        if(imgB is None):
            imgB = efpmodel.Image.get(db.Key.from_path('Image',b))

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
            
class ImageNext(webapp.RequestHandler):
    def get(self):
        MAX_HISTORY_SIZE = 100
        self.IMG_SELECT_KEY_QUERY = 'SELECT __key__ FROM Image ORDER BY date DESC, rating ASC'

        sid = self.request.get('s')
        num = self.validatePreloadNum(self.request.get('p'))
            
        session = self.getSession(sid)
        history = None
        cursor = None

        if(session):
            history = session.history
            cursor = session.cursor

        query = efpmodel.db.GqlQuery(self.IMG_SELECT_KEY_QUERY)
        if (cursor):
            query.with_cursor(cursor)
        images = query.fetch(num)               
        nextCursor = query.cursor()
        (images, nextCursor) = self.filterImagesInHistory(history, images, num, nextCursor)

        if(len(images) == 0):
            logging.error("Couldn't find any images to return! Trying to reset cursor.")
            query = efpmodel.db.GqlQuery(self.IMG_SELECT_KEY_QUERY)
            images = query.fetch(num)
            nextCursor = query.cursor()

        # Update session history to include next images
        if(session):
            while(len(session.history) > (MAX_HISTORY_SIZE - len(images))):
                session.history.pop(0)
            for img in images:
                session.history.append(str(img.name()))
            session.cursor = nextCursor
            session.put()
            memcache.delete('Session_'+str(session.key()))
            memcache.set('Session_'+str(session.key()),session)
            logging.debug("History end len: "+str(len(session.history)))
        else:
            logging.error("Couldn't find session "+sid)

        imageResponse = self.createJSONResponse(images)
        if(session):
            imageResponse['cb_sid'] = str(session.key())

        self.response.out.write(json.dumps(imageResponse))            
            

    def validatePreloadNum(self, p):
        num = 2
        try:
            if(p and int(p) > 0 and int(p) <= 16):
                num = int(p)
        except Exception, e:
            logging.error("Invalid value passed for preload num: "+str(p))
        finally:
            return num

    def getSession(self, sid):
        session = None
        try:
            logging.debug("Retrieving session with id: "+sid)
            session = memcache.get('Session_'+sid)
            if(session is None):
                session = efpmodel.Session.get(sid)
                memcache.set('Session_'+str(session.key()),session)
        except Exception, e:
            logging.info("Couldn't retrieve session id: "+sid)
        finally:
            if(session is None):
                logging.debug("Creating new session...")
                session = self.createSession()
            return session
                    
    def createSession(self):
        try:
            session = None
            session = efpmodel.Session();
            session.put()
            logging.info("Successfully created new session: "+str(session.key()))
            memcache.set('Session_'+str(session.key()),session)
        except Exception, e:
            logging.error("Couldn't create session: "+str(type(e)))
        finally:
            return session

    def filterImagesInHistory(self, history, images, num, nextCursor):
        if(history is None or images is None):
            return (images, nextCursor)

        try:
            filteredImages = [img for img in images if not history.count(str(img.name()))]
                        
            while(len(filteredImages) != num):
                query = efpmodel.db.GqlQuery(self.IMG_SELECT_KEY_QUERY).with_cursor(nextCursor)
                nimages = query.fetch(num-len(filteredImages))
                logging.debug("Fetching "+str(num-len(filteredImages))+" new images cursor("+nextCursor+".")
                newImages = [img for img in nimages if not history.count(str(img.name()))]
                logging.debug("Replaced "+str(len(newImages))+" old images.")
                filteredImages += newImages
                if(nextCursor == query.cursor()):
                    break
                else:
                    nextCursor = query.cursor()

            return (filteredImages, nextCursor)

        except Exception, e:
            logging.error("Couldn't filter next images based on history: "+str(type(e)))
        finally:
            return (images, nextCursor)

    def createJSONResponse(self, images):
        hashes = []
        titles = []
        elos = []            

        for imgKey in images:
            imgHash = str(imgKey.name())
            image = memcache.get(imgHash)
            if(image is None):
                image = efpmodel.Image.get(imgKey)
                memcache.set(imgHash,image)
            hashes.append(imgHash)
            titles.append(image.title)
            elos.append(image.rating)

        imageResponse = {"hashes" : hashes,
                         "titles" : titles,
                         "elos" : elos}

        return imageResponse


class ImageServe(webapp.RequestHandler):
    def get(self):
        try:
            imgHash = self.request.get('h')
            info = self.request.get('info')
            logging.info("info is:"+info)
            height = self.request.get('e')
            width = self.request.get('w') 

            img = self.getImg(imgHash)
            #img = self.resize(img,height,width)

            if (img and img.imageData):
                if(info is not ""):
                    imageResponse = {"title" : img.title,
                                     "rating" : img.rating,
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
            img = efpmodel.Image.get(efpmodel.db.Key.from_path('Image',imgHash))
            if(img):
                memcache.set('Image_'+imgHash,img)
        return img

class MainPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index2.html')
        self.response.out.write(template.render(path,None))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/',MainPage),
                                          ('/img',ImageServe),
                                          ('/next',ImageNext),
                                          ('/vote',ImageVote)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

