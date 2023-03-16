import re
from Preprocessor import Preprocessor
from itertools import product
import WildcardSearch

class BooleanSearchEngine():

    '''
    QUERY GRAMMAR TREE:

    QUERY => expr
    expr  => expr AND expr
    expr  => expr OR expr
    expr  => NOT expr 
    expr  => (expr)
    expr  => #n(List<term>)
    expr  => "List<term>"
    expr  => term
    '''

    def __init__(self, positionalInvertedIndex, permutermIndexTrie, metadataDictionary, stopwords, debugVerbose=False):
        self.index = positionalInvertedIndex
        self.permutermIndexTrie = permutermIndexTrie
        self.stopwords = stopwords
        self.metadataDictionary = metadataDictionary

    # Making query with filters. Parameter set to -1 means that this filter is not active.
    def makeQuery(self, query, debugVerbose=False, singleChapter = False, completionStatus = "all", language = 1, wordCountFrom = -1,
        wordCountTo = -1, hitsCountFrom = -1, hitsCountTo = -1, kudosCountFrom = -1, kudosCountTo = -1, commentsCountFrom = -1, commentsCountTo = -1, bookmarksCountFrom = -1, bookmarksCountTo = -1, dateFrom = -1, dateTo = -1):
        """ Makes a query with selected filters.
        Parameters
        ----------
        query: String
            The query to search for. Format: phrase (incl. inter wildcards), proximity, logical operators query
        debugVerbose: Boolean
            Flag indicating whether debugging output should be printed out.
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
        query = query.strip()
        query = query.replace("(", " ( ").replace(")", " ) ")
        query = query.replace("\"", " \" ") 
        # TODO: Handle this tokenisation properly
        query = query.split()

        if debugVerbose:
            print("before parseQuery")
            print(query)

        return self.parseQuery(query, debugVerbose=debugVerbose, singleChapter = singleChapter, completionStatus = completionStatus, language = language, wordCountFrom = wordCountFrom, wordCountTo = wordCountTo, hitsCountFrom = hitsCountFrom, hitsCountTo = hitsCountTo, kudosCountFrom = kudosCountFrom, kudosCountTo = kudosCountTo, commentsCountFrom = commentsCountFrom, commentsCountTo = commentsCountTo, bookmarksCountFrom = bookmarksCountFrom, bookmarksCountTo = bookmarksCountTo, dateFrom = dateFrom, dateTo = dateTo)

    # Parsing query with filters.
    def parseQuery(self, query, debugVerbose, singleChapter, completionStatus, language, wordCountFrom, wordCountTo, hitsCountFrom, hitsCountTo, kudosCountFrom, kudosCountTo, commentsCountFrom, commentsCountTo, bookmarksCountFrom, bookmarksCountTo, dateFrom, dateTo):

        # Step 0: Modify brackets for proximity search to simplify
        #         Step 1
        #         NOTE: Explicitly assumes that there are no brackets 
        #               inside the proximity search (TODO: Fix)
        newQuery = [query[0]]
        i = 1
        withinProximitySearchMode = False
        while i < len(query):
            symbol = query[i]
            if symbol == "(":
                if self.isProximitySearchMarker(newQuery[len(newQuery) -1]):
                    withinProximitySearchMode = True
                    marker = newQuery.pop()
                    newQuery.append(marker + symbol)
                else:
                    newQuery.append(symbol)

            elif symbol == ")" and withinProximitySearchMode:
                newQuery.append(symbol + "#")
                # withinProximitySearchMode = False
            else:
                newQuery.append(symbol)
            i += 1
        query = newQuery

        if debugVerbose:
            print("Post stage 0:")
            print(query)
            print()

        # Step 1: Recursively process any (expr) instances
        bracketStartPos = -1
        bracketEndPos = -1
        bracketDepth = 0

        newQuery = []
        for pos, symbol in enumerate(query):
            if symbol == "(":
                if bracketDepth == 0 and (pos == 0 or not self.isProximitySearchMarker(query[pos-1])):
                    bracketStartPos = pos+1
                bracketDepth += 1
            elif symbol == ")":
                if bracketDepth == 1:
                    bracketEndPos = pos
                    newQuery.append(self.parseQuery(query[bracketStartPos:bracketEndPos], debugVerbose=debugVerbose, singleChapter = singleChapter, completionStatus = completionStatus, language = language, wordCountFrom = wordCountFrom, wordCountTo = wordCountTo, hitsCountFrom = hitsCountFrom, hitsCountTo = hitsCountTo, kudosCountFrom = kudosCountFrom, kudosCountTo = kudosCountTo, commentsCountFrom = commentsCountFrom, commentsCountTo = commentsCountTo, bookmarksCountFrom = bookmarksCountFrom, bookmarksCountTo = bookmarksCountTo, dateFrom = dateFrom, dateTo = dateTo))

                bracketDepth -= 1
            elif bracketDepth == 0:
                newQuery.append(symbol)

        # If brackets are mismatched, throw exception for malformed query
        if bracketDepth != 0:
            raise RuntimeError("Mismatched brackets in search query")
        query = newQuery

        if debugVerbose:
            print("Post stage 1:")
            print(query)
            print()

        
        # Step 2: Expand terms with *
        expandedQueries = []
        position2term = {}
        # separate search terms for proximity search
        separated = False
        if withinProximitySearchMode and len(query) == 3:
            splitPart = query[1].split(",")
            query = [query[0]] + splitPart + [query[-1]]
            separated = True
        for i in range(len(query)):
            if not self.isSymbolTerm(query[i]):
                position2term[i] = [query[i]]

            elif "*" in query[i] and len(query[i]) > 1:
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
        expandedQueries = [list(d.values()) for d in allPermutations]

        if debugVerbose:
            print("Post stage 2:")
            print(expandedQueries)
            print()

        # TODO: fix proximity search 

        answer = set()
        searchScope = self.index.getDocIDs()
        for query in expandedQueries:        
            # Step 3: Normalise terms
            for i in range(len(query)):
                if self.isSymbolTerm(query[i]):
                    #TODO: Add in parameters somewhere to control whether or not 
                    #      stopword removal or stemming occurs
                    query[i] = self.preprocessQueryTerm(query[i])

            if debugVerbose:
                print("Post stage 3:")
                print(query)
                print()

            # Step 4: Handle exact search

            newQuery = []
            exactTerms = []
            withinExactSearchMode = False
            for symbol in query:
                if symbol == "\"":
                    withinExactSearchMode = not withinExactSearchMode

                    if not withinExactSearchMode and len(exactTerms) > 0:
                        newQuery.append(self.exactSearch(exactTerms))
                    exactTerms = []
                    continue
                if withinExactSearchMode:
                    if self.isWildCard(symbol):
                        exactTerms.append(symbol)
                    elif not self.isSymbolTerm(symbol):
                        raise RuntimeError("Malformed query, non term symbols should not occur within an exact search ")
                    elif symbol:                    
                        exactTerms.append(symbol)
                else:
                    newQuery.append(symbol)
            query = newQuery        

            if debugVerbose:
                print("Post stage 4:")
                print(query)
                print()

            # Step 5: Handle positional search

            newQuery = []
            withinProximitySearchMode = False
            proximityThreshold = -1
            proximityTerms = []
            i = 0
            while i < len(query):
                # TODO: Assumes that there only terms within proximity search brackets
                symbol = query[i]
                if self.isProximitySearchMarker(symbol):
                    withinProximitySearchMode = True
                    proximityThreshold = self.getProximityThresholdFromMarker(symbol)
                elif symbol == ")#":
                    if not withinProximitySearchMode:
                        raise RuntimeError("Malformed query, proximity search closed before it was opened")
                    withinProximitySearchMode = False
                    newQuery.append(self.proximitySearch(proximityTerms, proximityThreshold, searchScope))
                    proximityTerms = []
                    proximityThreshold = -1
                else:
                    if not withinProximitySearchMode:
                        newQuery.append(symbol)
                    else:
                        if not self.isSymbolTerm(symbol):
                            raise RuntimeError("Malformed query, non term symbol found inside proximity search")
                        proximityTerms.append(symbol)
                i += 1
            if withinProximitySearchMode:
                raise RuntimeError("Malformed query: proximity search missing closing bracket")

            query = newQuery

            if debugVerbose:
                print("Post Stage 5:")
                print(query)
                print()

            # Convert terms into posting lists
            posting_terms_idxs = [term for term in query if self.isSymbolTerm(term)]
            postings = self.findDocumentsTermOccursIn(posting_terms_idxs)
            query = [postings.get(term,term) if self.isSymbolTerm(term) else term for term in query]
            # Step 6: Handle the NOT cases
            i = 0
            newQuery = []
            while i < len(query):
                symbol = query[i]
                i += 1
                if symbol != "NOT":
                    newQuery.append(symbol)
                    continue
                if i == len(query):
                    # TODO: Ask about if this needs to be able to handle
                    #       malformed queries
                    continue

                nextSymbol = query[i]            
                i += 1

                if not self.isSymbolPostingList(nextSymbol):
                    continue
                newQuery.append(self.negate(nextSymbol, list(searchScope)))
            query = newQuery

            if debugVerbose:
                print("Post stage 6:")
                print(query)
                print()

            # Step 7: Handle the AND cases
            i = 0
            newQuery = []
            while i < len(query):
                symbol = query[i]
                if symbol != "AND":
                    newQuery.append(symbol)
                    i += 1
                    continue

                if i == 0 or i == len(query) - 1:
                    # TODO: This is a malformed query, should handle this
                    #       at some point
                    i += 1
                    continue
                previousSymbol = newQuery[len(newQuery) - 1]
                nextSymbol = query[i + 1]
                if not (self.isSymbolPostingList(previousSymbol) and self.isSymbolPostingList(nextSymbol)):
                # TODO: Another malformed query (nothing AND TERM) or (TERM AND nothing)
                    i += 1
                    continue
                i += 2
                newQuery.pop(len(newQuery) - 1)
                newQuery.append(self.intersection(previousSymbol, nextSymbol))

            query = newQuery

            if debugVerbose:
                print("Post stage 7:")
                print(query)
                print()

            # Step 8: Handle the OR cases
            i = 0
            newQuery = []
            while i < len(query):
                symbol = query[i]
                if symbol != "OR":
                    newQuery.append(symbol)
                    i += 1
                    continue

                if i == 0 or i == len(query) - 1:
                    # TODO: This is a malformed query, should handle this
                    #       at some point
                    i += 1
                    continue
                previousSymbol = newQuery[len(newQuery) - 1]
                nextSymbol = query[i + 1]
                if not (self.isSymbolPostingList(previousSymbol) and self.isSymbolPostingList(nextSymbol)):
                # TODO: Another malformed query (nothing OR TERM) or (TERM OR nothing)
                    i += 1
                    continue
                i += 2
                newQuery.pop(len(newQuery) - 1)
                newQuery.append(self.union(previousSymbol, nextSymbol))

            query = newQuery

            if debugVerbose:
                print("Post stage 8:")
                print(query)
                print()

            assert len(query) == 1

            answer.update(query[0])

        return sorted(answer)

    def isWildCard(self, symbol):
        return symbol == "*"

    def isSymbolTerm(self, symbol):
        if self.isSymbolPostingList(symbol):
            return False
        if symbol in ["AND", "OR", "NOT", "(", ")", "\"", ")#", "*"]:
            return False
        if self.isProximitySearchMarker(symbol):
            return False
        return True

    def isSymbolPostingList(self, symbol):
        # TODO: I don't like what this is called, rename, and possibly
        #       refactor the codebase so it isn't required.
        return type(symbol) == list

    def preprocessQueryTerm(self, term, removeStopWords=True, stem=True):
        # TODO: If the preprocessor splits the term into more than one
        #       because of non alphanumeric characters, handle that case
        preprocessor = Preprocessor(term, stopwords=self.stopwords)
        preprocessor.normaliseCases()
        if removeStopWords:
            preprocessor.removeStopWords()
        if stem:
            preprocessor.stemTerms()
            #TODO: Is this how I want to handle it?
        if len(preprocessor.terms) == 0:
            return ""
        return preprocessor.terms[0]
    
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
            storyID = doc // 1000
            if storyID in filteredStoryIDs:
                filteredDocs.add(doc)

        return filteredDocs


    def findDocumentsTermOccursIn(self, terms):
        return self.index.getDocumentsTermOccursIn(terms)

    def isProximitySearchMarker(self, symbol):
        return type(symbol) != list and re.match("#\d+\(?$", symbol) is not None

    def getProximityThresholdFromMarker(self, symbol):
        return int(symbol[1:len(symbol)-1])

    def removeSubsequentStars(self, orderedTerms):
        previousStar = False
        cleanedTerms = []
        for term in orderedTerms:
            if term == "*" and previousStar:
                continue
            elif term == "*" and not previousStar:
                cleanedTerms.append(term)
                previousStar = True
            else:
                previousStar = False
                cleanedTerms.append(term)
        
        return cleanedTerms


    # In exact search which supports wild card inter queries, we can have 3 cases:
    # 1) * is at the very beginning of a phrase - done
    # 2) * is between 2 words - done
    # 3) * is at the very end of a phrase - not done, is it worth it to handle this small edge case (?)
    def exactSearch(self, orderedTerms):
        # TODO: Error handling for when no ordered terms 
        #       are provided
        orderedTerms = self.removeSubsequentStars(orderedTerms)

        # if query consists only from *, this query is meaningless:
        if len(orderedTerms) == 1 and orderedTerms[0] == "*":
            return []

        startIndex = 0 if orderedTerms[0] != "*" else 1 # index of first non-star term
        
        postings = self.findDocumentsTermOccursIn(orderedTerms)
        docs = postings.get(orderedTerms[startIndex],[])

        # find docs for remaining words:
        for i in range(startIndex + 1, len(orderedTerms)):
            if orderedTerms[i] == "*":
                continue 
            docs = self.intersection(docs, postings.get(orderedTerms[i],[])) # docs contain all common docs

        if len(orderedTerms) == 1 or len(docs) == 0:
            return docs

        # TODO: Abstract away access to self.index.terms
        # handles 1) case where * is at the very beginning of a phrase
        if startIndex == 1:
            #previousTermPositions = [(docID, pos) for docID in docs for pos in self.index.getPostingList([(orderedTerms[startIndex],docID)]).get(orderedTerms[startIndex]) if pos != 0]
            postinglist = self.index.getPostingList([(orderedTerms[startIndex],docID) for docID in docs]).get(orderedTerms[startIndex])
            previousTermPositions = [(docID,pos) for docID in postinglist for pos in postinglist[docID] if pos != 0]
        else:
            #previousTermPositions = [(docID, pos) for docID in docs for pos in self.index.getPostingList([(orderedTerms[startIndex],docID)]).get(orderedTerms[startIndex])]
            postinglist = self.index.getPostingList([(orderedTerms[startIndex],docID) for docID in docs]).get(orderedTerms[startIndex])
            previousTermPositions = [(docID,pos) for docID in postinglist for pos in postinglist[docID]]

        # handles 2) case where * is between 2 words
        previousStar = False
        post_list = self.index.getPostingList([(term,docID) for term in orderedTerms[(startIndex+1):] for (docID, pos) in previousTermPositions])
        for i, term in enumerate(orderedTerms[(startIndex+1):]):
            #TODO: See above todo about abstraction
            if term != "*" and previousStar: # for terms which come after *
                newPositions = []
                for (docID, pos) in previousTermPositions: 
                    for pos2 in range(pos + 2, pos + 21): # O(1); upper limit - 20 terms (a sentence) in between 
                        if pos2 in post_list[term][docID]:
                            newPositions.append((docID, pos2))
                previousTermPositions = newPositions
                previousStar = False 
            elif term != "*" and not previousStar: # for terms which come after another term
                newPositions = []
                for (docID, pos) in previousTermPositions:
                    if (pos + 1) in post_list[term][docID]:
                        newPositions.append((docID, pos + 1))
                previousTermPositions = newPositions
                previousStar = False
            else: # for * terms
                previousStar = True

        result = []
        for doc, _ in previousTermPositions:
            if doc not in result:
                result.append(doc)
        return sorted(result)

    def proximitySearch(self, terms, proximityThreshold, searchScope, ordered=False):
        # TODO: Error handling for when no ordered terms 
        #       are provided
        postings = self.findDocumentsTermOccursIn(terms)
        docs = postings.get(terms[0],[])
        for i in range(1, len(terms)):
            docs = self.intersection(docs, postings.get(terms[i],[]))

        if len(terms) == 1 or len(docs) == 0:
            return docs
        ## TODO: Finish
        result = []
        for docID in docs:
            if self.termsOccurWithinProximityInDocument(terms, docID, proximityThreshold):
                result.append(docID)
        return sorted(result)

    def termsOccurWithinProximityInDocument(self, terms, docID, proximityThreshold):
        instances = []
        # Build positional list
        for term in terms:
            for pos in self.index.getPostingList([(term,docID)])[term][docID]:
                instances.append((term, pos))
        instances = sorted(instances, key=lambda x: x[1])



        # Check that for terms t_1, ..., t_n, that for
        # all t_i, t_j s.t. i != j, pos_diff(t_i, t_j) < proximityThreshold
        # TODO: This can be made more efficient
        for i in range(len(instances)):
            term, pos = instances[i]
            termsWithinProximity = set()
            termsWithinProximity.add(term)
            for j in range(i+1, len(instances)):
                otherTerm, otherPos = instances[j]
                if otherTerm in termsWithinProximity:
                    continue
                # Assumption: difference between first and last term positions
                #             must be no more than the proximity threshold
                if otherPos - pos > proximityThreshold:
                    break
                termsWithinProximity.add(otherTerm)
                if len(termsWithinProximity) == len(terms):
                    return True
        return False

    def orderedTermsWithinProximityInDocument(self, terms, docID, proximityThreshold):
        instances = []
        for term in terms:
            for pos in self.index.getPostingList([(term,docID)]).get(term):
                instances.append(term,pos)
        instances = sorted(instances, key=lambda x: x[1])

        curr_term = 0
        for i in range(len(instances)):
            term, pos = instances[i]
            if term == terms[curr_term]:
                termsWithinProximity = set()
                termsWithinProximity.add(term)
                curr_term = 1
                for j in range(i+1, len(instances)):
                    otherTerm, otherPos = instances[j]
                    if otherTerm == terms[curr_term]:
                        if otherTerm in termsWithinProximity:
                            continue
                        if otherPos - pos > proximityThreshold:
                            curr_term = 0
                            break
                        termsWithinProximity.add(otherTerm)
                        curr_term += 1
                        if len(termsWithinProximity) == len(terms):
                            return True

        return False

    def negate(self, docs, searchScope):
        return sorted([x for x in searchScope if x not in docs])

    def union(self, docs1, docs2):

        unionDocs = set()
        unionDocs.update(docs1)
        unionDocs.update(docs2)

        return sorted(list(unionDocs))

    # NB: to use this intersection function, documents must be ordered!
    def intersection(self, docs1, docs2):
        intersection = []
        p1 = 0
        p2 = 0
        while (p1 < len(docs1) and p2 < len(docs2)):
            if docs1[p1] == docs2[p2]:
                intersection.append(docs1[p1])
                p1 += 1
                p2 += 1
            elif docs1[p1] < docs2[p2]:
                p1 += 1
            else:
                p2 += 1
        return intersection