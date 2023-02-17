import pickle

from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from fastapi import FastAPI
from typing import Dict

from AO3_SearchEngine import Search_Engine
from indexDecompressor import IndexDecompressor
from StoryMetadataLoader import StoryMetadataLoader
from StoryMetadataRecord import StoryMetadataRecord
from preprocessing import loadStopWordsIntoSet
from WildcardSearch import create_permuterm_index_trie


# ===============================================================
# ========================= CONSTANTS ===========================
# ===============================================================

PATH_INDEX = "data/chapters-index-vbytes.bin"
PATH_TERM_COUNTS = "data/term-counts.bin"
PATH_DOC_TERMS = "data/doc-terms.pickle"
PATH_METADATA = "data/compressedMetadata.bin"

AO3_BASE = "https://archiveofourown.org/works/"

# ===============================================================
# ===================== BACKEND INTEGRATION =====================
# ===============================================================


def load_search_engine() -> Search_Engine:
    print("Loading search engine")
    with open(PATH_INDEX, "rb") as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()
    print(f"Index built from {PATH_INDEX}")

    with open(PATH_TERM_COUNTS, "rb") as f:
        data = f.read()
        term_counts = pickle.loads(data)
    print(f"Term counts loaded from {PATH_TERM_COUNTS}")

    with open(PATH_DOC_TERMS, "rb") as f:
        data = f.read()
        doc_terms = pickle.loads(data)

    permuterm_index_trie = create_permuterm_index_trie(doc_terms)
    print(f"Permuterm index tree constructed with doc terms from {PATH_DOC_TERMS}")

    stopwords = loadStopWordsIntoSet("englishStopWords.txt")
    print("Stopwords loaded")

    return Search_Engine(index, permuterm_index_trie, stopwords, term_counts)


def load_metadata() -> Dict[int, StoryMetadataRecord]:
    print("Loading metadata")
    metadata = StoryMetadataLoader.loadFromCompressedFile(PATH_METADATA)
    print(f"Metadata loaded from {PATH_METADATA}")
    return metadata


# ===============================================================
# ========================= API SERVER ==========================
# ===============================================================

app = FastAPI()
seach_engine = load_search_engine()
metadata = load_metadata()


@app.get("/query/")
async def read_query(query: str, page: int, limit: int):
    """
    API endpoint exposed to the public.

    Example request:

        {BASE_URL}/query/?query=Doctor%20Who&page=1&limit=15
    """
    end = page * limit
    start = end - limit

    results_query = await cached_search(query)

    if start > len(results_query):
        return []
    elif end > len(results_query):
        results_paginated = results_query[start:]
    else:
        results_paginated = results_query[start:end]

    return [get_story_data(story_id) for story_id, _ in results_paginated]


# ===============================================================
# ========================== CACHING ============================
# ===============================================================
# See https://github.com/aio-libs/aiocache#usage

query_results_cache = Cache(Cache.MEMORY)
ttl = 60 * 10  # How long we preserve query results for, in s
serialiser = PickleSerializer()


@cached(ttl=ttl, cache=Cache.MEMORY, serializer=serialiser)
async def cached_search(query: str):
    """
    Cache results returned from the search engine.
    """
    return seach_engine.search(query)


# ===============================================================
# ========================= UTILITY =============================
# ===============================================================


def get_story_data(doc_id) -> Dict[str, str | int]:
    """
    """
    expected_keys = set(
        [
            "storyID",
            "title",
            "author",
            "_compressedDescription",
            "currentChapterCount",
            "finalChapterCountKnown",
            "finalChapterCount",
            "finished",
            "language",
            "wordCount",
            "commentCount",
            "bookmarkCount",
            "kudosCount",
            "hitCount",
            "lastUpdated",
        ]
    )

    story_id = doc_id // 1000
    chapter_no = doc_id % 1000 + 1

    # Assign default values, for when metadata not available
    story_data = StoryMetadataRecord().__dict__

    assert story_data.keys() == expected_keys

    story_data.update(
        {
            "storyID": story_id,
            "url": f"{AO3_BASE}{story_id}",
            "chapterNumber": chapter_no,
        }
    )

    if story_id in metadata:
        story_data.update(metadata[story_id].__dict__)
        del story_data['_compressedDescription']
        story_data['description'] = metadata[story_id].getDescription()

    return story_data
