import sqlite3
from typing import Set

from TagPositionalInvertedIndex import TagPositionalInvertedIndex

from Preprocessor import Preprocessor


class TagDBImporter():

    def __init__(self, pathToDB):

        self.QUERY = "SELECT TagLinks.storyId, Tags.name FROM TagLinks INNER JOIN Tags ON TagLinks.tagId = Tags.id;"

        self.conn = sqlite3.connect(pathToDB)

        self.cursor = self.conn.cursor()

    def importTagsToIndex(self, limit=None, verbose=False) -> TagPositionalInvertedIndex:

        tagIndex = TagPositionalInvertedIndex()

        self.cursor.execute(self.QUERY)

        for i, row in enumerate(self.cursor):
            if limit and i >= limit:
                break

            if verbose and i % 100000 == 0:
                print(f"Processed {i / 1000000} million tag instances.")

            storyID = int(row[0])

            # Reduce all tags to lower case, to make autocomplete easier

            tag = row[1].lower()

            tagIndex.insertTagInstance(tag, storyID)

        return tagIndex

    def importAndPreprocessTagsToIndex(self, stopwords: Set[str], limit=None, verbose=False) -> TagPositionalInvertedIndex:
        tagIndex = TagPositionalInvertedIndex()

        self.cursor.execute(self.QUERY)

        for i, row in enumerate(self.cursor):
            if limit and i >= limit:
                break

            if verbose and i % 100000 == 0:
                print(f"Processed {i / 1000000} million tag instances.")

            storyID = int(row[0])

            tag = row[1]

            #TODO: This is inefficient, want to have a preprocessor set up
            # which doesn't have to have the raw document on initialisation,
            # and can pass in new strings on demand
            preprocessedTagTerms = Preprocessor(tag, stopwords).preprocess(removeStopWords=False)


            for term in preprocessedTagTerms:
                tagIndex.insertTagInstance(term, storyID)

        return tagIndex


if __name__ == "__main__":

    from indexCompressor import tagIndexToVBytes
    from indexDecompressor import IndexDecompressor

    from TagPositionalInvertedIndexExporter import TagPositionalInvertedIndexExporter
    from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader

    from preprocessing import loadStopWordsIntoSet
    STOPWORDS_PATH = "englishStopWords.txt"
    stopwords = loadStopWordsIntoSet(STOPWORDS_PATH)

    PATH_TO_DB = r"F:\SmallerDB.sqlite3"

    importer = TagDBImporter(PATH_TO_DB)

    index = importer.importTagsToIndex(verbose=True, limit=10000000)

    compressedIndex = bytearray(tagIndexToVBytes(index))

    decompressor = IndexDecompressor(compressedIndex)

    decompressedIndex = decompressor.toTagIndex()

    print(index == decompressedIndex)

    ## TEST THAT WRITING THEN READING TO FILE WORKS

    SAVE_TO = "data/compressedTagIndex.bin"

    TagPositionalInvertedIndexExporter.saveToCompressedIndex(index, SAVE_TO)

    readInIndex = TagPositionalInvertedIndexLoader.loadFromCompressedFile(SAVE_TO)

    print(index == readInIndex)

    # preprocessedTagIndex = importer.importAndPreprocessTagsToIndex(stopwords, limit=10000000, verbose=True)
    #
    # PREPROCESSED_INDEX_PATH = "data/compressedPreprocessedTagIndex.bin"
    #
    # TagPositionalInvertedIndexExporter.saveToCompressedIndex(preprocessedTagIndex,PREPROCESSED_INDEX_PATH)
    #
    # readInPreprocessedIndex = TagPositionalInvertedIndexLoader.loadFromCompressedFile(PREPROCESSED_INDEX_PATH)
    #
    # print(preprocessedTagIndex == readInPreprocessedIndex)


