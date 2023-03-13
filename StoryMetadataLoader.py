import os
from typing import Dict

from StoryMetadataRecord import StoryMetadataRecord

from indexDecompressor import IndexDecompressor

class StoryMetadataLoader:

    def __init__(self):
        pass

    @staticmethod
    def loadFromCompressedFile(filename: str) -> Dict[int, StoryMetadataRecord]:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist")
        with open(filename, "rb") as f:
            compressedMetadataIndex = f.read()
        decompressor = IndexDecompressor(compressedMetadataIndex)

        return decompressor.toMetadataIndex()

    @staticmethod
    def mergeChunkIntoIndex(existing: Dict[int, StoryMetadataRecord],
                            chunk: Dict[int, StoryMetadataRecord]) -> None:
        """
        Inserts the contents of a smaller metadata index (chunk)
        into an index that already exists loaded within memory (existing).

        If the same story ID is present within both indexes, will retain
        whichever one was more recently updated.

        Returns nothing, as existing is a reference, and as such its contents
        will be modified within this method call.
        """

        for storyID in chunk.keys():
            if storyID in existing and existing[storyID].lastUpdated > chunk[storyID].lastUpdated:
                continue
            else:
                existing[storyID] = chunk[storyID]