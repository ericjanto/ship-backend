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

@app.get("/getTokensBeforeProcessing/{docID}")
async def getTokensBeforeProcessing(docID: int):
    return JSONResponse(content=index.get_tokens_before_processing(docID), status_code=200)

@app.get("/getTokensBeforeStemming/{docID}")
async def getTokensBeforeStemming(docID: int):
    return JSONResponse(content=index.get_tokens_before_stemming(docID), status_code=200)

@app.get("/getUniqueTokensBeforeProcessing/{docID}")
async def getUniqueTokensBeforeProcessing(docID: int):
    return JSONResponse(content=index.get_unique_tokens_before_processing(docID), status_code=200)

@app.get("/getUniqueTokensBeforeStemming/{docID}")
async def getUniqueTokensBeforeStemming(docID: int):
    return JSONResponse(content=index.get_unique_tokens_before_stemming(docID), status_code=200)

@app.get("/getTokensAfterStemming/{docID}")
async def getTokensAfterStemming(docID: int):
    return JSONResponse(content=index.get_tokens_after_stemming(docID), status_code=200)

@app.get("/getAllTermCounts/{docID}")
async def getAllTermCounts(docID: int):
    return JSONResponse(content=index.get_all_term_counts(docID), status_code=200)

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