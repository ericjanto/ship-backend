from math import log10

from preprocessing import loadStopWordsIntoSet
from Preprocessor import Preprocessor
from PositionalInvertedIndex import PositionalInvertedIndex
from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
import WildcardSearch
from itertools import product

class RankedSearchEngine():

    def __init__(self, positionalInvertedIndex, permutermIndexTrie, stopwords=None, stem=True):
        self.index = positionalInvertedIndex
        self.permutermIndexTrie = permutermIndexTrie
        self.stopwords = stopwords

        self.stem = stem

    def makeQuery(self, query):
        expandedQueries = []
        position2term = {}
        query = query.split(" ")
        for i in range(len(query)):
            if "*" in query[i] and len(query[i]) > 1:
                query[i] = WildcardSearch.clean_wildcard_term(query[i])
                query[i] = WildcardSearch.rotate_query_term(query[i])
                expandedTerm = self.permutermIndexTrie.search(query[i])
                if expandedTerm == "NOT FOUND":
                    position2term[i] = [query[i]] #this term surely won't be in the index because it contains $ and * characters
                else:
                    position2term[i] = list(expandedTerm)
            else:
                position2term[i] = [query[i]]

        allPermutations = [dict(zip(position2term, v)) for v in product(*position2term.values())]
        expandedQueries = [" ".join(d.values()) for d in allPermutations]
        # print(expandedQueries)
        results = []

        for query in expandedQueries:
            preprocessor = Preprocessor(query, self.stopwords)
            preprocessor.normaliseCases()
            preprocessor.removeStopWords()
            if self.stem:
                preprocessor.stemTerms()

            assert [term is not None or term != "" for term in preprocessor.terms]

            queryTerms = preprocessor.terms

            for docID in self.index.documentIDs:
                similarity_score = self.queryScore(queryTerms, docID)
                if similarity_score != 0:
                    results.append((docID, round(similarity_score, 4)))

        return sorted(results, key= lambda x: x[1], reverse=True)


    def queryScore(self, queryTerms, docID):
        score = 0.0
        for term in queryTerms:
                score += self.index.tfidf(term, docID)
        return score


if __name__ == "__main__":

    FILENAME = "trec.sample"
    stopwords = loadStopWordsIntoSet("englishStopwords.txt")
    pii = PositionalInvertedIndexFactory.generateIndexFromFile(f"data/lab2data/{FILENAME}.xml", stopwords=stopwords, stem=True)
    pii.writeToTxtFile(f"indexes/index.{FILENAME}.txt")

    searchEngine = RankedSearchEngine(pii, stopwords)
    queries = ["income tax reduction", "peace in the Middle East", "unemployment rate in UK", "industry in scotland", "the industries of computers", "Microsoft Windows", "stock market in Japan", "the education with computers", "health industry", "campaigns of political parties"]
    
    with open("lab3output-max150Results-refactor-test.txt", "w") as f:

        for i, query in enumerate(queries):
            results = searchEngine.makeQuery(query)
            for (docID, score) in results[:150]:
                f.write(f"{i+1},{docID},{score}\n")

    with open("lab3output.txt", "w") as f:

        for i, query in enumerate(queries):
            results = searchEngine.makeQuery(query)
            for (docID, score) in results:
                f.write(f"{i+1},{docID},{score}\n")