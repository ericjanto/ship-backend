from AO3_SearchEngine import Search_Engine
from PIIClientFastAPI import PIIClientFlask
from TagPIIClientFastAPI import TagPIIClientFastAPI
from TermCountsClient import TermCountsClient
from StoryMetadataClient import StoryMetadataClient
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

def docID_2_document(docIDs):
    global search_engine
    global index
    global metadataIndex

    all_meta_data = metadataIndex.getStoryDescriptors([id//1000 for id in docIDs])
    all_story_excerpt = metadataIndex.getDescription([id//1000 for id in docIDs])
    documents = []
    for docID in docIDs:
        document = {'docId': 0, 
                'url': '', 
                'title': '', 
                'excerpt': ''}
        story_id = docID // 1000
        chapter_no = docID % 1000 + 1
        document['docId'] = story_id
        document['url'] = f'{base_url}works/{story_id}/chapters/{chapter_no}'
        story_meta_dat = all_meta_data.get(str(docID//1000))
        story_excerpt = all_story_excerpt.get(str(docID//1000),'')
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

    index = PIIClientFlask('localhost',5001)
    tag_index = TagPIIClientFastAPI('localhost',5002)
    term_counts = TermCountsClient('localhost',5003)
    metadataIndex = StoryMetadataClient('localhost',5004)
    with open('data/doc-terms.pickle','rb') as f:
        data = f.read()
        permu_terms = pickle.loads(data)
    permuterm_trie = create_permuterm_index_trie(permu_terms)
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
    print(query)
    tags = json.loads(search)["tags"]
    print(tags)
    filter_params = json.loads(search)["filter_params"]
    print(filter_params)
    if not filter_params:
        filter_params = dict()
    tag_str = ' '.join(['TAG{'+ tag +'}' for tag in tags])
    print(f'{tag_str} {query}')
    results = search_engine.search(f'{tag_str} {query}',**filter_params)
    
    response = docID_2_document([docID for docID,score in results])

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