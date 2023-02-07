Note: All information is accurate as of 07/02/2023, may stil be subject to change.

At the moment, there are three indexes for this project:

- the main index: A traditional posting list index as seen in cw1, documents are at a chapter level.
- the tag index: Contains sorted posting lists of docIDs for each story tagged with a given tag. Will be updated to include tag types in the near future
- the metadata index: Contains most of the information other than tags that you would see in a Story's preview on ao3. Note: On our source database, Ratings, Categories and Warnings are stored as tags, so can be found in the tag index rather than the metadata index.

The classes associated with each of these three classes are:

- PositionalInvertedIndex
- TagPositionalInvertedIndex
- Dict[StoryID, StoryMetadataRecord]

Set up:

I believe the only non-standard library currently being used is PyStemmer.

To load the three indexes, use the loadFromCompressedFile static methods in the classes:
- PositionalInvertedIndexLoader
- TagPositionalInvertedIndexLoader
- StoryMetadataLoader

Small sample indexes exist in the repository for all three indexes:

The tag and metadata indexes can be found in the data directory, and the main index is in the root directory, with the name "chapters-index-vbyte.bin"