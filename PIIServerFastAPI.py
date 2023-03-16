from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from PositionalInvertedIndexLoader import PositionalInvertedIndexLoader
import json
import sys
import uvicorn

app = FastAPI()
index = None

@app.on_event("startup")
async def startup_event():
    global index
    global indexFile
    global fullScale
    if fullScale:
        index = PositionalInvertedIndexLoader.loadFromMultipleCompressedFiles(indexFile, chunk_limit=30, verbose=True)
    else:
        index = PositionalInvertedIndexLoader.loadFromCompressedFile(indexFile)

    print("Index loaded")

@app.get("/getDistinctTermsCount")
async def getDistinctTermsCount(request: Request):
    return JSONResponse(content=index.getDistinctTermsCount(), status_code=200)

@app.get("/getEnglishTermsCount")
async def getEnglishTermsCount(request: Request):
    return JSONResponse(content=index.getEnglishTermsCount(), status_code=200)

@app.post("/getTermFrequency")
async def getTermFrequency(request: Request):
    pairs = await request.body()
    pairs = json.loads(pairs, parse_int=int)["pairs"]
    response = {}
    for term, docID in pairs:
        if term not in response:
            response[term] = dict()
        response[term][docID] = index.getTermFrequency(term, docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/getDocFrequency")
async def getDocFrequency(request: Request):
    terms = await request.body()
    terms = json.loads(terms, parse_int=int)["terms"]
    response = {}
    for term in terms:
        response[term] = index.getDocFrequency(term)
    return JSONResponse(content=response, status_code=200)

@app.post("/getDocumentsTermOccursIn")
async def getDocumentsTermOccursIn(request: Request):
    terms = await request.body()
    terms = json.loads(terms, parse_int=int)["terms"]
    response = {}
    for term in terms:
        response[term] = index.getDocumentsTermOccursIn(term)
    return JSONResponse(content=response, status_code=200)

@app.post("/getPostingList")
async def getPostingList(request: Request):
    pairs = await request.body()
    pairs = json.loads(pairs, parse_int=int)["pairs"]
    response = {}
    for term, docID in pairs:
        if term not in response:
            response[term] = dict()
        response[term][docID] = index.getPostingList(term, docID)
    return JSONResponse(content=response, status_code=200)

@app.post("/tfidf")
async def tfidf(request: Request):
    pairs = await request.body()
    pairs = json.loads(pairs, parse_int=int)["pairs"]
    response = {}
    for term, docID in pairs:
        if term not in response:
            response[term] = dict()
        response[term][docID] = index.tfidf(term, docID)
    return JSONResponse(content=response, status_code=200)

@app.get("/getNumDocs")
async def getNumDocs(request: Request):
    return JSONResponse(content=index.getNumDocs(), status_code=200)

@app.get("/getDocIDs")
async def getDocIDs(request: Request):
    list_of_docIDs = list(index.getDocIDs()) # Since set is not serializable
    return JSONResponse(content=list_of_docIDs, status_code=200)

    
if __name__ == '__main__':
    global fullScale
    global indexFile
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print("Usage: python3 PIIServerFastAPI.py <ip> <port> <index file> <full scale mode (y/n)>")
        sys.exit(1)

    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    indexFile = sys.argv[3]
    print("IndexFile:", indexFile)
    if len(sys.argv) == 5:
        fullScale = True if sys.argv[5].lower().startswith("y") else False
    else:
        fullScale = False
    print("Loading full index:", fullScale)

    uvicorn.run(app, host=ip, port=port)