from typing import Dict

from PositionalInvertedIndex import PositionalInvertedIndex
from StoryMetadataRecord import StoryMetadataRecord
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

            term = self.readNCharsFromByteStream(termLength)

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

            tag = self.readNCharsFromByteStream(tagLength)

            storyIDCount = self.readNextIntFromByteStream()

            lastStoryID = 0

            storyIDs = [0] * storyIDCount

            for i in range(storyIDCount):
                delta = self.readNextIntFromByteStream()

                storyID = delta + lastStoryID

                storyIDs[i] = storyID

                lastStoryID = storyID

            self.index.insertStoryIDs(tag, storyIDs)

        return self.index

    def toMetadataIndex(self) -> Dict[int, StoryMetadataRecord]:
        self.index = dict()

        numStories = self.readNextIntFromByteStream()

        for _ in range(numStories):
            metadataRecord = StoryMetadataRecord()

            metadataRecord.storyID = self.readNextIntFromByteStream()

            metadataRecord.title = self.readNextStrFromByteStream()
            metadataRecord.author = self.readNextStrFromByteStream()

            metadataRecord._compressedDescription = self.readRawBytesFromByteStream()

            flagState = self.readNextIntFromByteStream()
            if flagState % 2 == 1:
                metadataRecord.finished = True
            if flagState >= 2:
                metadataRecord.finalChapterCountKnown = True
            else:
                metadataRecord.finalChapterCount = 0

            metadataRecord.currentChapterCount = self.readNextIntFromByteStream()

            if metadataRecord.finalChapterCountKnown:
                metadataRecord.finalChapterCount = self.readNextIntFromByteStream()

            metadataRecord.language = self.readNextIntFromByteStream()

            metadataRecord.wordCount = self.readNextIntFromByteStream()
            metadataRecord.commentCount = self.readNextIntFromByteStream()
            metadataRecord.bookmarkCount = self.readNextIntFromByteStream()
            metadataRecord.kudosCount = self.readNextIntFromByteStream()
            metadataRecord.hitCount = self.readNextIntFromByteStream()

            metadataRecord.lastUpdated = self.readNextIntFromByteStream()

            self.index[metadataRecord.storyID] = metadataRecord

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

    def readRawBytesFromByteStream(self):
        numBytes = self.readNextIntFromByteStream()
        rawBytes = self.vBytes[self.pos : self.pos + numBytes]
        self.pos += numBytes
        return rawBytes

    def readNextStrFromByteStream(self):
        strLength = self.readNextIntFromByteStream()
        return self.readNCharsFromByteStream(strLength)

    def readNCharsFromByteStream(self, numChars):
        term = self.vBytes[self.pos : self.pos + numChars].decode("utf-8")
        self.pos += numChars
        return term






