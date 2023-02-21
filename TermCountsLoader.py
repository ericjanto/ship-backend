class TermCountsLoader:
    def __init__(self):
        pass

    @staticmethod
    def loadFromFile(path, termCounts):
        with open(path, 'rb') as f:
            return pickle.load(f)