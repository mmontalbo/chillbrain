import math
#import cbmodel

class ImageFeed():
    """
    Initializes the ImageFeed object with a desired feed size.
    Feed size indicates how many images should be returned when
    nextImages is called. Its value cannot be less than 1 or greater
    than 20.

    @param size desired feed size
    """
    def __init__(self, size):
        if size > 0 and size <= 20:
            self.feedSize = size
        else:
            self.feedSize = 0
    """
    nextImages returns a list of images, with length feedSize, drawn
    from each available image source and interleaved evenly. Note that
    it is possible to leave the cursor blank for each source, in which case
    a fresh query will be run for the source and a new cursor will be
    returned.

    @param sourceCursors array of (source, cursor) pairs
    @return list of new cursors and images with length feedSize
    """
    def nextImages(self, sourceCursors):
        images = []
        cursors = []
        if self.feedSize == 0 or len(sourceCursors) == 0:
            return images

        numToFetch = math.ceil(self.feedSize / len(sourceCursors))

        for sourceCursor in sourceCursors:            
            (source, cursor) = sourceCursor
            query = self.imageQuery(source)
            if cursor is not None and cursor is not "":
                query.with_cursor(cursor)
            srcImgs = query.fetch(numToFetch)

            if len(srcImgs) < numToFetch:
                logging.info("Only ("+len(srcImgs)+") images to return for ("+cursor+","+source+").");
                logging.info("Resetting cursor.")
                query = self.imageQuery(source)
                srcImgs = query.fetch(numToFetch)

            cusors.append(query.cursor())
            images.append(srcImgs)

        shuffledImages = self.shuffleImages(images)
        while(len(shuffledImages > self.feedSize)):
            shuffledImages.pop()

        return (shuffledImages,cursors)

    """
    imageQuery returns a GQL query for the Image with the given
    source.

    @return GQL query for Images with given source
    """
    def imageQuery(self, source):
        return Image.gql("WHERE source=:1", source)

    """
    shuffleImages interleaves the elements of each indiviual list
    it is given into a single list, which it subsequently returns.

    @param list containing lists of images
    @return list of shuffled images
    """
    def shuffleImages(self, images):
        shuffledImages = []

        for i in range(0,len(images[0])):
            for row in images:
                shuffledImages.append(row[i])
        
        return shuffledImages
