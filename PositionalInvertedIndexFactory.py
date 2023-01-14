from Preprocessor import Preprocessor
from PositionalInvertedIndex import PositionalInvertedIndex
from XMLDocumentCollectionParser import XMLDocumentCollectionParser

from preprocessing import loadStopWordsIntoSet

''' 
TODO: Currently only works with the contents of a
single XML document collection
'''

class PositionalInvertedIndexFactory():

    def __init__(self):
        pass

    @staticmethod
    def generateIndexFromFile(filename, stem=True, stopwords=None):
        # TODO: Validate that filename is an XML file
        docParser = XMLDocumentCollectionParser(filename)
        documents = docParser.yieldAllRemainingDocuments()
        docIDs = [x[0] for x in documents]
        documents = [x[1] for x in documents]

        docTerms = PositionalInvertedIndexFactory.preprocessDocs(documents, stem=stem, stopwords=stopwords)

        return PositionalInvertedIndexFactory.generateIndexFromPreprocessedDocs(docTerms, docIDs)

    @staticmethod
    def generateIndexFromSpecificDocumentsInFile(filename, docIDs, stem=True, stopwords=None):
        # TODO: Validate that filename is an XML file
        docParser = XMLDocumentCollectionParser(filename)
        documents = [docParser.yieldSpecificDocument(docID) for docID in docIDs]

        docTerms = PositionalInvertedIndexFactory.preprocessDocs(documents, stem=stem, stopwords=stopwords)

        return PositionalInvertedIndexFactory.generateIndexFromPreprocessedDocs(docTerms, docIDs)

    @staticmethod
    def preprocessDocs(documents, stem=True, stopwords=None):
        preprocessed = [Preprocessor(doc, stopwords) for doc in documents]

        [pre.normaliseCases() for pre in preprocessed]

        if stopwords is not None:
            [pre.removeStopWords() for pre in preprocessed]
        if stem:
            [pre.stemTerms() for pre in preprocessed]

        # TODO: Don't really understand why I need this inner list
        #       comp, but if I don't then I get a term that is an
        #       empty string
        return [[x for x in pre.terms if x] for pre in preprocessed]

    @staticmethod
    def generateIndexFromPreprocessedDocs(documents, docIDs):
        positionalInvertedIndex = PositionalInvertedIndex()

        for document, docID in zip(documents, docIDs):
            for position, term in enumerate(document):
                positionalInvertedIndex.insertTermInstance(term, docID, position)
        return positionalInvertedIndex


if __name__ == "__main__":

    FILENAME = "trec.sample"
    stopwords = loadStopWordsIntoSet("englishStopwords.txt")
    pii = PositionalInvertedIndexFactory.generateIndexFromFile(f"data/lab2data/{FILENAME}.xml", stopwords=None, stem=False)
    pii.writeToTxtFile(f"indexes/index.{FILENAME}.txt")