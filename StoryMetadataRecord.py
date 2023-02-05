import zlib

class StoryMetadataRecord():

    def __init__(self) -> None:
        self.storyID = None
        self.title = None
        self.author = None
        
        # Note: Should be treated as a private field,
        # only access via getters and setters so it can
        # be compressed and decompressed reliably.
        self._compressedDescription = None

        self.currentChapterCount = None

        # These fields should be set using the 
        # provided setter method, setFinalChapterCount
        self.finalChapterCountKnown = False
        self.finalChapterCount = None

        self.finished = False

        self.language = None

        self.wordCount = None

        self.commentCount = None
        self.bookmarkCount = None
        self.kudosCount = None
        self.hitCount = None

        # All dates are strings in the YYYY/MM/DD format
        self.lastUpdated = None

    def setFinalChapterCount(self, finalChapterCount: int) -> None:
        if finalChapterCount is None:
            self.finalChapterCountKnown = False
            self.finalChapterCount = 0
        else:
            self.finalChapterCountKnown = True
            self.finalChapterCount = finalChapterCount


    def setDescription(self, description: str) -> None:
        # Given the description field for a Story, compresses
        # the string and stores it within the record

        # convert the description string to a bytes object
        bytesDescription = description.encode(encoding="utf-8")

        # compress the description
        self._compressedDescription = zlib.compress(bytesDescription)


    def getDescription(self) -> str:
        # Decompresses and returns the description field for the Story
        return zlib.decompress(self._compressedDescription).decode(encoding="utf-8")
