#!/bin/bash

python3.9 PIIServerFastAPI.py 10.132.0.4 5001 data/compressed-chapter-indexes-emergency-query/ y &
python3.9 TagPIIServerFastAPI.py 10.132.0.4 5002 data/compressedTagIndexFull.bin &
python3.9 TermCountsServer.py 10.132.0.4 5003 data/termCountsFull.bin &
python3.9 StoryMetadataServer.py 10.132.0.4 5004 data/compressedMetadataFull.bin
