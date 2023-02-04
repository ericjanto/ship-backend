import numpy as np
import multiprocessing as mp

from PositionalInvertedIndex import PositionalInvertedIndex
from Preprocessor import Preprocessor

# Placeholder Method to get the number of terms after preprocessing in a document.
def get_Document_Length(docID):
    pass

# Placeholder Method to get the average number of terms after preprocessing in a document.
def get_Average_Document_Length():
    pass

class BM25_Model():
    def __init__(self,positionalInvertedIndex,stopwords):
        self.index = PositionalInvertedIndex()
        self.stopwords = stopwords

    def preprocess_query(self,query,removeStopWords=True,stem=True):
        preprocessor = Preprocessor(query,self.stopwords)
        preprocessor.normaliseCases()
        if removeStopWords:
            preprocessor.removeStopWords()
        if stem:
            preprocessor.stemTerms()
        if len(preprocessor.terms) == 0:
            return ""
        return preprocessor.terms[0]

    def score_document(self,query,doc_nos):
        # TODO: k is a hyperparameter which can be tuned later on. Currently using best
        # practise value given from the lectures.
        k = 1.5
        results = []
        for doc_no in doc_nos:
            doc_score = 0
            for term in query:
                tf = self.index.tf(term,doc_no)
                df = self.index.df(term)
                L_d = get_Document_Length(doc_no)
                avg_L = get_Average_Document_Length()
                N = self.index.documentCount
                term_1 = tf/(k*(L_d/avg_L) + tf + 0.5)
                term_2 = np.log10((N-df+0.5)/(df+0.5))
                doc_score += term_1 * term_2
            results += (doc_no,doc_score)
        return results
    
    def partition_data(self,data_idxs,no_of_partitions):
        splits = []
        data_size = len(data_idxs)
        chunk_size = data_size // no_of_partitions
        chunk_start = 0

        while chunk_start < data_size:
            chunk_end = chunk_start + min(data_size-chunk_start,chunk_size)
            splits += [data_idxs[chunk_start:chunk_end]]
            chunk_start = chunk_end
        
        return splits

    def ranked_search(self,query):
        query_terms = self.preprocess_query(query)
        doc_IDs = list(self.index.documentIDs)
        no_of_processes = mp.cpu_count() - (mp.cpu_count()//4)

        doc_partitions = self.partition_data(doc_IDs,no_of_processes)
        pool = mp.Pool(processes=no_of_processes)
        results = [pool.apply_async(self.score_document,(query_terms,doc_IDs,)) for doc_IDs in doc_partitions]
        results = [score.get() for score in results]
        ranked_docs = sum(results,[])
        return ranked_docs