import os

from PositionalInvertedIndex import PositionalInvertedIndex


class PositionalInvertedIndexLoader():

    def __init__(self):
        pass

    @staticmethod
    def loadFromFile(filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist")
        index = PositionalInvertedIndex()

        with open(filename, "r", encoding="utf-8") as f:
            content = f.readlines()
            currentTerm = None
            for line in content:
                if line == "\n":
                    continue
                isNewTerm = not line.startswith("\t")
                splitLine = line.strip().split(":")
                if len(splitLine) != 2:
                    raise RuntimeError("Malformed index file")
                if isNewTerm:
                    currentTerm = splitLine[0]
                else:
                    docID = int(splitLine[0])
                    occurences = [int(x.strip()) for x in splitLine[1].split(",")]
                    for position in occurences:
                        index.insertTermInstance(currentTerm, docID, position)
        return index






if __name__ == "__main__":
    readInIndex = PositionalInvertedIndexLoader.loadFromFile("indexes/index.trec.sample.txt")
    readInIndex.writeToTxtFile("indexes/index.loaderTest.trec.sample.txt")
