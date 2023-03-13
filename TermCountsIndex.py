class TermCountsIndex:
    def __init__(self, index):
        self.index = index

    def appendIntoTermCounts(self, termCounts:dict):
        for docID, termCount in termCounts.items():
            if docID in self.index:
                self.index[docID] = [x + y for x, y in zip(self.index[docID], termCount)]
            else:
                self.index[docID] = termCount
    
    def get_tokens_before_processing(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID][0]
    
    def get_tokens_before_stemming(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID][1]
    
    def get_unique_tokens_before_processing(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID][2]
    
    def get_unique_tokens_before_stemming(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID][3]
    
    def get_tokens_after_stemming(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID][4]
    
    def get_all_term_counts_for(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID]

    def get_all_term_counts(self):
        return self.index