import pickle
import pandas as pd
import bz2
import WildcardSearch

class PermutermIndexExporter:

    def __init__(self):
        pass
    
    @staticmethod
    def buildIndex():
        terms = pd.read_pickle("./data/doc-terms.pickle")
        return WildcardSearch.create_permuterm_index_trie(terms)

    @staticmethod
    def saveToFile(path, permutermIndex):
        ofile = bz2.BZ2File(path,'wb')
        pickle.dump(permutermIndex, ofile)
        ofile.close()

if __name__=='__main__':
    exporter = PermutermIndexExporter()
    permutermIndex = exporter.buildIndex()
    exporter.saveToFile("data/permuterm-index.bz2", permutermIndex)