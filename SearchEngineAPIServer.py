from AO3_SearchEngine import Search_Engine
from PIIClientFastAPI import PIIClientFlask
from TagPIIClientFastAPI import TagPIIClientFastAPI
from TermCountsClient import TermCountsClient
from StoryMetadataClient import StoryMetadataClient
from WildcardSearch import create_permuterm_index_trie
from preprocessing import loadStopWordsIntoSet
# TODO: Also need story metadata client
import pandas as pd
import json
import pickle


import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
search_engine = None
index = None
metadataIndex = None
index_ip = ''

# origins = [
#     "http://localhost:3002/",
#     "https://search.storyhunter.live"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

base_url = 'https://archiveofourown.org/'

def docID_2_document(docIDs):
    global search_engine
    global index
    global metadataIndex

    all_meta_data = metadataIndex.getStoryDescriptors([int(id)//1000 for id in docIDs])
    all_story_excerpt = metadataIndex.getDescription([int(id)//1000 for id in docIDs])
    documents = []
    for docID in docIDs:
        document = {'docId': 0, 
                'url': '', 
                'title': '', 
                'excerpt': ''}
        story_id = int(docID) // 1000
        chapter_no = int(docID) % 1000 + 1
        document['docId'] = story_id
        document['url'] = f'{base_url}works/{story_id}/chapters/{chapter_no}'
        story_meta_dat = all_meta_data.get(str(int(docID)//1000))
        story_excerpt = all_story_excerpt.get(str(int(docID)//1000),'')
        if story_meta_dat:
            title = story_meta_dat.get('title')
        else:
            title = ''
        document['title'] = title
        document['excerpt'] = story_excerpt
        documents.append(document)
    return documents

@app.on_event("startup")
async def startup_event():
    global search_engine
    global index
    global metadataIndex
    global index_ip
    global tag_index

    index = PIIClientFlask(index_ip,5001)
    tag_index = TagPIIClientFastAPI(index_ip,5002)
    term_counts = TermCountsClient(index_ip,5003)
    metadataIndex = StoryMetadataClient(index_ip,5004)
    permuter_terms = pd.read_pickle('data/doc-terms.pickle')
    permuterm_trie = create_permuterm_index_trie(permuter_terms)
    stopwords = loadStopWordsIntoSet('englishStopWords.txt')
    search_engine = Search_Engine(index,permuterm_trie,tag_index,metadataIndex,stopwords,term_counts)

@app.get("/test")
def test(request: Request):
    if request.method == 'GET':
        return JSONResponse(content="Hello World", status_code=200)
    
@app.get("/query")
async def query(request: Request):
    search = await request.body()
    query = json.loads(search)["query"]
    tags = json.loads(search)["tags"]
    filter_params = json.loads(search)["filter_params"]
    if not filter_params:
        filter_params = dict()
    tag_str = ' '.join(['TAG{'+ tag +'}' for tag in tags])
    query_str = tag_str + query if len(tag_str)>0 else query
    results = search_engine.search(query_str,**filter_params)
    response = docID_2_document([docID for docID,score in results])
    return JSONResponse(content=response, status_code=200)

@app.get("/autocomplete")
async def query(prefix: str):
    completions = tag_index.get_ranked_autocomplete([(prefix, 5)])
    return JSONResponse(content=completions, status_code=200)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python SearchEngineAPIServer.py <ip> <port> <index ip>")
        sys.exit(1)
    
    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    index_ip = sys.argv[3]
    print("Index IP: ", index_ip)
    uvicorn.run(app, host=ip, port=port) 
