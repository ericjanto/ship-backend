from PositionalInvertedIndex import PositionalInvertedIndex

from indexCompressor import indexToVBytes

class PositionalInvertedExporter():

    def __init__(self, ):
        pass


    @staticmethod
    def saveToTxtFile(index, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for term, occurrences in sorted(index.terms.items()):
                f.write(f"{term}:{len(occurrences)}\n")
                for docID, positions in sorted(occurrences.items()):
                    f.write(f"\t{docID}: ")
                    for i, position in enumerate(positions):
                        f.write(f"{position}")
                        if i != len(positions) - 1:
                            f.write(",")
                    f.write("\n")
                # https://piazza.com/class/l7ze53oc13q32o/post/80_f1 
                # confirms that a blank line between separate terms 
                # is valid formatting for the index file
                f.write("\n")


    @staticmethod
    def saveToCompressedIndex(index, filename):
        compressedIndex = indexToVBytes(index)
        with open(filename, "wb") as f:
            f.write(bytes(compressedIndex))

if __name__=='__main__':
    pii = PositionalInvertedIndex.readFromBinary("index.bin")
    print(pii.documentIDs)
    piexporter = PositionalInvertedExporter()
    piexporter.saveToCompressedIndex(pii, "index-vbytes.bin")