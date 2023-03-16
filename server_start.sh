#!/bin/bash

python3.9 PIIServerFastAPI.py localhost 5001 data/compressed-chapter-indexes-emergency-query/ y &
python3.9 TagPIIServerFastAPI.py localhost 5002 data/compressedTagIndexFull.bin &
python3.9 TermCountsServer.py localhost 5003 data/termCountsFull.bin &
python3.9 StoryMetadataServer.py localhost 5004 data/compressedMetadataFull.bin
