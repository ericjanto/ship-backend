from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
from Preprocessor import Preprocessor 
import pickle

class TermCounts():
## This class is used to count the number of terms in each document
    def __init__(self, stopwords):
        self.stopwords = stopwords
        self.termCounts = {}
        self.preprocessor = Preprocessor(None, self.stopwords)

    def countTerms(self, docIDs, documents)->None:
        for docId, document in zip(docIDs, documents):
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

    def countTermsRowWise(self, row, docId):
        """
        Counts the number of terms in a row and save it to the termCounts dictionary
        """
        # Do nothing if the docId is not in the termCounts dictionary
        if docId in self.termCounts:
            print(f"Duplicate docID: {docId} found! Skipping...")
            return
        tokens_before_processing = self.preprocessor.preprocessDocument(row, removeStopWords=False, stem=False)
        tokens_before_stemming = self.preprocessor.removeStopWords()
        tokens_after_stemming = self.preprocessor.stemTerms()

        tokens_before_processing_count = len(tokens_before_processing)
        tokens_before_stemming_count = len(tokens_before_stemming)
        unique_tokens_before_processing = len(set(tokens_before_processing))
        unique_tokens_before_stemming = len(set(tokens_before_stemming))

        tokens_after_stemming_count = len(tokens_after_stemming)

        self.termCounts[docId]  = [ 
                                    tokens_before_processing_count, 
                                    tokens_before_stemming_count, 
                                    unique_tokens_before_processing, 
                                    unique_tokens_before_stemming,
                                    tokens_after_stemming_count
                                    ]
                
