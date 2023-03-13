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

        # All dates are strings in the UNIX format
        self.lastUpdated = None

    def setAuthor(self, author) -> None:
        # TODO: currently a hacky workaround for the
        # fact that this isn't handling multiple authors properly
        if isinstance(author, list):
            self.author = ", ".join(author)
        else:
            self.author = author

    def setFinalChapterCount(self, finalChapterCount: int) -> None:
        if finalChapterCount is None or finalChapterCount < 0:
            self.finalChapterCountKnown = False
            self.finalChapterCount = 0
        else:
            self.finalChapterCountKnown = True
            self.finalChapterCount = finalChapterCount


    def setDescription(self, description: str) -> None:
        # Given the description field for a Story, compresses
        # the string and stores it within the record

        if description is None:
            description = ""

        # convert the description string to a bytes object
        bytesDescription = description.encode(encoding="utf-8")

        # compress the description
        self._compressedDescription = zlib.compress(bytesDescription)


    def getDescription(self) -> str:
        # Decompresses and returns the description field for the Story
        return zlib.decompress(self._compressedDescription).decode(encoding="utf-8")

    def __eq__(self, other):
        if not isinstance(other, StoryMetadataRecord):
            return False

        return (self.storyID == other.storyID
                and self.title == other.title
                and self.author == other.author
                and self._compressedDescription == other._compressedDescription
                and self.currentChapterCount == other.currentChapterCount
                and self.finalChapterCount == other.finalChapterCount
                and self.finalChapterCountKnown == other.finalChapterCountKnown
                and self.finished == other.finished
                and self.language == other.language
                and self.wordCount == other.wordCount
                and self.commentCount == other.commentCount
                and self.kudosCount == other.kudosCount
                and self.bookmarkCount == other.bookmarkCount
                and self.hitCount == other.hitCount
                and self.lastUpdated == other.lastUpdated)