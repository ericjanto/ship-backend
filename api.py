import pickle

from fastapi import FastAPI
from typing import Dict

from AO3_SearchEngine import Search_Engine
from preprocessing import loadStopWordsIntoSet
from indexDecompressor import IndexDecompressor
from WildcardSearch import create_permuterm_index_trie
from StoryMetadataLoader import StoryMetadataLoader
from StoryMetadataRecord import StoryMetadataRecord


# ===============================================================
# =========================== PATHS =============================
# ===============================================================

PATH_INDEX = "data/chapters-index-vbytes.bin"
PATH_TERM_COUNTS = "data/term-counts.bin"
PATH_DOC_TERMS = "data/doc-terms.pickle"
PATH_METADATA = "data/compressedMetadata.bin"


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

    ::TODO::
    - [x] Retrieve metadata
        - StoryMetadataLoader
    - [ ] Set up query sessions (threading?) / caching
        - aio cache
    - [ ] Investigate if there's a good way to specify or validate
        the returned JSON schema
    """

    # Index the results using page and limit
    end = page * limit
    start = end - limit

    results_query = seach_engine.search(query)

    if start > len(results_query):
        return []
    elif end > len(results_query):
        results_paginated = results_query[start:]
    else:
        results_paginated = results_query[start:end]

    return [get_story_data(story_id) for story_id, _ in results_paginated]


# ===============================================================
# ========================= UTILITY =============================
# ===============================================================


def get_story_data(story_id) -> Dict[str, str | int]:
    # Assign default values, for when metadata not available
    story_data = {
        "storyID": story_id,
        "url": f"https://archiveofourown.org/works/{story_id}",
        "title": None,
        "author": None,
        "_compressedDescription": None,
        "currentChapterCount": None,
        "finalChapterCountKnown": None,
        "finalChapterCount": None,
        "finished": None,
        "language": None,
        "wordCount": None,
        "commentCount": None,
        "bookmarkCount": None,
        "kudosCount": None,
        "hitCount": None,
        "lastUpdated": None,
    }

    if story_id in metadata:
        story_data.update(metadata[story_id].__dict__)

    return story_data
