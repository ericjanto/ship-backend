from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from StoryMetadataLoader import StoryMetadataLoader
import json
import sys
import uvicorn

app = FastAPI()

index = None

@app.on_event("startup")
async def startup_event():
    global index
    global indexFile
    print(indexFile)
    index = StoryMetadataLoader.loadFromCompressedFile(indexFile)
    print(list(index.keys())[:10])
    print("Index loaded")

@app.post("/getDescription")
async def getDescription(request: Request):
    request = await request.body()
    request = json.loads(request)
    storyIDs = request["storyIDs"]
    response = {}
    for storyID in storyIDs:
        if storyID in index:
            response[storyID] = index[storyID].getDescription()
        else:
            response[storyID] = dict()
    return JSONResponse(content=response, status_code=200)

@app.post("/getLastUpdated")
async def getLastUpdated(request: Request):
    request = await request.body()
    request = json.loads(request)
    storyIDs = request["storyIDs"]
    response = {}
    for storyID in storyIDs:
        if storyID in index:
            response[storyID] = index[storyID].getLastUpdated()
        else:
            response[storyID] = dict()
    return JSONResponse(content=response, status_code=200)

@app.post("/getStats")
async def getStats(request: Request):
    request = await request.body()
    request = json.loads(request)
    storyIDs = request["storyIDs"]
    response = {}
    for storyID in storyIDs:
        if storyID in index:
            response[storyID] = index[storyID].getStats()
        else:
            response[storyID] = dict()
    return JSONResponse(content=response, status_code=200)

@app.post("/getLanguage")
async def getLanguage(request: Request):
    request = await request.body()
    request = json.loads(request)
    storyIDs = request["storyIDs"]
    response = {}
    for storyID in storyIDs:
        if storyID in index:
            response[storyID] = index[storyID].getLanguage()
        else:
            response[storyID] = dict()
    return JSONResponse(content=response, status_code=200)

@app.post("/getStoryDescriptors")
async def getStoryDescriptors(request: Request):
    request = await request.body()
    request = json.loads(request)
    storyIDs = request["storyIDs"]
    response = {}
    for storyID in storyIDs:
        if storyID in index:
            response[storyID] = index[storyID].getStoryDescriptors()
        else:
            response[storyID] = dict()
    return JSONResponse(content=response, status_code=200)

if __name__ == "__main__":
    global indexFile
    if len(sys.argv) != 4:
        print("Usage: python3 StoryMetadataServer.py <ip> <port> <index file>")
        sys.exit(1)

    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    indexFile = sys.argv[3]
    print("IndexFile:", indexFile)

    uvicorn.run(app, host=ip, port=port)

