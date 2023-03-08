### Similar to PIIServer-FastAPI.py, but with tags using the TagPositionalInvvertedIndex class

import sys
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader
import uvicorn

app = FastAPI()
index = None

@app.on_event("startup")
async def startup_event():
    global index
    global indexFile
    index = TagPositionalInvertedIndexLoader.loadFromCompressedFile(indexFile)
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

@app.post("/getTagFrequency")
async def getTagFrequency(request: Request):
    tags = await request.body()
    tags = json.loads(tags)["tags"]
    response = {}
    for tag in tags:
        response[tag] = index.getTagFrequency(tag)
    return JSONResponse(content=response, status_code=200)

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

