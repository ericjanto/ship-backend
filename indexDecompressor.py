from PositionalInvertedIndex import PositionalInvertedIndex


class IndexDecompressor():

    def __init__(self, vBytes):
        """
        vBytes should be a bytearray object
        """
        self.vBytes = vBytes

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

                for _ in range(numberOfOccurences):
                    delta = self.readNextIntFromByteStream()

                    position = delta + lastPosition

                    self.index.insertTermInstance(term, docID, position)

                    lastPosition = position

        return self.index



    def readNextIntFromByteStream(self):
        val = 0

        keepGoing = True

        while self.pos < len(self.vBytes):

            byteVal = self.vBytes[self.pos]

            val += byteVal % 128

            self.pos += 1

            if byteVal < 128:
                val = val << 7
            else:
                return val
        # If the compressed index is not corrupted, 
        # this line should never be reached
        return val

    def readTermFromByteStream(self, numChars):
        term = self.vBytes[self.pos : self.pos + numChars].decode("utf-8")
        self.pos += numChars
        return term






