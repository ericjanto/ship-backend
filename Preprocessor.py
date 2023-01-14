import re
import Stemmer
import matplotlib.pyplot as plt

import os

class Preprocessor():

    #TODO: Make it so that this can either accept the 
    #      document as a string, or the filename

    def __init__(self, rawDocument, stopwords, filename=None):

        self.filename = filename
        self.stopwords = stopwords # Set

        self.stemmer = Stemmer.Stemmer('porter')

        self.terms = rawDocument

        

        self.splitIntoTerms()
    
    def splitIntoTerms(self):
        self.terms = re.split(r'\W+', self.terms)
        
        # Remove empty terms:
        self.terms = [term for term in self.terms if len(term) > 0]

        return self.terms

    def normaliseCases(self):
        for i in range(len(self.terms)):
            self.terms[i] = self.terms[i].lower()
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

    def preprocess(self, verbose=False, stem=True):
        self.normaliseCases()
        if verbose:
            print("Normalised cases for " + self.filename)

        self.removeStopWords()
        if verbose:
            print("Removed stop words from " + self.filename)

        if stem:
            self.stemTerms()
            if verbose:
                print("Regularised " + self.filename)

        return self.terms