from typing import List, Dict

from StoryMetadataRecord import StoryMetadataRecord

def intToVByte(x):
    if x == 0:
        return bytearray([128])
    vBytes = []
    while x > 0:
        vBytes.append(x % 128)
        x = x >> 7
    vBytes[0] += 128

    return bytearray(vBytes[::-1])

def vByteArrayToInts(vBytes):
    ints = [0]
    for vb in vBytes:
        val = int(vb)
        ints[-1] += val % 128
        if val >= 128:
            ints.append(0)
        else:
            ints[-1] = ints[-1] << 7
    return ints[:-1]

def strToBytes(term):
    if term is None:
        term = ""
    return bytearray(term, encoding="utf-8")


def convertStrToLengthPlusVByteEncoding(s: str) -> List[int]:
    bStr = strToBytes(s)
    bStrLength = len(bStr)
    bStrLengthVBytes = intToVByte(bStrLength)

    finalRepresentation = bStrLengthVBytes + bStr

    return finalRepresentation

def indexToVBytes(pii):
    vBytes = []

    # Add the number of terms in the index
    vBytes += intToVByte(len(pii.terms))

    for term in pii.terms:
        # Add the term to the byte representation
        vBytes += convertStrToLengthPlusVByteEncoding(term)

        # Write the number of documents that this term occurs
        # in to the vByte encoding
        vBytes += intToVByte(len(pii.terms[term]))

        for docID in pii.terms[term]:
            # Write the docID to the vByte encoding
            vBytes += intToVByte(docID)

            # Note and write how many positions that
            # this term occurs in this document, then write
            # it to vByte encoding
            positions = pii.terms[term][docID]

            vBytes += intToVByte(len(positions))

            # When writing positions to encoding, only save the
            # delta from the previous position
            lastPosition = 0

            for position in positions:
                deltaPosition = position - lastPosition

                vBytes += intToVByte(deltaPosition)

                lastPosition = position

    return vBytes

# TODO: Refactor this file as a whole


def tagIndexToVBytes(tpii):

    vBytes = []

    # Add the number of tags in the index
    vBytes += intToVByte(len(tpii.tags))

    for tag in tpii.tags:

        # Add the tag into the byte representation
        vBytes += convertStrToLengthPlusVByteEncoding(tag)

        # Write the posting list for the term to the
        # vByte representation

        storyIDs = tpii.tags[tag]

        storyIDCount = len(storyIDs)

        vBytes += intToVByte(storyIDCount)

        lastStoryID = 0

        for storyID in storyIDs:

            deltaID = storyID - lastStoryID

            vBytes += intToVByte(deltaID)

            lastStoryID = storyID

    return vBytes

def metadataIndexToVBytes(metadataIndex: Dict[int, StoryMetadataRecord]) -> List[int]:
    vBytes = []

    vBytes += intToVByte(len(metadataIndex))

    for story in metadataIndex:
        vBytes += StoryMetadataRecordToVBytes(metadataIndex[story])

    return vBytes

def StoryMetadataRecordToVBytes(metadataRecord: StoryMetadataRecord) -> List[int]:
    vBytes = []

    vBytes += intToVByte(metadataRecord.storyID)

    vBytes += convertStrToLengthPlusVByteEncoding(metadataRecord.title)

    vBytes += convertStrToLengthPlusVByteEncoding(metadataRecord.author)

    # Write the compressed description, which is already in bytes
    vBytes += intToVByte(len(metadataRecord._compressedDescription))
    vBytes += bytearray(metadataRecord._compressedDescription)

    # To save a single byte, will write the two boolean flagged fields together
    flagState = 0
    if metadataRecord.finished:
        flagState += 1
    if metadataRecord.finalChapterCountKnown:
        flagState += 2
    vBytes += intToVByte(flagState)

    vBytes += intToVByte(metadataRecord.currentChapterCount)

    if metadataRecord.finalChapterCountKnown:
        vBytes += intToVByte(metadataRecord.finalChapterCount)

    vBytes += intToVByte(metadataRecord.language)

    vBytes += intToVByte(metadataRecord.wordCount)
    vBytes += intToVByte(metadataRecord.commentCount)
    vBytes += intToVByte(metadataRecord.bookmarkCount)
    vBytes += intToVByte(metadataRecord.kudosCount)
    vBytes += intToVByte(metadataRecord.hitCount)

    vBytes += convertStrToLengthPlusVByteEncoding(metadataRecord.lastUpdated)

    return vBytes

if __name__ == "__main__":
    print(intToVByte(150))
    print(vByteArrayToInts(intToVByte(150)))


    for i in range(1000000):
        if i != vByteArrayToInts(intToVByte(i))[0]:
            print(f"ERROR: {i}")
