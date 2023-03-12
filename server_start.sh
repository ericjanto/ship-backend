#!/bin/bash
source ~/.bashrc

conda.bat activate AO3

python PIIServerFastAPI.py localhost 5001 data/chapters-index-vbytes.bin &
python TagPIIServerFastAPI.py localhost 5002 data/compressedTagIndex.bin &
python TermCountsServer.py localhost 5003 data/termCounts.bin &
python StoryMetadataServer.py localhost 5004 data/compressedMetadata.bin