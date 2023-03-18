import numpy as np
import pickle
from indexDecompressor import IndexDecompressor
from preprocessing import loadStopWordsIntoSet
from Preprocessor import Preprocessor

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
    def __init__(self,positionalInvertedIndex,stopwords,term_counts):
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
        self.term_counts = term_counts
        all_term_counts = self.term_counts.get_tokens_before_stemming(self.index.getDocIDs())
        
        total_term_counts = sum(all_term_counts.values())
        self.avg_doc_len = total_term_counts/len(all_term_counts)

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

    def score_documents(self,query,doc_nos):
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
        b = 0.75
        # TODO: k is a hyperparameter which can be tuned later on. Currently using best
        # practise value given from the lectures.
        results = []
        doc_nos = list(doc_nos)
        term_counts = self.term_counts.get_tokens_before_stemming(doc_nos)
        N = self.index.getNumDocs()
        tf_dict = self.index.getTermFrequency([(term,doc_no) for term in query for doc_no in doc_nos])
        df_dict = self.index.getDocFrequency(query)

        for doc_no in doc_nos:
            doc_score = 0
            for term in query:
                tf = tf_dict.get(term).get(doc_no,0)
                df = df_dict.get(term,0)
                L_d = term_counts.get(doc_no,0)
                avg_L = self.avg_doc_len
                C_td = (tf/(1-b + b*(L_d/avg_L))) #+ 0.5
                #term_1 = tf*(k+1)/((tf+k)*(1-0.75+0.75*(L_d/avg_L)))
                term_1 = ((k+1)*(C_td+0.5))/(k+C_td+0.5)
                term_2 = np.log10(((N+1)/(df+0.5)))
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
            doc_list = self.index.getDocumentsTermOccursIn(term)
            if doc_list:
                doc_IDs += list(doc_list.keys())
        doc_IDs = list(set(doc_IDs))

        ranked_docs = self.score_documents(query_terms,doc_IDs)
        return sorted(ranked_docs,key=lambda x: x[1],reverse=True)

# Example Usage of Bm25 
if __name__ == "__main__":
    with open('data/chapters-index-vbytes.bin','rb') as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()
    
    with open('data/term-counts.bin','rb') as f:
        data = f.read()
        term_counts = pickle.loads(data)
    
    stopwords = loadStopWordsIntoSet('englishStopWords.txt')

    model = BM25_Model(index,stopwords,term_counts)
    results = model.ranked_search('Knives by Kylielee1000')[:5]
    
    for docId,score in results:
        print(f"Document Number: {docId}\nScore: {score}")
