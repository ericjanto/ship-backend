import pickle

from fastapi import FastAPI

from AO3_SearchEngine import Search_Engine
from preprocessing import loadStopWordsIntoSet
from indexDecompressor import IndexDecompressor
from WildcardSearch import create_permuterm_index_trie


# ===============================================================
# ====================== UTILITY FUNCTIONS ======================
# ===============================================================


def init_search_engine() -> Search_Engine:
    """
    Instantiates a search engine.
    """
    print("Please wait for the search engine to load")
    with open("data/chapters-index-vbytes.bin", "rb") as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()

    print("Index built")
    with open("data/term-counts.bin", "rb") as f:
        data = f.read()
        term_counts = pickle.loads(data)

    print("Term counts Loaded")

    with open("data/doc-terms.pickle", "rb") as f:
        data = f.read()
        doc_terms = pickle.loads(data)

    permuterm_index_trie = create_permuterm_index_trie(doc_terms)
    print("permuterm index tree constructed")

    stopwords = loadStopWordsIntoSet("englishStopWords.txt")
    print("Stopwords loaded")

    return Search_Engine(index, permuterm_index_trie, stopwords, term_counts)


# ===============================================================
# ========================= API SERVER ==========================
# ===============================================================

app = FastAPI()
seach_engine = init_search_engine()


@app.get("/query/")
async def read_items(query: str, page: int, limit: int):
    """
    API endpoint exposed to the public.

    Example request:

        {BASE_URL}/query/?query=Doctor%20Who&page=1&limit=15

    ::TODO::
    - [ ] Retrieve more than doc num only
    - [ ] Set up query sessions (threading?)
    - [ ] Investigate if there's a good way to specify or validate
        the returned JSON schema
    """
    query_results = seach_engine.search(query)

    # Index the results using page and limit
    end = page * limit
    start = end - limit

    if start > len(query_results):
        return []
    elif end > len(query_results):
        return query_results[start:]
    else:
        return query_results[start:end]

