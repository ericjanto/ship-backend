from BooleanSearchEngine import BooleanSearchEngine
from preprocessing import loadStopWordsIntoSet
from bm25 import BM25_Model
from indexDecompressor import IndexDecompressor
import pickle

query_examples = ["Who what who were AND (what OR (where AND are you))",
                  "supernatural and doctor who superwholock",
                  "superwholock",
                  "bionicles",
                  "Bob Fraser in a zombie apocalypse",
                  "Doctor Who",
                  "Doctor Mallard"]

CONNECTIVES = ['AND','OR','and','or']

class Search_Engine():
    def __init__(self,positionalInvertedIndex,stopwords,termcounts):
        self.index = positionalInvertedIndex
        self.stopwords = stopwords
        self.termcounts = termcounts
        self.boolean_engine = BooleanSearchEngine(self.index,self.stopwords)
        self.ranker = BM25_Model(self.index,self.stopwords,self.termcounts)
    
    def search(self,query):
        query = query.replace('(',' ( ')
        query = query.replace(')',' ) ')
        query = query.replace('"',' " ')
        tokens = query.split()
        doc_IDs = self.recur_connectives(tokens)
        terms = self.ranker.preprocess_query(query)
        doc_score_pairs = self.ranker.score_documents(terms,doc_IDs)
        return sorted(doc_score_pairs,key=lambda x: x[1], reverse=True)

    def recur_connectives(self,subquery):
        split_query = list(self.bracketed_split(subquery,CONNECTIVES,strip_brackets=False))
        if 'AND' in split_query or 'and' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.intersection(token_2)
        elif 'OR' in split_query or 'or' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.union(token_2)
        else:
            or_str = []
            quotes = []
            curr_quote = []
            depth = 0
            for token in split_query[0]:
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
            if quotes:
                query_str = ' OR '.join([f"\"{' '.join(quote)}\"" for quote in quotes])
            else:
                query_str = ' OR '.join(or_str)
            results = set(self.boolean_engine.makeQuery(query_str,debugVerbose=True))
            return results

    def bracketed_split(self,string, delimiter, strip_brackets=False):
        openers = '('
        closers = ')'
        opener_to_closer = dict(zip(openers, closers))
        opening_bracket = dict()
        current_string = []
        depth = 0
        for c in string:
            if c in openers:
                depth += 1
                opening_bracket[depth] = c
                if strip_brackets and depth == 1:
                    continue
            elif c in closers:
                assert depth > 0, f"You exited more brackets that we have entered in string {string}"
                assert c == opener_to_closer[opening_bracket[depth]], f"Closing bracket {c} did not match opening bracket {opening_bracket[depth]} in string {string}"
                depth -= 1
                if strip_brackets and depth == 0:
                    continue
            if depth == 0 and (c in delimiter):
                yield current_string
                yield c
                current_string = []
            else:
                current_string += [c]
        assert depth == 0, f'You did not close all brackets in string {string}'
        yield current_string

if __name__ == "__main__":
    with open('data/chapters-index-vbytes.bin','rb') as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()
    
    print("Index built")
    with open('data/term-counts.bin','rb') as f:
        data = f.read()
        term_counts = pickle.loads(data)
    
    print("Term counts Loaded")
    stopwords = loadStopWordsIntoSet('englishStopWords.txt')
    print("Stopwords loaded")
    api = Search_Engine(index,stopwords,term_counts)
    print(api.search(query_examples[3]))