import requests
import json
# Perform a GET request
response = requests.get('http://localhost:5000/test')
print(response.text)

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
        data = {'terms': [term]}
        response = requests.post(f'http://{self.ip}:{self.port}/getDocFrequency', json=data)
        return response.json()

    def getDocumentsTermOccursIn(self, term):
        data = {'terms': [term]}
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
        return response.json(), type(response.json())

    def getDocIDs(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getDocIDs')
        return set(response.json())

if __name__ == '__main__':
    client = PIIClientFlask('localhost', 5000)
    client2 = PIIClientFlask('localhost', 5000)
    print("1.", client.getDistinctTermsCount())
    print("2.", client2.getEnglishTermsCount())
    print("3.",client.getTermFrequency([('the', 1), ('the', 2)]))
    print("4.",client2.getDocFrequency('the'))
    print("5.",client.getDocumentsTermOccursIn('the'))
    print("6.",client2.getPostingList([('the', 1), ('the', 2)]))
    print("7.",client.tfidf([('the', 1), ('the', 2)]))
    print("8.",client2.getNumDocs())
    print("9.",client.getDocIDs())
   