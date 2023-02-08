from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
import pickle

class TermCounts():
## This class is used to count the number of terms in each document
    def __init__(self, docIDs, documents, stopwords):
        self.docIDs = docIDs
        assert len(self.docIDs) == len(set(self.docIDs)), "Duplicate docIDs found in the database"
        self.documents = documents
        self.stopwords = stopwords
        self.termCounts = {}
        self.__countTerms()

    def __countTerms(self):
        for docId, document in zip(self.docIDs, self.documents):
            tokens_before_processing = PositionalInvertedIndexFactory.preprocessDocs([document], stem=False)[0]
            tokens_before_stemming = PositionalInvertedIndexFactory.preprocessDocs([document], 
                                                                        stem=False, stopwords=self.stopwords)[0]

            tokens_after_stemming = len(PositionalInvertedIndexFactory.preprocessDocs([document], 
                                            stem=True, 
                                            stopwords=self.stopwords)[0]
                                        )
            tokens_before_processing_count = len(tokens_before_processing)
            tokens_before_stemming_count = len(tokens_before_stemming)
            unique_tokens_before_processing = len(set(tokens_before_processing))
            unique_tokens_before_stemming = len(set(tokens_before_stemming))
            
            self.termCounts[docId] = {"tok_befr_processing": tokens_before_processing_count,
                                        "tok_bfr_stemming": tokens_before_stemming_count,
                                        "u_tok_bfr_processing": unique_tokens_before_processing,
                                        "u_tok_bfr_stemming": unique_tokens_before_stemming,
                                        "tok_aft_stemming": tokens_after_stemming
                                        }

    def saveToBin(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.termCounts, f)
                
