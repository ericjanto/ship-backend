import sqlite3

from typing import Dict

from StoryMetadataRecord import StoryMetadataRecord

class MetadataImporter():

    def __init__(self, pathToDB):
        self.conn = sqlite3.connect(pathToDB)

        self.cursor = self.conn.cursor()

        self.metadataIndex = dict()

        self.numStoriesMissingMetadata = 0

    def importMetadata(self, limit=None, verbose=None) -> Dict[int, StoryMetadataRecord]:
        QUERY = """SELECT 
                      StoryHeaders.id, StoryHeaders.title, Authors.name, 
                      StoryHeaders.description, StoryHeaders.curChapters, 
                      StoryHeaders.maxChapters, StoryHeaders.finished,
                      StoryHeaders.language, StoryHeaders.words, 
                      StoryHeaders.comments, StoryHeaders.bookmarks, 
                      StoryHeaders.kudos, StoryHeaders.hits, 
                      STRFTIME('%Y/%m/%d', StoryHeaders.date)
                FROM StoryHeaders 
                LEFT JOIN AuthorLinks ON StoryHeaders.id = AuthorLinks.storyId
                LEFT JOIN Authors ON AuthorLinks.authorId = Authors.id;
                """
        self.cursor.execute(QUERY)

        for i, row in enumerate(self.cursor):
            if limit and i >= limit:
                break

            if row[1] is None and row[2] is None:
                # is no title and no author enough to say that
                # the metadata is missing? Probably, imo
                self.numStoriesMissingMetadata += 1
                continue

            #TODO: these min calls are hacky at best, see if better
            # way to do things
            storyMetadata = StoryMetadataRecord()
            storyMetadata.storyID = max(int(row[0]), 0)
            storyMetadata.title = row[1]
            storyMetadata.author = row[2]
            storyMetadata.setDescription(row[3])
            storyMetadata.currentChapterCount = max(int(row[4]), 0)
            storyMetadata.setFinalChapterCount(int(row[5]))
            storyMetadata.finished = bool(row[6])
            storyMetadata.language = max(int(row[7]), 0)
            storyMetadata.wordCount = max(int(row[8]), 0)
            storyMetadata.commentCount = max(int(row[9]), 0)
            storyMetadata.bookmarkCount = max(int(row[10]), 0)
            storyMetadata.kudosCount = max(int(row[11]), 0)
            storyMetadata.hitCount = max(int(row[12]), 0)
            storyMetadata.lastUpdated = row[13]

            self.metadataIndex[storyMetadata.storyID] = storyMetadata

            if verbose and i % 100000 == 0:
                print(f"Imported metadata records for {i/1000000} million stories")

        print(self.numStoriesMissingMetadata)
        return self.metadataIndex



if __name__ == "__main__":
    PATH_TO_DB = r"F:\SmallerDB.sqlite3"

    PATH_TO_METADATA_INDEX = "data/compressedMetadata.bin"
    importer = MetadataImporter(PATH_TO_DB)

    metadata = importer.importMetadata(verbose=True, limit=1000000)

    from indexCompressor import metadataIndexToVBytes
    from indexDecompressor import IndexDecompressor

    print(len(metadata))

    compressedIndex = metadataIndexToVBytes(metadata)

    print(len(compressedIndex))


    with open(PATH_TO_METADATA_INDEX, "wb") as f:
        f.write(bytearray(compressedIndex))

    with open(PATH_TO_METADATA_INDEX, "rb") as f:
        compressedTagIndex = f.read()
    decompressor = IndexDecompressor(compressedTagIndex)

    decompressedMetadata = decompressor.toMetadataIndex()

    print(len(decompressedMetadata))

    print(metadata == decompressedMetadata)

