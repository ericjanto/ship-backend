from TagPositionalInvertedIndex import TagPositionalInvertedIndex

from indexCompressor import tagIndexToVBytes

class TagPositionalInvertedIndexExporter():

    def __init__(self):
        pass

    @staticmethod
    def saveToCompressedIndex(tagIndex, filename):
        compressedIndex = tagIndexToVBytes(tagIndex)
        with open(filename, "wb") as f:
            f.write(bytearray(compressedIndex))
