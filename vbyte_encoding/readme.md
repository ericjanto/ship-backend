Expected Positional Index Structure:

- Document Count (Integer)

- Document IDs (Set)

- HashMap {
    - Term (String)
    - HashMap {
        - Document ID (String)
        - List {
            - Position (String)
        }
    }
}


V-Byte Encoding format:


- Term count (v-bytes)

- For term in Term count:

    - characters in term (v-bytes)

    - Term (regular bytes)
    
    - document frequency (v-bytes) (MUST BE AN INTEGER)

    For document in documents:

        - Doc ID (v-bytes)

        - number of occurences in document (v-bytes)

        for occurence in occurences:

            - term position (v-bytes, relative to last position)

Notes:

    Due to how positional inverted indexes will be read in, there is no reason
    to write the document count and set of document IDs to the file.


Trade offs:

    If we want to store DocIDs as v-bytes relative to the previous docID, 
    then we need maintain a sorted list of document IDs for each term,
    or generate one when saving to file. This would be a considerable time
    vs space trade off.