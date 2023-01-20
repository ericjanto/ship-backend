Expected Positional Index Structure:

- Document Count (Integer)

- HashMap {
    - Term 
    - HashMap {
        - Document ID
        - List {
            - Position
        }
    }
}


V-Byte Encoding format:

- Document Count (v-bytes)

- Term count (v-bytes)

- For term in Term count:

    - characters in term (v-bytes)

    - Term (regular bytes)
    
    - document frequency (v-bytes)

    For document in documents:

        - Doc ID (v-bytes, relative to previous doc ID)

        - number of occurences in document (v-bytes)

        for occurence in occurences:

            - term position (v-bytes)

Trade offs:

    If we want to store DocIDs as v-bytes relative to the previous docID, 
    then we need maintain a sorted list of document IDs for each term,
    or generate one when saving to file. This would be a considerable time
    vs space trade off.