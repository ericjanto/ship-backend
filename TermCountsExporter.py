import pickle

class TermCountsExporter:
    def __init__(self):
        pass

    @staticmethod
    def saveToFile(path, termCounts):
        with open(path, 'wb') as f:
            pickle.dump(termCounts, f)