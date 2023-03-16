import sys
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader
import uvicorn
import os
from Autocompleter import Autocompleter

app = FastAPI()
index = None
autocompleter = None

@app.on_event("startup")
async def startup_event():
    global index
    global indexFile
    global autocompleter
    autocompleter = Autocompleter(indexFile)
    index = autocompleter.tag_index
    print("Index loaded")

@app.get("/test")
def test(request: Request):
    if request.method == 'GET':
        return JSONResponse(content="Hello World", status_code=200)

@app.post("/getStoryIDsWithTag")
async def getStoryIDsWithTag(request: Request):
    tags = await request.body()
    tags = json.loads(tags)["tags"]
    response = {}
    for tag in tags:
        response[tag] = index.getStoryIDsWithTag(tag)
    return JSONResponse(content=response, status_code=200)

@app.post("/autocomplete")
async def get_ranked_autocomplete(request:Request):
    global autocompleter
    pairs = await request.body()
    pairs = json.loads(pairs)["pairs"]
    results = {}
    for prefix, n in pairs:
        if prefix not in results:
            results[prefix] = {}
        results[prefix][n] = autocompleter.get_ranked_autocomplete(prefix, n)
    return JSONResponse(content=results, status_code=200)


@app.post("/getTagFrequency")
async def getTagFrequency(request: Request):
    tags = await request.body()
    tags = json.loads(tags)["tags"]
    response = {}
    for tag in tags:
        response[tag] = index.getTagFrequency(tag)
    return JSONResponse(content=response, status_code=200)

@app.put("/mergeWithOtherIndex")
async def mergeWithOtherIndex(request: Request):
    global index
    dateFileNames = await request.body()
    dateFileNames = json.loads(dateFileNames, parse_int=int)["dateFileNames"]
    for dateFileName in dateFileNames:
        # path = "./data/WebScraperImports/WebScraped-Tags/" + dateFileName
        path = "./data/" + dateFileName
        if os.path.exists(path):
            tagIndex = TagPositionalInvertedIndexLoader.loadFromCompressedFile(path)
            index.mergeWithOtherIndex(tagIndex)
    return JSONResponse(content="Done Merging!", status_code=200)

@app.put("/mergeWithOtherIndexAllDates")
async def mergeWithOtherIndexAllDates():
    global index
    path = "./data/WebScraperImports/WebScraped-Tags/"
    # list all files in the directory
    for fileName in os.listdir(path):
        tagIndex = TagPositionalInvertedIndexLoader.loadFromCompressedFile(path+fileName)
        index.mergeWithOtherIndex(tagIndex)
    return JSONResponse(content="Done Merging!", status_code=200)

if __name__ == '__main__':
    global indexFile
    if len(sys.argv) != 4:
        print("Usage: python3 PIIServer-FastAPI.py <ip> <port> <index file>")
        sys.exit(1)
    
    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    indexFile = sys.argv[3]
    print("IndexFile:", indexFile)

    uvicorn.run(app, host=ip, port=port)

