import numpy as np
from multiprocessing import Manager
from multiprocessing import Pool
from multiprocessing import cpu_count

from PositionalInvertedIndex import PositionalInvertedIndex
from Preprocessor import Preprocessor

# Placeholder Method to get the number of terms after preprocessing in a document.
def get_Document_Lengths(docIDs,index):
    doc_len = 0
    for docID in docIDs:
        for term in index.terms.keys():
            appearances = index.terms[term].get(docID,[])
            doc_len += len(appearances)
    return doc_len

# Placeholder Method to get the average number of terms after preprocessing in a document.
def get_Average_Document_Length(index):
    no_of_processes = (cpu_count()//4)
    doc_splits = partition_data(list(index.documentIDs),no_of_processes)
    pool = Pool(processes=no_of_processes)
    results = [pool.apply_async(get_Document_Lengths,(split,index,)) for split in doc_splits]
    results = [process.get() for process in results]
    total_len = sum(results)
    pool.terminate()
    return total_len / index.documentCount

def partition_data(data_idxs,no_of_partitions):
    """Helper function to partition data into chunks for preprocessing.
    Parameters
    -----------
    data_idxs: List[int]
        List of data identifiers, e.g document IDs
    no_of_partitions: int
        Number of partitions to split the data into
    Returns
    -----------
    List[List[int]]
        A list of lists containing document IDs
    """
    splits = []
    data_size = len(data_idxs)
    chunk_size = data_size // no_of_partitions
    chunk_start = 0

    while chunk_start < data_size:
        chunk_end = chunk_start + min(data_size-chunk_start,chunk_size)
        splits += [data_idxs[chunk_start:chunk_end]]
        chunk_start = chunk_end
    
    return splits

class BM25_Model():
    """Class follows Okapi BM25 model for information retrieval which scores the documents
    following a probabilistic model.  
    """
    def __init__(self,positionalInvertedIndex,stopwords):
        """
        Parameters
        ----------
        positionalInvertedIndex: PositionalInvertedIndex
            An instance of the inverted index which provides an API that allows for 
            retrieval of term-document information.
        stopwords: List[String]
            A list of common english words that a removed from the documents and a
            query.
        """
        self.index = positionalInvertedIndex
        self.stopwords = stopwords
        self.average_Doc_Len = get_Average_Document_Length(positionalInvertedIndex)

    def preprocess_query(self,query,removeStopWords=True,stem=True):
        """Processes a set of terms by performing case folding, stopword removal and
        stemming.
        Parameters
        ----------
        query: String
            The query given by the user
        removeStopWords: bool, default True
            Whether to remove stopwords from the given query
            If True, commonly used english words are removed from the users query
        stem: bool, default True
            Whether to apply Porter stemmer to the words.
            If True, words are stemmed to their roots.
        Returns
        ----------
        terms: List[String]
            A List of processed words after case folding, stopword removal and stemming.
        """
        preprocessor = Preprocessor(query,self.stopwords)
        preprocessor.normaliseCases()
        if removeStopWords:
            preprocessor.removeStopWords()
        if stem:
            preprocessor.stemTerms()
        if len(preprocessor.terms) == 0:
            return ""
        return preprocessor.terms

    def score_document(self,query,doc_nos):
        """Calculates the BM25 score of a batch of documents given a query.
        Parameters
        ----------
        query: List[String]
            List of terms after preprocessing is applied to a users query
        doc_nos: List[int]
            List of document IDs to calculate the score for.
        Returns
        ----------
        results: List[(int,float)]
            List of document ID and score pairs which indicate the relevancy of a
            document to the query. 

        """
        k = 1.5
        # TODO: k is a hyperparameter which can be tuned later on. Currently using best
        # practise value given from the lectures.
        results = []
        for doc_no in doc_nos:
            doc_score = 0
            for term in query:
                tf = self.index.tf(term,doc_no)
                df = self.index.df(term)
                L_d = get_Document_Lengths([doc_no],self.index)
                avg_L = self.average_Doc_Len
                N = self.index.documentCount
                term_1 = tf/(k*(L_d/avg_L) + tf + 0.5)
                term_2 = np.log10((N-df+0.5)/(df+0.5))
                doc_score += term_1 * term_2
            results += [[doc_no,doc_score]]
        return results

    def ranked_search(self,query):
        """Ranks documents in the index given a query from the user.
        Parameters
        ----------
        query: String
            The query string submitted by the user.
        Returns
        ----------
        ranked_docs: List[(int,float)]
            A list of all document ID and score pairs that indicate the relevancy
            of a document to a user query. 
        """
        query_terms = self.preprocess_query(query)
        doc_IDs = []
        for term in query_terms:
            doc_list = self.index.terms.get(term,None)
            if doc_list:
                doc_IDs += list(doc_list.keys())
        doc_IDs = list(set(doc_IDs))
        no_of_processes = (cpu_count()//4)

        # Using multiprocessing to rank documents in parallel
        doc_partitions = partition_data(doc_IDs,no_of_processes)
        pool = Pool(processes=no_of_processes)
        results = [pool.apply_async(self.score_document,(query_terms,doc_IDs,)) for doc_IDs in doc_partitions]
        results = [score.get() for score in results]
        ranked_docs = sum(results,[])
        pool.terminate()
        return ranked_docs