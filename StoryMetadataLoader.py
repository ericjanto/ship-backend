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