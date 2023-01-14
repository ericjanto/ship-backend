from math import log10

from preprocessing import loadStopWordsIntoSet
from Preprocessor import Preprocessor
from PositionalInvertedIndex import PositionalInvertedIndex
from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory

class RankedSearchEngine():

    def __init__(self, positionalInvertedIndex, stopwords=None, stem=True):
        self.index = positionalInvertedIndex
        self.stopwords = stopwords

        self.stem = stem

    def makeQuery(self, query):
        preprocessor = Preprocessor(query, self.stopwords)
        preprocessor.normaliseCases()
        preprocessor.removeStopWords()
        if self.stem:
            preprocessor.stemTerms()

        assert [term is not None or term != "" for term in preprocessor.terms]

        queryTerms = preprocessor.terms

        results = []

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