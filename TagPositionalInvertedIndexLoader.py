import os

from TagPositionalInvertedIndex import TagPositionalInvertedIndex

from indexDecompressor import IndexDecompressor


class TagPositionalInvertedIndexLoader():

    def __init__(self):
        pass

    @staticmethod
    def loadFromCompressedFile(filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist")
        with open(filename, "rb") as f:
            compressedTagIndex = f.read()
        decompressor = IndexDecompressor(compressedTagIndex)

        return decompressor.toTagIndex()