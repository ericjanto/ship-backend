import pickle
from TermCountsIndex import TermCountsIndex
class TermCountsLoader:
    def __init__(self):
        pass

    @staticmethod
    def loadFromFile(path):
        with open(path, 'rb') as f:
            return TermCountsIndex(pickle.load(f))