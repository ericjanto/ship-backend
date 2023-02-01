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
    return bytearray(term, encoding="utf-8")


def indexToVBytes(pii):
    vBytes = []

    # Add the number of terms in the index
    vBytes += intToVByte(len(pii.terms))

    for term in pii.terms:
        # Convert the term into regular bytes
        bTerm = strToBytes(term)
        # Get the length of the byte representation
        bTermLen = len(bTerm)
        # Convert that length into a vByte
        bTermLenVByte = intToVByte(bTermLen)

        # Write both the length of the term, and the term
        # to the vByte encoding of the index
        vBytes += bTermLenVByte
        vBytes += bTerm

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

        # Convert the tag into regular bytes
        bTag = strToBytes(tag)
        # Get the length of the byte representation
        bTagLen = len(bTag)
        # Convert that length into a vByte

        bTagLenVByte = intToVByte(bTagLen)

        vBytes += bTagLenVByte
        vBytes += bTag

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


if __name__ == "__main__":
    print(intToVByte(150))
    print(vByteArrayToInts(intToVByte(150)))


    for i in range(1000000):
        if i != vByteArrayToInts(intToVByte(i))[0]:
            print(f"ERROR: {i}")
