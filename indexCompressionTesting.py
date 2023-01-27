from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
from indexCompressor import indexToVBytes
from indexDecompressor import IndexDecompressor

from PositionalInvertedIndexLoader import PositionalInvertedIndexLoader


if __name__ == "__main__":

    # PATH_TO_XML_DOC_COLLECTION = "data/cw1/trec.5000.xml"

    # index = PositionalInvertedIndexFactory.generateIndexFromFile(PATH_TO_XML_DOC_COLLECTION)

    # compressed_index = indexToVBytes(index)

    # print(compressed_index[:10])

    # with open("index-compression_test.delta", "wb") as f:
    #     f.write(bytes(compressed_index))

    # read_in_index = []
    # with open("index-compression_test.delta", "rb") as f:
    #     read_in_index = bytes(f.read())
    #     # byte = f.read(1)
    #     # while byte:
    #     #     read_in_index.append(int(byte))
    #     #     byte = f.read(1)
    # firstTen = []
    # for b in read_in_index[:10]:
    #     firstTen.append(b)
    # print(firstTen)

    # decompressor = IndexDecompressor(read_in_index)
    # decompressedIndex = decompressor.toIndex()

    # print(index == decompressedIndex)

    # index2 = PositionalInvertedIndexLoader.loadFromCompressedFile("index-compression_test.delta")

    # print(index == index2 and index2 == decompressedIndex)

    with open("chapters-index-vbytes.bin", "rb") as f:
        compressed = f.read()

        secondDecompressor = IndexDecompressor(compressed)
        ao3index = secondDecompressor.toIndex()