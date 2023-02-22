from BooleanSearchEngine import BooleanSearchEngine
from preprocessing import loadStopWordsIntoSet
from bm25 import BM25_Model
from indexDecompressor import IndexDecompressor
from WildcardSearch import create_permuterm_index_trie
from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader
import pickle
import numpy as np

query_examples = ["Who what who were AND (what OR (where AND are you))",
                  "supernatural and doctor who superwholock",
                  "superwholock",
                  "bionicles",
                  "Bob Fraser in a zombie apocalypse",
                  "Doctor Who",
                  "Doctor Mallard",
                  "mix of words with \"Tails * bench\"",
                  "\"Tails * bench\"",
                  "Other terms with Mon*",
                  "Mon*"]

CONNECTIVES = ['AND','OR','and','or']

class Search_Engine():
    def __init__(self,positionalInvertedIndex,permutermIndexTrie,tagIndex,stopwords,termcounts):
        self.index = positionalInvertedIndex
        self.stopwords = stopwords
        self.termcounts = termcounts
        self.permutermIndexTrie = permutermIndexTrie
        self.tagIndex = tagIndex
        self.boolean_engine = BooleanSearchEngine(self.index,self.permutermIndexTrie,self.stopwords)
        self.ranker = BM25_Model(self.index,self.stopwords,self.termcounts)
        total_term_counts = sum([term_counts[docID]['tok_bfr_stemming'] for docID in term_counts])
        self.avg_doc_len = total_term_counts/len(term_counts.keys())
    
    def search(self,query):
        query = query.replace('(',' ( ')
        query = query.replace(')',' ) ')
        query = query.replace('"',' " ')
        tokens = query.split()
        doc_IDs = self.recur_connectives(tokens)
        intra_wild_card_terms = [token for token in tokens if (('*' in token) and (len(token) > 1))]
        if len(intra_wild_card_terms) > 0:
            for wild_card_term in intra_wild_card_terms:
                tokens.remove(wild_card_term)
            expanded_terms = self.permutermIndexTrie.expand_wildcard_terms(intra_wild_card_terms)
            expanded_terms = [term[0] for term in expanded_terms]
            tokens += expanded_terms
        query = ' '.join(tokens)
        terms = self.ranker.preprocess_query(query)
        tag_docIDs = self.tag_search(terms)
        doc_IDs = doc_IDs.union(tag_docIDs)
        doc_score_pairs = dict.fromkeys(doc_IDs)
        

        query_scores = self.ranker.score_documents(terms,doc_IDs)
        tag_scores = self.score_tag_docs(terms,tag_docIDs)
        
        for docID,score in query_scores:
            doc_score_pairs[docID] += score
        
        for docID,score in tag_scores:
            doc_score_pairs[docID] += score
        
        return sorted(doc_score_pairs.items(),key=lambda x: x[1], reverse=True)

    def recur_connectives(self,subquery):
        split_query = self.bracketed_split(subquery,CONNECTIVES,strip_brackets=False)
        if 'AND' in split_query or 'and' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.intersection(token_2)
        elif 'OR' in split_query or 'or' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.union(token_2)
        else:
            quotes,or_str = self.quote_split(split_query[0])
            if quotes:
                query_str = ' OR '.join([f"\"{' '.join(quote)}\"" for quote in quotes])
            else:
                query_str = ' OR '.join(or_str)
            results = set(self.boolean_engine.makeQuery(query_str))
            return results
    
    def bracketed_split(self,string, delimiter, strip_brackets=False):
        openers = '('
        closers = ')'
        split_query = []
        current_string = []
        depth = 0
        for c in string:
            if c in openers:
                depth += 1
                if strip_brackets and depth == 1:
                    continue
            elif c in closers:
                depth -= 1
                if strip_brackets and depth == 0:
                    continue
            if depth == 0 and (c in delimiter):
                split_query += [current_string]
                split_query += [c]
                current_string = []
            else:
                current_string += [c]
        split_query += [current_string]
        return split_query

    def quote_split(self,string):
        or_str = []
        quotes = []
        curr_quote = []
        depth = 0
        for token in string:
            if token == '"' and depth == 0:
                depth += 1
                continue
            elif token == '"' and depth > 0:
                quotes += [curr_quote]
                curr_quote = []
                depth -= 1
                continue
            if depth > 0:
                curr_quote += [token]
            else:
                or_str += [token]
        return quotes,or_str

    def tag_search(self, tags):
        docIDs = set()
        for tag in tags:
            docIDs = docIDs.union(set(self.tagIndex.getStoryIDsWithTag(tag)))
        return docIDs

    def score_tag_docs(self, tags, docIDs):
        k = 1.5
        b = 0.75
        results = []
        for doc_ID in docIDs:
            doc_score = 0
            for token in tags:
                tf = 1
                df = self.tagIndex.getTagFrequency(token)
                L_d = self.termcounts[doc_ID]['tok_bfr_stemming']
                avg_L = self.avg_doc_len
                N = self.index.getNumDocs()
                C_td = (tf/(1-b + b*(L_d/avg_L))) + 0.5
                term_1 = ((k+1)*C_td)/(k+C_td)
                term_2 = np.log10(((N+1)/(df+0.5)))
                doc_score += term_1 * term_2
            results += [[doc_ID,doc_score]]
        return results

if __name__ == "__main__":
    with open('data/chapters-index-vbytes.bin','rb') as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()
    print("Index Loaded")

    tag_index = TagPositionalInvertedIndexLoader().loadFromCompressedFile('data/compressedPreprocessedTagIndex.bin')
    print("Tag Index Loaded")

    with open('data/term-counts.bin','rb') as f:
        data = f.read()
        term_counts = pickle.loads(data)
    print("Term counts Loaded")

    with open('data/doc-terms.pickle','rb') as f:
        data = f.read()
        doc_terms = pickle.loads(data)
    permuterm_index_trie = create_permuterm_index_trie(doc_terms)
    print("permuterm index tree constructed")

    stopwords = loadStopWordsIntoSet('englishStopWords.txt')
    print("Stopwords loaded")
    api = Search_Engine(index,permuterm_index_trie,tag_index,stopwords,term_counts)
    print(api.search(query_examples[9]))