from AO3_SearchEngine import Search_Engine
from PIIClientFastAPI import PIIClientFlask
from TagPIIClientFastAPI import TagPIIClientFastAPI
from TermCountsClient import TermCountsClient
from WildcardSearch import create_permuterm_index_trie
from preprocessing import loadStopWordsIntoSet
# TODO: Also need story metadata client
import json
import pickle

import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
search_engine = None
index = None
metadataIndex = None

base_url = 'https://archiveofourown.org/'

def docID_2_document(docID):
    global search_engine
    global index
    global metadataIndex

    document = {'docId': 0, 
                'url': '', 
                'title': '', 
                'excerpt': ''}
    story_id = docID // 1000
    chapter_no = docID % 1000 + 1
    document['docId'] = story_id
    document['url'] = f'{base_url}works/{story_id}/chapters/{chapter_no}'
    document['title'] = metadataIndex[docID].title
    document['excerpt'] = metadataIndex[docID].getDescription()
    return document

@app.on_event("startup")
async def startup_event():
    global search_engine
    global index
    index = PIIClientFlask('localhost',5001)
    tag_index = TagPIIClientFastAPI('localhost',5002)
    term_counts = TermCountsClient('localhost',5003)
    metadataIndex = {-20:'dummy'}
    with open('data/termCounts.bin','rb') as f:
        data = f.read()
        term_counts = pickle.loads(data)
    permuterm_trie = create_permuterm_index_trie(term_counts)
    stopwords = loadStopWordsIntoSet('englishStopWords.txt')
    search_engine = Search_Engine(index,permuterm_trie,tag_index,metadataIndex,stopwords,term_counts)

@app.get("/test")
def test(request: Request):
    if request.method == 'GET':
        return JSONResponse(content="Hello Worlds", status_code=200)
    
@app.post("/query")
async def query(request: Request):
    search = await request.body()
    query = json.loads(search)["query"]
    tags = json.loads(search)["tags"]
    filter_params = json.loads(search)
    response = []
    tag_str = ' '.join(['TAG{'+ tag +'}' for tag in tags])
    results = search_engine.search(f'{tag_str} {query}',filter_params)
    
    for docID, score in results:
        response.append(docID_2_document(docID))

    return JSONResponse(content=response, status_code=200)



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python SearchEngineAPIServer.py <ip> <port>")
        sys.exit(1)
    
    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    uvicorn.run(app, host=ip, port=port) 