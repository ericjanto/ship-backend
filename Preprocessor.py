import re
from typing import List

import Stemmer
import matplotlib.pyplot as plt

import os

class Preprocessor():

    #TODO: Make it so that this can either accept the 
    #      document as a string, or the filename

    def __init__(self, rawDocument, stopwords):

        self.stopwords = stopwords # Set

        self.stemmer = Stemmer.Stemmer('porter')

        self.terms = rawDocument

        if self.terms is not None:
            self.splitIntoTerms()
    
    def splitIntoTerms(self):

        if self.terms is None:
            raise TypeError("Cannot split None, expects self.terms to be a string")

        self.terms = re.split(r'\W+', self.terms)
        
        # Remove empty terms:
        self.terms = [term for term in self.terms if len(term) > 0]

        return self.terms

    def normaliseCases(self):
        for i, term in enumerate(self.terms):
            self.terms[i] = term.lower()
        return self.terms

    def removeStopWords(self):
        if self.stopwords is None:
            return self.terms
        self.terms = [term for term in self.terms if term not in self.stopwords]
        return self.terms

    def stemTerms(self):
        self.terms = self.stemmer.stemWords(self.terms)
        return self.terms

    def exportProcessedDocumentToFile(self, filename):
        path, file = os.path.split(filename)
        if path and not os.path.isdir(path):
            os.makedirs(path)
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines('\n'.join(self.terms).strip())

    def preprocess(self, verbose=False, removeStopWords=True, stem=True) -> List[str]:
        """
        Legacy method, intended for when the document to be preprocessed
        has been has already been passed in via the constructor.
        """
        self.normaliseCases()
        if verbose:
            print("Normalised cases")

        if removeStopWords:
            self.removeStopWords()
            if verbose:
                print("Removed stop words from")

        if stem:
            self.stemTerms()
            if verbose:
                print("Regularised")

        return self.terms

    def preprocessDocument(self, doc: str, removeStopWords: bool = True, stem: bool = True) -> str:
        """
        Rather than having to provide the documents in full when
        initialising the preprocessor, this allows
        for documents to be preprocessed as they come in.
        """
        self.terms = doc

        self.splitIntoTerms()

        self.normaliseCases()

        if removeStopWords:
            self.removeStopWords()

        if stem:
            self.stemTerms()

        return self.terms