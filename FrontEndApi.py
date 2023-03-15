import json
import pickle
import sys
from pydantic import BaseModel
import uvicorn

from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict, Optional

from AO3_SearchEngine import Search_Engine
from SearchEngineAPIClient import SearchEngineAPIClient
from indexDecompressor import IndexDecompressor
from StoryMetadataLoader import StoryMetadataLoader
from StoryMetadataRecord import StoryMetadataRecord
from preprocessing import loadStopWordsIntoSet
from WildcardSearch import create_permuterm_index_trie

global search_engine_client

# ===============================================================
# ========================= CONSTANTS ===========================
# ===============================================================

# PATH_INDEX = "data/chapters-index-vbytes.bin"
# PATH_TAG_INDEX = "data/compressedTagIndex.bin"
# PATH_TERM_COUNTS = "data/term-counts.bin"
# PATH_DOC_TERMS = "data/doc-terms.pickle"
# PATH_METADATA = "data/compressedMetadata.bin"

# AO3_BASE = "https://archiveofourown.org/works/"

# ===============================================================
# ===================== BACKEND INTEGRATION =====================
# ===============================================================


# def load_search_engine() -> Search_Engine:
#     print("Loading search engine")
#     with open(PATH_INDEX, "rb") as f:
#         data = f.read()
#         decompressor = IndexDecompressor(data)
#         index = decompressor.toIndex()
#     print(f"Index built from {PATH_INDEX}")

#     with open(PATH_TERM_COUNTS, "rb") as f:
#         data = f.read()
#         term_counts = pickle.loads(data)
#     print(f"Term counts loaded from {PATH_TERM_COUNTS}")

#     with open(PATH_DOC_TERMS, "rb") as f:
#         data = f.read()
#         doc_terms = pickle.loads(data)

#     permuterm_index_trie = create_permuterm_index_trie(doc_terms)
#     print(f"Permuterm index tree constructed with doc terms from {PATH_DOC_TERMS}")

#     stopwords = loadStopWordsIntoSet("englishStopWords.txt")
#     print("Stopwords loaded")

#     Search_Engine(positionalInvertedIndex=index, permutermIndexTrie=permuterm_index_trie, tagIndex=)
#     return Search_Engine(index, permuterm_index_trie, stopwords, term_counts)


# def load_metadata() -> Dict[int, StoryMetadataRecord]:
#     print("Loading metadata")
#     metadata = StoryMetadataLoader.loadFromCompressedFile(PATH_METADATA)
#     print(f"Metadata loaded from {PATH_METADATA}")
#     return metadata


# ===============================================================
# ========================= API SERVER ==========================
# ===============================================================

app = FastAPI()
# seach_engine = load_search_engine()
# metadata = load_metadata()

origins = [
    "http://localhost:3002",
    "https://search.storyhunter.live"
    "localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test(request: Request):
    if request.method == 'GET':
        return JSONResponse(content="Hello World", status_code=200)


class QueryParameters(BaseModel):
    q: str
    p: int
    l: int
    tags: Optional[str] = None

    # valid filter params:
    singleChapter: bool = False


@app.get("/query")
async def read_query(request: Request):
    query_parameters = QueryParameters(**dict(request.query_params))


    # if query_parameters.tags:
    #     tags = [t for t in query_parameters.tags.split(',') if t]
    # else:
    #     tags = []
    tags = ['tag1', 'manga']
    filter_params = {}
    page = query_parameters.p
    limit = query_parameters.l
    
    print(query_parameters)
    print(tags)

    results_query = await cached_search(query_parameters.q, tags, filter_params)


    end = page * limit
    start = end - limit

    if start > len(results_query):
        results_paginated = []
    elif end > len(results_query):
        results_paginated = results_query[start:]
    else:
        results_paginated = results_query[start:end]
    return JSONResponse(content=results_paginated, status_code=200)

# @app.get("/query")
# async def read_query(request: Request):
#     search = await request.body()
#     query = json.loads(search)["query"]
#     tags = json.loads(search)["tags"]
#     filter_params = json.loads(search)["filter_params"]
#     if not filter_params:
#         filter_params = dict()
#     page = json.loads(search)["p"]
#     limit = json.loads(search)["l"]
    
#     results_query = await cached_search(query, tags, filter_params)
    
#     print(results_query)

#     end = page * limit
#     start = end - limit

#     if start > len(results_query):
#         return []
#     elif end > len(results_query):
#         results_paginated = results_query[start:]
#     else:
#         results_paginated = results_query[start:end]
#     return JSONResponse(content=results_paginated, status_code=200)


# @app.get("/query/")
# async def read_query(query: str, page: int, limit: int):
#     """
#     API endpoint exposed to the public.

#     Example request:

#         {BASE_URL}/query/?query=Doctor%20Who&page=1&limit=15
#     """
#     end = page * limit
#     start = end - limit

#     results_query = await cached_search(query)

#     if start > len(results_query):
#         return []
#     elif end > len(results_query):
#         results_paginated = results_query[start:]
#     else:
#         results_paginated = results_query[start:end]

#     return [get_story_data(story_id) for story_id, _ in results_paginated]


# ===============================================================
# ========================== CACHING ============================
# ===============================================================
# See https://github.com/aio-libs/aiocache#usage

query_results_cache = Cache(Cache.MEMORY)
ttl = 60 * 10  # How long we preserve query results for, in s
serialiser = PickleSerializer()


@cached(ttl=ttl, cache=Cache.MEMORY, serializer=serialiser)
async def cached_search(query: str, tags=[], filter_params = None):
    """
    Cache results returned from the search engine client.
    """
    return search_engine_client.query(query, tags, filter_params)


# ===============================================================
# ========================= UTILITY =============================
# ===============================================================

# def get_story_data(doc_id) -> Dict[str, str | int]:
#     """
#     """

#     # NOTE:
#     #   we ADD these fields later: [url, chapterNumber, description]
#     #   we REMOVE these fields: [_decompressedDescription]
#     expected_keys = set(
#         [
#             "storyID",
#             "title",
#             "author",
#             "_compressedDescription",
#             "currentChapterCount",
#             "finalChapterCountKnown",
#             "finalChapterCount",
#             "finished",
#             "language",
#             "wordCount",
#             "commentCount",
#             "bookmarkCount",
#             "kudosCount",
#             "hitCount",
#             "lastUpdated",
#         ]
#     )

#     story_id = doc_id // 1000
#     chapter_no = doc_id % 1000 + 1

#     # Assign default values, for when metadata not available
#     story_data = StoryMetadataRecord().__dict__

#     assert story_data.keys() == expected_keys

#     story_data.update(
#         {
#             "storyID": story_id,
#             "url": f"{AO3_BASE}{story_id}",
#             "chapterNumber": chapter_no,
#         }
#     )

#     if story_id in metadata:
#         story_data.update(metadata[story_id].__dict__)
#         del story_data['_compressedDescription']
#         story_data['description'] = metadata[story_id].getDescription()

#     return story_data

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python FrontEndApi.py <ip> <port> <se_server_ip> <se_server_port>"
        )
        sys.exit(1)

    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)

    se_ip = sys.argv[3]
    print("SE IP:", se_ip)
    se_port = int(sys.argv[4])
    print("SE Port:", se_port)

    search_engine_client = SearchEngineAPIClient(se_ip, se_port)

    uvicorn.run(app, host=ip, port=port)
