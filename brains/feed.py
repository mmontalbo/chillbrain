from config.chill_constants import *
from model.image import *

import collections
import logging
import math

class ImageFeed():
    """
    Initializes the ImageFeed object with a desired feed size.
    Feed size indicates how many images should be returned when
    nextImages is called. Its value cannot be less than 1 or greater
    than 20.

    @param size desired feed size
    """
    def __init__(self, size):
        ImageFeed.MAX_FEED_SIZE = 20
        self.feedSources = []
        self.fetchSizes = []

        if size > 0 and size <= ImageFeed.MAX_FEED_SIZE:
            self.feedSize = size
        else:
            self.feedSize = 0
       
    """
    initial_images inizializes self.feedSouces with the given image source list.
    It then calls next_images, returning the resulting list of images. initial_images
    should be called once after ImageFeed is intialized and from then on, next_images
    should be called to return subsequent images from the given sources.

    @param sourcesList a list of image sources to draw from

    @return shuffled list of images from the given sources
    """
    def initial_images(self, sourcesList):
        self.feedSources = [(source, None) for source in sourcesList]
        return self.next_images() 
            
    """
    next_images returns a list of images, with length feedSize, drawn
    from each feedSource defined image source and interleaved.

    @return list of shuffled images with size feedSize
    """
    def next_images(self):
        images = []
        cursors = []

        if self.feedSize == 0 or len(self.feedSources) == 0:
            return images
        
        # If we haven't calculated fetchSizes yet, calculate them and store
        # the results.
        if len(self.fetchSizes) == 0:
            self.fetchSizes = self.calculate_fetch_sizes()

        # Fetch the fetchSizes[i] specified number of images from each source.
        for (i, feedSource) in enumerate(self.feedSources):
            (source,cursor) = feedSource

            query = self.image_query(source)
            if cursor is not None and cursor is not "":
                query.with_cursor(cursor)                
            numToFetch = self.fetchSizes[i]
            srcImgs = query.fetch(numToFetch)

            # If we got less than the number of images we asked for, try 
            # resetting the cursor and running the query again.
            if len(srcImgs) < numToFetch:
                logging.warn("Only "+str(len(srcImgs))+" images to return for "+str(source)+".");
                logging.warn("Resetting cursor.")
                query = self.image_query(source)
                srcImgs = query.fetch(numToFetch)                

            images.append(srcImgs)
            feedSource = (source, query.cursor()) # Update feedSource with new cursor

        shuffledImages = self.shuffle_images(images)

        return shuffledImages
    
    def set_feed_size(self, size):
        self.feedSize = size

    """
    image_query returns a GQL query for the Image with the given
    source.

    @return GQL query for Images with given source
    """
    def image_query(self, source):
        return CBImage.all().filter("source =", source)

    """
    shuffle_images interleaves the elements of each indiviual list
    it is given into a single list, which it subsequently returns.

    @param list containing lists of images
    @return list of shuffled images
    """
    def shuffle_images(self, images):
        shuffledImages = []

        for i in range(0, self.feedSize):
            index = i % len(images)
            if len(images[index]) == 0:
                return shuffledImages
            shuffledImages.append(images[i % len(images)].pop())
        return shuffledImages

    """
    Calculate the number of images to fetch from each source.
    If the number of images to fetch can't be distributed evenly
    among the sources, assign an extra image fetch starting from the
    beginning of the self.feedSources list until the remainder is exhausted.
    
    @return list of fetch sizes
    """
    def calculate_fetch_sizes(self):
        numFeedSources = len(self.feedSources)
        if numFeedSources > 0:
            fetchSizes = []
            baseQuerySize = self.feedSize/numFeedSources
            remainder = self.feedSize % numFeedSources
            for i in range(0, numFeedSources):
                fetchSizes.append(baseQuerySize)
                if i < remainder:
                    fetchSizes[i] += 1
        return fetchSizes
