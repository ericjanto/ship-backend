from PositionalInvertedIndex import PositionalInvertedIndex
from TagPositionalInvertedIndex import TagPositionalInvertedIndex

# TODO: Refactor, possibly split into abstract and subclasses

class IndexDecompressor():

    def __init__(self, vBytes):
        """
        vBytes should be a bytearray object
        """
        self.vBytes = vBytes

        self.vBytesLength = len(self.vBytes)

        self.pos = 0

        self.index = None


    def toIndex(self):
        self.index = PositionalInvertedIndex()

        numTerms = self.readNextIntFromByteStream()

        for _ in range(numTerms):
            termLength = self.readNextIntFromByteStream()

            term = self.readTermFromByteStream(termLength)

            docCount = self.readNextIntFromByteStream()

            for _ in range(docCount):
                docID = self.readNextIntFromByteStream()

                numberOfOccurences = self.readNextIntFromByteStream()

                lastPosition = 0

                positions = [0] * numberOfOccurences

                for i in range(numberOfOccurences):
                    delta = self.readNextIntFromByteStream()

                    position = delta + lastPosition

                    positions[i] = position

                    #self.index.insertTermInstance(term, docID, position)

                    lastPosition = position

                self.index.insertPostingList(term, docID, positions)

        return self.index


    def toTagIndex(self):
        self.index = TagPositionalInvertedIndex()

        numTags = self.readNextIntFromByteStream()

        for _ in range(numTags):
            tagLength = self.readNextIntFromByteStream()

            tag = self.readTermFromByteStream(tagLength)

            storyIDCount = self.readNextIntFromByteStream()

            lastStoryID = 0

            for _ in range(storyIDCount):
                delta = self.readNextIntFromByteStream()

                storyID = delta + lastStoryID

                self.index.insertTagInstance(tag, storyID)

                lastStoryID = storyID

        return self.index


    def readNextIntFromByteStream(self):
        val = 0

        while self.pos < self.vBytesLength:

            byteVal = self.vBytes[self.pos]

            if byteVal >= 128:
                val += byteVal - 128
            else:
                val += byteVal

            self.pos += 1

            if byteVal < 128:
                val = val * 128
            else:
                return val
        # If the compressed index is not corrupted, 
        # this line should never be reached
        return val

    def readTermFromByteStream(self, numChars):
        term = self.vBytes[self.pos : self.pos + numChars].decode("utf-8")
        self.pos += numChars
        return term






