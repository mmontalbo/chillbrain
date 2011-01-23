import math
from config.sources import *
from model import cbmodel
import logging

class FeedSource():
    def __init__(self, source, cursor):
        self.source = source
        self.cursor = cursor

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

        if size > 0 and size <= ImageFeed.MAX_FEED_SIZE:
            self.feedSize = size
        else:
            self.feedSize = 0
            
    def initialImages(self, sourcesList):
        return self.nextImages([FeedSource(source, None) for source in sourcesList]) 
            
    """
    nextImages returns a list of images, with length feedSize, drawn
    from each available image source and interleaved evenly. Note that
    it is possible to leave the cursor blank for each source, in which case
    a fresh query will be run for the source and a new cursor will be
    returned.

    @param feedSources list of FeedSource objects that contain a feed source
    cursor

    @return list of shuffled images with size feedSize and a new list of FeedSources
    with updated cursors
    """
    def nextImages(self, feedSources):
        images = []
        cursors = []
        numCursors = len(feedSources)
        if self.feedSize == 0 or numCursors == 0:
            return images

        fetchSize = []
        baseQuerySize = self.feedSize/numCursors
        remainder = self.feedSize % numCursors
        for i in range(0, numCursors):
            fetchSize.append(baseQuerySize)
            if i < remainder:
                fetchSize[i] += 1

        position = 0
        for feedSource in feedSources:
            source = feedSource.source
            cursor = feedSource.cursor
            query = self.imageQuery(source)
            if cursor is not None and cursor is not "":
                query.with_cursor(cursor)
                
            numToFetch = fetchSize[position]
            srcImgs = query.fetch(numToFetch)

            if len(srcImgs) < numToFetch:
                logging.info("Only ("+str(len(srcImgs))+") images to return for ("+str(cursor)+","+str(source)+").");
                logging.info("Resetting cursor.")
                query = self.imageQuery(source)
                srcImgs = query.fetch(numToFetch)
                
            feedSource.cursor = query.cursor()
            images.append(srcImgs)
            position += 1

        logging.info(str(images))
        shuffledImages = self.shuffleImages(images)

        return (shuffledImages,feedSources)

    """
    imageQuery returns a GQL query for the Image with the given
    source.

    @return GQL query for Images with given source
    """
    def imageQuery(self, source):
        return cbmodel.Image.all().filter("source =", source)

    """
    shuffleImages interleaves the elements of each indiviual list
    it is given into a single list, which it subsequently returns.

    @param list containing lists of images
    @return list of shuffled images
    """
    def shuffleImages(self, images):
        shuffledImages = []

        for i in range(0, self.feedSize):
            index = i % len(images)
            if len(images[index]) == 0:
                return shuffledImages
            shuffledImages.append(images[i % len(images)].pop())
        return shuffledImages
