import bisect
from math import log10
import pickle
from typing import Set

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

        bisect.insort(self.terms[docID], position)

    def insertPostingList(self, term: str, docID: int, positions: List[int]) -> None:
        """ 
        TODO: Make this faster when inserting into a posting
        list that already exists
        """
        if docID not in self.documentIDs:
            self.documentIDs.add(docID)
            self.documentCount += 1

        if term not in self.terms:
            self.terms[term] = dict()

        if docID not in self.terms[term]:
            self.terms[term][docID] = positions
        else:
            # TODO:
            # This method explicitly assumes that a
            # specific posting being added is not already
            # in the index. For our use case, this isn't a problem
            # due to how we split the index on importing, but it is
            # worth looking at
            for pos in positions:
                self.terms.insertTermInstance(term, docID, pos)

    def getDistinctTermsCount(self):
        return len(self.terms.keys())
    
    # NB: not super accurate, because some languages have words which consist of ascii characters only (e.g. "amore" in Italian)
    def getEnglishTermsCount(self):
        count = 0
        for term in self.terms.keys():
            if len(term.encode('ascii', errors='ignore').decode('utf-8')) == len(term):
                count += 1
        return count


    def getTermFrequency(self, term: str, docID: int) -> int:
        ''' Count the number of times a term occurred in a document. '''
        if term not in self.terms:
            return 0
        if docID not in self.terms[term]:
            return 0
        return len(self.terms[term][docID])


    def getDocFrequency(self, term: str) -> int:
        if term not in self.terms:
            return 0
        return len(self.terms[term])


    def getDocumentsTermOccursIn(self, term: str) -> List[int]:
        """
        Returns the docID of every doc that contains the specified term
        """
        if term not in self.terms:
            return []
        return list(self.terms[term].keys())

    def getPostingList(self, term: str, docID: int) -> List[int]:
        """
        Returns the posting list of a term in a specified document ID
        """
        
        if term not in self.terms or docID not in  self.terms[term]:
            return []
        
        return self.terms[term][docID]


    def tfidf(self, term: str, docID: int) -> float:
        '''
        Computes the tf-idf score for a term in a 
        document from the indexed collection.

        If either the tf or df value are zero, will
        return 0
        '''
        if self.getDocFrequency(term) == 0 or self.getTermFrequency(term, docID) == 0:
            return 0
        return (1 + log10(self.getTermFrequency(term, docID))) * log10(self.documentCount / self.getDocFrequency(term))

    def getNumDocs(self) -> int:
        """
        Returns the total number of documents
        contained within the index
        """
        return self.documentCount

    def getDocIDs(self) -> Set[int]:
        """
        Returns the set of documentIDs corresponding
        to all the documents present in the index
        """

        return self.documentIDs

    def mergeWithOtherIndex(self, other) -> None:
        """Merges the contents of another index into this one"""
        for term in other.terms:
            for docID in other.terms[term]:
                self.insertPostingList(term, docID, other.terms[term][docID])

    def __eq__(self, other) -> bool:
        if not isinstance(other, PositionalInvertedIndex):
            return False

        return (self.terms == other.terms 
                and self.documentIDs == other.documentIDs 
                and self.documentCount == other.documentCount)

