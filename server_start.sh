#!/bin/bash

python3.9 PIIServerFastAPI.py localhost 5001 data/chapters-index-vbytes.bin &
python3.9 TagPIIServerFastAPI.py localhost 5002 data/compressedTagIndex.bin &
python3.9 TermCountsServer.py localhost 5003 data/termCounts.bin &
python3.9 StoryMetadataServer.py localhost 5004 data/compressedMetadata.bin
