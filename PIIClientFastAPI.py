import requests
import json

### Convert above to a class and add more methods
class PIIClientFlask:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def getDistinctTermsCount(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getDistinctTermsCount')
        return response.json()
        
    def getEnglishTermsCount(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getEnglishTermsCount')
        return response.json()

    def getTermFrequency(self, pairs):
        data = {'pairs': pairs}
        response = requests.post(f'http://{self.ip}:{self.port}/getTermFrequency', json=data)
        return response.json()

    def getDocFrequency(self, term):
        data = {'terms': term}
        response = requests.post(f'http://{self.ip}:{self.port}/getDocFrequency', json=data)
        return response.json()

    def getDocumentsTermOccursIn(self, terms):
        data = {'terms': terms}
        response = requests.post(f'http://{self.ip}:{self.port}/getDocumentsTermOccursIn', json=data)
        return response.json()

    def getPostingList(self, pairs):
        data = {'pairs': pairs}
        response = requests.post(f'http://{self.ip}:{self.port}/getPostingList', json=data)
        return response.json()

    def tfidf(self, pairs):
        data = {'pairs': pairs}
        response = requests.post(f'http://{self.ip}:{self.port}/tfidf', json=data)
        return response.json()

    def getNumDocs(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getNumDocs')
        return response.json()

    def getDocIDs(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getDocIDs')
        return response.json()
    
    def mergeWithOtherIndexAllDates(self):
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndexAllDates')
        return response.json()
    
    def mergeWithOtherIndex(self, dateFileNames):
        data = {'dateFileNames': dateFileNames}
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndex', json=data)
        return response.json()

if __name__ == '__main__':
    client = PIIClientFlask('localhost', 5001)
    client2 = PIIClientFlask('localhost', 5001)
    print("1.", client.getDistinctTermsCount())
    print("2.", client2.getEnglishTermsCount())
    print("3.",client.getTermFrequency([('appl', 247000), ('banan', 247000)]))
    print("4.",client2.getDocFrequency(['appl']))
    print("5.",client.getDocumentsTermOccursIn(['appl']))
    print("6.",client2.getPostingList([('appl', 247000), ('banan', 247000)]))
    print("7.",client.tfidf([('appl', 247000), ('appl', 247000)]))
    print("8.",client2.getNumDocs())
    # print("9.", client.mergeWithOtherIndex(['compressed-chapter-indexes/chapterIndex-part-1.bin']))
    print("10.", client.mergeWithOtherIndexAllDates())
    print("8.",client.getNumDocs())
    # print("9.",client.getDocIDs())
   