class TermCountsIndex:
    def __init__(self, index):
        self.index = index
    
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
    
    def get_all_term_counts(self, docID):
        if type(docID) == str:
            docID = int(docID)
        if docID not in self.index:
            return []
        return self.index[docID]