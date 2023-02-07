from typing import Dict

from indexCompressor import metadataIndexToVBytes
from StoryMetadataRecord import StoryMetadataRecord

class StoryMetadataExporter:

    def __init__(self):
        pass

    @staticmethod
    def saveToCompressedIndex(metadata: Dict[int, StoryMetadataRecord], filename: str) -> None:
        compressedMetadata = metadataIndexToVBytes(metadata)
        with open(filename, "wb") as f:
            f.write(bytearray(compressedMetadata))