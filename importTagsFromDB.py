import sqlite3

from TagPositionalInvertedIndex import TagPositionalInvertedIndex


class TagDBImporter():

    def __init__(self, pathToDB):
        self.conn = sqlite3.connect(pathToDB)

        self.cursor = self.conn.cursor()

        self.tagIndex = TagPositionalInvertedIndex()

    def importTagsToIndex(self, limit=None, verbose=False):

        QUERY = "SELECT TagLinks.storyId, Tags.name FROM TagLinks INNER JOIN Tags ON TagLinks.tagId = Tags.id;"

        self.cursor.execute(QUERY)

        for i, row in enumerate(self.cursor):
            if limit and i >= limit:
                break

            if verbose and i % 100000 == 0:
                print(f"Processed {i / 1000000} million tag instances.")

            storyID = int(row[0])

            tag = row[1]

            self.tagIndex.insertTagInstance(tag, storyID)

        return self.tagIndex


if __name__ == "__main__":

    from indexCompressor import tagIndexToVBytes
    from indexDecompressor import IndexDecompressor

    from TagPositionalInvertedIndexExporter import TagPositionalInvertedIndexExporter
    from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader

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


