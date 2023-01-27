import re

from Preprocessor import Preprocessor

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

    def __init__(self, positionalInvertedIndex, stopwords, debugVerbose=False):
        self.index = positionalInvertedIndex
        self.stopwords = stopwords

    def makeQuery(self, query, debugVerbose=False):
        query = query.strip()
        query = query.replace("(", " ( ").replace(")", " ) ")
        query = query.replace("\"", " \" ") 
        # TODO: Handle this tokenisation properly
        query = query.split()

        if debugVerbose:
            print("before parseQuery")
            print(query)

        return self.parseQuery(query, debugVerbose=debugVerbose)

    def parseQuery(self, query, debugVerbose=False):

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
                withinProximitySearchMode = False
            else:
                newQuery.append(symbol)
            i += 1
        query = newQuery

        if debugVerbose:
            print("Post stage 0:")
            print(query)
            print()

        # Step one: Recursively process any (expr) instances
        bracketStartPos = -1
        bracketEndPos = -1
        bracketDepth = 0

        newQuery = []
        # TODO: Urgently, fix this so it will work once proximity search is working
        for pos, symbol in enumerate(query):
            if symbol == "(":
                if bracketDepth == 0 and (pos == 0 or not self.isProximitySearchMarker(query[pos-1])):
                    bracketStartPos = pos+1
                bracketDepth += 1
            elif symbol == ")":
                if bracketDepth == 1:
                    bracketEndPos = pos
                    newQuery.append(self.parseQuery(query[bracketStartPos:bracketEndPos]))

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

        # Step 2: Normalise terms

        for i in range(len(query)):
            if self.isSymbolTerm(query[i]):
                #TODO: Add in parameters somewhere to control whether or not 
                #      stopword removal or stemming occurs
                query[i] = self.preprocessQueryTerm(query[i])

        if debugVerbose:
            print("Post stage 2:")
            print(query)
            print()

        # Step 3: Handle exact search

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
                if not self.isSymbolTerm(symbol):
                    raise RuntimeError("Malformed query, non term symbols should not occur within an exact search ")
                if symbol:                    
                    exactTerms.append(symbol)
            else:
                newQuery.append(symbol)
        query = newQuery        

        if debugVerbose:
            print("Post stage 3:")
            print(query)
            print()

        # Step 4: Handle positional search

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
                newQuery.append(self.proximitySearch(proximityTerms, proximityThreshold))
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
            print("Post Stage 4:")
            print(query)
            print()

        # Convert terms into posting lists
        query = [self.findDocumentsTermOccursIn(term) if self.isSymbolTerm(term) else term for term in query]

        # Step 5: Handle the NOT cases
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
            newQuery.append(self.negate(nextSymbol))
        query = newQuery

        if debugVerbose:
            print("Post stage 5:")
            print(query)
            print()

        # Step 6: Handle the AND cases
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
            print("Post stage 6:")
            print(query)
            print()

        # Step 7: Handle the OR cases
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
            print("Post stage 7:")
            print(query)
            print()

        assert len(query) == 1

        return query[0]

    def isSymbolTerm(self, symbol):
        if self.isSymbolPostingList(symbol):
            return False
        if symbol in ["AND", "OR", "NOT", "(", ")", "\"", ")#"]:
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

    def findDocumentsTermOccursIn(self, term):
        return self.index.getDocumentsTermFoundIn(term)

    def isProximitySearchMarker(self, symbol):
        return type(symbol) != list and re.match("#\d+\(?$", symbol) is not None

    def getProximityThresholdFromMarker(self, symbol):
        return int(symbol[1:len(symbol)-1])

    def exactSearch(self, orderedTerms):
        # TODO: Error handling for when no ordered terms 
        #       are provided
        docs = self.findDocumentsTermOccursIn(orderedTerms[0])
        for i in range(1, len(orderedTerms)):
            docs = self.intersection(docs, self.findDocumentsTermOccursIn(orderedTerms[i]))

        if len(orderedTerms) == 1 or len(docs) == 0:
            return docs

        # TODO: Abstract away access to self.index.terms
        startPositions = [(docID, pos) for docID in docs for pos in self.index.terms[orderedTerms[0]][docID]]

        for i, term in enumerate(orderedTerms[1:]):
            i += 1
            #TODO: See above todo about abstraction
            startPositions = [(docID, pos) for (docID, pos) in startPositions if pos + i in self.index.terms[term][docID]]
        result = []
        for doc, _ in startPositions:
            if doc not in result:
                result.append(doc)
        return sorted(result)

    def proximitySearch(self, terms, proximityThreshold, ordered=False):
        # TODO: Error handling for when no ordered terms 
        #       are provided
        docs = self.findDocumentsTermOccursIn(terms[0])
        for i in range(1, len(terms)):
            docs = self.intersection(docs, self.findDocumentsTermOccursIn(terms[i]))

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
            for pos in self.index.terms[term][docID]:
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
            for pos in self.index.terms[term][docID]:
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

    def negate(self, docs):
        return sorted([x for x in self.index.documentIDs if x not in docs])

    def union(self, docs1, docs2):

        unionDocs = set()
        unionDocs.update(docs1)
        unionDocs.update(docs2)

        return sorted(list(unionDocs))

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