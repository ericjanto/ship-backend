#!/bin/bash

python3.9 PIIServerFastAPI.py 10.132.0.4 5001 data/chapters-index-vbytes.bin &
python3.9 TagPIIServerFastAPI.py 10.132.0.4 5002 data/compressedTagIndex.bin &
python3.9 TermCountsServer.py 10.132.0.4 5003 data/termCounts.bin &
python3.9 StoryMetadataServer.py 10.132.0.4 5004 data/compressedMetadata.bin
