from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from TermCountsLoader import TermCountsLoader
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
    index = TermCountsLoader.loadFromFile(indexFile)
    
    print("Index loaded")

@app.post("/getTokensBeforeProcessing")
async def getTokensBeforeProcessing(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_tokens_before_processing(docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getTokensBeforeStemming")
async def getTokensBeforeStemming(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_tokens_before_stemming(docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getUniqueTokensBeforeProcessing")
async def getUniqueTokensBeforeProcessing(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_unique_tokens_before_processing(docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getUniqueTokensBeforeStemming")
async def getUniqueTokensBeforeStemming(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_unique_tokens_before_stemming(docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getTokensAfterStemming")
async def getTokensAfterStemming(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_tokens_after_stemming(docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getAllTermCountsForDocIds")
async def getAllTermCountsForDocIds(request: Request):
    docIDs = await request.body()
    docIDs = json.loads(docIDs)["docIDs"]
    response = {}
    for docID in docIDs:
        response[docID] = index.get_all_term_counts_for(docID)
    return JSONResponse(content=response, status_code=200)

@app.get("/getAllTermCounts")
async def getAllTermCounts():
    return JSONResponse(content=index.get_all_term_counts(), status_code=200)

@app.put("/appendIntoTermCounts")
async def appendIntoTermCounts(request: Request):
    termCounts = await request.body()
    termCounts = json.loads(termCounts)["termCounts"]
    for termCount in termCounts:
        index.append_into_term_counts(termCount)
    return JSONResponse(content="Appended!", status_code=200)


if __name__ == "__main__":
    global indexFile
    if len(sys.argv) != 4:
        print("Usage: python3 TermCountsServer.py <ip> <port> <index file>")
        sys.exit(1)

    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    indexFile = sys.argv[3]
    print("IndexFile:", indexFile)

    uvicorn.run(app, host=ip, port=port)