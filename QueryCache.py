from collections import OrderedDict 

# A simple cache for queries
class QueryCache():
    def __init__(self,cache_size):
        self.size = cache_size
        self.cache = OrderedDict()

    def get(self, query):
        try:
            results = self.cache.pop(query)
            self.cache[query] = results
            return results
        except:
            return []
    
    def push(self, query, results):
        try:
            self.cache.pop(query)
        except:
            if len(self.cache) >= self.size:
                self.cache.popitem(last=False)
        self.cache[query] = results
    
    def exists(self, query):
        if self.cache.get(query):
            return True
        else:
            return False