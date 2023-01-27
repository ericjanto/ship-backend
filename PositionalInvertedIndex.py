from math import log10
import pickle
from indexCompressor import *

class PositionalInvertedIndex():

    ''' Structure (In pseudo-java syntax)
        HashMap<Term, HashMap<DocID, List<Position>>
    '''

    def __init__(self):
        self.terms = dict()

        self.documentIDs = set()

        # Will be useful for boolean searches including NOT
        self.documentCount = 0

    def insertTermInstance(self, term, docID, position):
        if docID not in self.documentIDs:
            self.documentIDs.add(docID)
            self.documentCount += 1

        if term not in self.terms:
            self.terms[term] = dict()
        if docID not in self.terms[term]:
            self.terms[term][docID] = []
        #TODO: This uses a O(n) linear scan, but could be reduced to 
        #      use a binary search instead. However, given that inserting
        #      into the list still has O(n) runtime, it might not provide
        #      much benefit
        for i in range(len(self.terms[term][docID])):
            if position == self.terms[term][docID][i]:
                return
            if position < self.terms[term][docID][i]:
                self.terms[term][docID].insert(i, position)
                return
        self.terms[term][docID].append(position)

    def insertPostingList(self, term, docID, positions):
        """ 
        Should only use this when importing an existing
        index, and never when adding new entries to an existing
        index. This is because this will override the postings
        list for term at docID.

        positions must be a list
        """
        if docID not in self.documentIDs:
            self.documentIDs.add(docID)
            self.documentCount += 1

        if term not in self.terms:
            self.terms[term] = dict()

        self.terms[term][docID] = positions

    def getTermDocumentFrequency(self, term):
        if term not in self.terms:
            return 0
        return len(self.terms[term])

    def getDocumentsTermFoundIn(self, term):
        if term not in self.terms:
            return []
        return list(self.terms[term].keys())
        

    def tf(self, term, docID):
        ''' Count the number of times a term occured in a document. '''
        if term not in self.terms:
            return 0
        if docID not in self.terms[term]:
            return 0
        return len(self.terms[term][docID])

    def df(self, term):
        '''
        Count the number of documents where the specified 
        term occurs at least once.
        '''
        if term not in self.terms:
            return 0
        return len(self.terms[term])

    def tfidf(self, term, docID):
        '''
        Computes the tf-idf score for a term in a 
        document from the indexed collection.

        If either the tf or df value are zero, will
        return 0
        '''
        if self.df(term) == 0 or self.tf(term, docID) == 0:
            return 0
        return (1 + log10(self.tf(term, docID))) * log10(self.documentCount / self.df(term))

    # Largely keeping this so that we don't have to re-index, in case there are any [future] bugs with index compression
    def writeToBinary(self, filename): 
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        

    def __eq__(self, other):
        if not isinstance(other, PositionalInvertedIndex):
            return False

        return (self.terms == other.terms 
                and self.documentIDs == other.documentIDs 
                and self.documentCount == other.documentCount)

