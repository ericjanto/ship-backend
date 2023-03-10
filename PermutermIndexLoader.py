import bz2 
import pickle 


class PermutermIndexLoader:
    def __init__(self):
        pass

    @staticmethod
    def loadFromCompressedFile(path):
        ifile = bz2.BZ2File(path,'rb')
        permutermIndex = pickle.load(ifile)
        ifile.close()
        
        return permutermIndex