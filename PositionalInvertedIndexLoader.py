import os
import pandas as pd
from PositionalInvertedIndex import PositionalInvertedIndex
from indexDecompressor import IndexDecompressor
from PositionalInvertedIndexExporter import PositionalInvertedExporter
import WildcardSearch

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

    @staticmethod
    def loadFromCompressedFile(filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"{filename} does not exist")
        with open (filename, "rb") as f:
            compressedIndex = f.read()

        decompressor = IndexDecompressor(compressedIndex)

        return decompressor.toIndex()


    @staticmethod
    def loadFromMultipleCompressedFiles(pathToFiles: str, verbose: bool = False) -> PositionalInvertedIndex:
        # Assumes that every file in the specified directory is a compressed index
        if not os.path.exists(pathToFiles):
            raise FileNotFoundError(f"{pathToFiles} does not exist")

        index = PositionalInvertedIndex()

        indexFiles = [f for f in os.listdir(pathToFiles) if os.path.isfile(os.path.join(pathToFiles, f))]

        indexFiles.sort()

        for i, file in enumerate(indexFiles):
            pathToFile = os.path.join(pathToFiles, file)
            indexChunk = PositionalInvertedIndexLoader.loadFromCompressedFile(pathToFile)
            
            index.mergeWithOtherIndex(indexChunk)

            if verbose:
                print(f"Loaded and merged {i + 1} of {len(indexFiles)} index chunks")

        return index


if __name__ == "__main__":
    readInIndex = PositionalInvertedIndexLoader.loadFromCompressedFile("./data/chapters-index-vbytes.bin")
    PositionalInvertedExporter.saveToTxtFile(readInIndex, "./data/chapters-index.txt")

    terms = pd.read_pickle("./data/doc-terms.pickle")
    permutermIndexTrie = WildcardSearch.create_permuterm_index_trie(terms)
    