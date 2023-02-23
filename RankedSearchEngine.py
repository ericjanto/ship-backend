from math import log10

from preprocessing import loadStopWordsIntoSet
from Preprocessor import Preprocessor
from PositionalInvertedIndex import PositionalInvertedIndex
from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
import WildcardSearch
from itertools import product

class RankedSearchEngine():

    def __init__(self, positionalInvertedIndex, permutermIndexTrie, metadataDictionary, stopwords=None, stem=True):
        self.index = positionalInvertedIndex
        self.permutermIndexTrie = permutermIndexTrie
        self.metadataDictionary = metadataDictionary
        self.stopwords = stopwords

        self.stem = stem

    def makeQuery(self, query, singleChapter = False, completionStatus = "all", language = 1, wordCountFrom = -1,
        wordCountTo = -1, hitsCountFrom = -1, hitsCountTo = -1, kudosCountFrom = -1, kudosCountTo = -1, commentsCountFrom = -1, commentsCountTo = -1, bookmarksCountFrom = -1, bookmarksCountTo = -1, dateFrom = -1, dateTo = -1):
        """ Makes a query with selected filters.
        Parameters
        ----------
        query: String
            The query to search for.
        singleChapter: Boolean 
            Filter to filter out ONLY single-chapter stories. If set to false, both single-chapter and not single-chapter stories are returned.
        completionStatus: String ("all"/"completed"/"in-progress")
            Filter to filter out documents based on their completion status.
        language: Integer
            Filter to filter out documents based on used language. English language is 1. 
        wordCountFrom: Integer
            Filter to filter out documents based on their word count.
        wordCountTo: Integer
            Filter to filter out documents based on their word count.
        hitsCountFrom: Integer
            Filter to filter out documents based on the number of hits they have.
        hitsCountTo: Integer
            Filter to filter out documents based on the number of hits they have.
        kudosCountFrom: Integer
            Filter to filter out documents based on the number of kudos they have.
        kudosCountTo: Integer
            Filter to filter out documents based on the number of kudos they have.
        commentsCountFrom: Integer
            Filter to filter out documents based on the number of comments they have.
        commentsCountTo: Integer
            Filter to filter out documents based on the number of comments they have.
        bookmarksCountFrom: Integer
            Filter to filter out documents based on the number of bookmarks they have.
        bookmarksCountTo: Integer
            Filter to filter out documents based on the number of bookmarks they have.
        dateFrom: Integer (date in UNIX format or -1)
            Filter to filter out documents based on their "Last updated" date.
        dateTo: Integer (date in UNIX format or -1)
            Filter to filter out documents based on their "Last updated" date.
        
        Returns
        ----------
        answer: set(Integer)
            Matching documents sorted by their ID.
        """
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

        searchScope = list(self.filterDocs(singleChapter = singleChapter, completionStatus = completionStatus, language = language, wordCountFrom = wordCountFrom, wordCountTo = wordCountTo, hitsCountFrom = hitsCountFrom, hitsCountTo = hitsCountTo, kudosCountFrom = kudosCountFrom, kudosCountTo = kudosCountTo, commentsCountFrom = commentsCountFrom, commentsCountTo = commentsCountTo, bookmarksCountFrom = bookmarksCountFrom, bookmarksCountTo = bookmarksCountTo, dateFrom = dateFrom, dateTo = dateTo))

        for query in expandedQueries:
            preprocessor = Preprocessor(query, self.stopwords)
            preprocessor.normaliseCases()
            preprocessor.removeStopWords()
            if self.stem:
                preprocessor.stemTerms()

            assert [term is not None or term != "" for term in preprocessor.terms]

            queryTerms = preprocessor.terms

            for docID in searchScope:
                similarity_score = self.queryScore(queryTerms, docID)
                if similarity_score != 0:
                    results.append((docID, round(similarity_score, 4)))

        return sorted(results, key= lambda x: x[1], reverse=True)


    def queryScore(self, queryTerms, docID):
        score = 0.0
        for term in queryTerms:
                score += self.index.tfidf(term, docID)
        return score
    
    def parameterWithinBoundary(self, parameter, lowerBound, upperBound):
        return (lowerBound == -1 or parameter >= lowerBound) and (upperBound == -1 or parameter <= upperBound)
    
    def filterDocs(self, singleChapter, completionStatus, language, wordCountFrom, wordCountTo, hitsCountFrom, hitsCountTo, kudosCountFrom, kudosCountTo, commentsCountFrom, commentsCountTo, bookmarksCountFrom, bookmarksCountTo, dateFrom, dateTo):
        """ From all the documents, filters those documents that match the set filters. In the main 'for loop', checking a document terminates early if some condition is not met.
        Parameters
        ----------
        see makeQuery params
        
        Returns
        ----------
        answer: list(Integer)
            Filtered documents.
        """
        allStoryIDs = self.metadataDictionary.keys()
        filteredStoryIDs = []

        for id in allStoryIDs:
            storyInfo = self.metadataDictionary[id]

            chapterCountMatch = (not singleChapter) or (singleChapter and storyInfo.finalChapterCountKnown and storyInfo.finalChapterCount == 1) or (singleChapter and (not storyInfo.finalChapterCountKnown) and storyInfo.currentChapterCount == 1)
            if not chapterCountMatch:
                continue
            completionStatusMatch = (completionStatus == "all") or (completionStatus == "completed" and storyInfo.finished) or (completionStatus == "in-progress" and not storyInfo.finished)
            if not completionStatusMatch:
                continue
            languageMatch = storyInfo.language == language
            if not languageMatch:
                continue
            wordCountMatch = self.parameterWithinBoundary(storyInfo.wordCount, wordCountFrom, wordCountTo)
            if not wordCountMatch:
                continue
            hitsCountMatch = self.parameterWithinBoundary(storyInfo.hitCount, hitsCountFrom, hitsCountTo)
            if not hitsCountMatch:
                continue
            kudosCountMatch = self.parameterWithinBoundary(storyInfo.kudosCount, kudosCountFrom, kudosCountTo)
            if not kudosCountMatch:
                continue
            commentsCountMatch = self.parameterWithinBoundary(storyInfo.commentCount, commentsCountFrom, commentsCountTo)
            if not commentsCountMatch:
                continue
            bookmarksCountMatch = self.parameterWithinBoundary(storyInfo.bookmarkCount, bookmarksCountFrom, bookmarksCountTo)
            if not bookmarksCountMatch:
                continue
            dateMatch = self.parameterWithinBoundary(storyInfo.lastUpdated, dateFrom, dateTo)
            if not dateMatch:
                continue

            # if we reach here, the condition should always be True
            if chapterCountMatch and completionStatusMatch and languageMatch and wordCountMatch and hitsCountMatch and kudosCountMatch and commentsCountMatch and bookmarksCountMatch and dateMatch:
                filteredStoryIDs.append(id)

        filteredStoryIDs = set(filteredStoryIDs)

        allDocs = self.index.getDocIDs()
        filteredDocs = set()

        for doc in allDocs:
            storyID = doc / 1000
            if storyID in filteredStoryIDs:
                filteredDocs.add(doc)

        return filteredDocs



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