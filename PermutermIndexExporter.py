import pickle
import pandas as pd
import bz2
import WildcardSearch

class PermutermIndexExporter:

    def __init__(self):
        pass
    
    @staticmethod
    def buildIndex(doc_terms_path):
        terms = pd.read_pickle(doc_terms_path)
        return WildcardSearch.create_permuterm_index_trie(terms)

    @staticmethod
    def saveToFile(path, permutermIndex):
        ofile = bz2.BZ2File(path,'wb')
        pickle.dump(permutermIndex, ofile)
        ofile.close()

if __name__=='__main__':
    exporter = PermutermIndexExporter()
    permutermIndex = exporter.buildIndex("./data/doc-terms.pickle")
    exporter.saveToFile("data/permuterm-index.bz2", permutermIndex)