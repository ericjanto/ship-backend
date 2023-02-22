from collections import OrderedDict 

# A simple cache for queries
class QueryCache():
    def __init__(self,cache_size):
        self.size = cache_size
        self.cache = OrderedDict()

    def get(self, query):
        results = self.cache.pop(query)
        self.cache[query] = results
        return results
    
    def push(self, query, results):
        if len(self.cache) >= self.size:
            self.cache.popitem(last=False)
        self.cache[query] = results