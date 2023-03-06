from flask import Flask, request
from PositionalInvertedIndexLoader import PositionalInvertedIndexLoader
import json
import sys

class PIIServerFlask:
    def __init__(self, index, ip, port):
        self.index = index
        self.ip = ip
        self.port = port
        self.app = Flask(__name__)
        self.app.add_url_rule('/', view_func=self.test, methods=['GET', 'POST'])
        self.app.add_url_rule('/getDistinctTermsCount', view_func=self.getDistinctTermsCount, methods=['GET'])
        self.app.add_url_rule('/getEnglishTermsCount', view_func=self.getEnglishTermsCount, methods=['GET'])
        self.app.add_url_rule('/getTermFrequency', view_func=self.getTermFrequency, methods=['POST'])
        self.app.add_url_rule('/getDocFrequency', view_func=self.getDocFrequency, methods=['POST'])
        self.app.add_url_rule('/getDocumentsTermOccursIn', view_func=self.getDocumentsTermOccursIn, methods=['POST'])
        self.app.add_url_rule('/getPostingList', view_func=self.getPostingList, methods=['POST'])
        self.app.add_url_rule('/tfidf', view_func=self.tfidf, methods=['POST'])
        self.app.add_url_rule('/getNumDocs', view_func=self.getNumDocs, methods=['GET'])
        self.app.add_url_rule('/getDocIDs', view_func=self.getDocIDs, methods=['GET'])


    def test(self):
        if request.method == 'GET':
            return 'This is a GET request'
        elif request.method == 'POST':
            data = request.json
            return f'This is a POST request with data: {data}'
    
    def getDistinctTermsCount(self):
        return json.dumps(self.index.getDistinctTermsCount()).encode('utf-8')
    
    def getEnglishTermsCount(self):
        return json.dumps(self.index.getEnglishTermsCount()).encode('utf-8')
    
    def getTermFrequency(self):
        pairs = request.json["pairs"]
        response = {}
        for term, docID in pairs:
            if term not in response:
                response[term] = dict()
            response[term][docID] = self.index.getTermFrequency(term, docID)
        return json.dumps(response).encode('utf-8')
    
    def getDocFrequency(self):
        terms = request.json["terms"]
        response = {}
        for term in terms:
            response[term] = self.index.getDocFrequency(term)
        return json.dumps(response).encode('utf-8')
    
    def getDocumentsTermOccursIn(self):
        terms = request.json["terms"]
        response = {}
        for term in terms:
            response[term] = self.index.getDocumentsTermOccursIn(term)
        return json.dumps(response).encode('utf-8')
    
    def getPostingList(self):
        pairs = request.json["pairs"]
        response = {}
        for term, docID in pairs:
            if term not in response:
                response[term] = dict()
            response[term][docID] = self.index.getPostingList(term, docID)
        return json.dumps(response).encode('utf-8')
    
    def tfidf(self):
        pairs = request.json["pairs"]
        response = {}
        for term, docID in pairs:
            if term not in response:
                response[term] = dict()
            response[term][docID] = self.index.tfidf(term, docID)
        return json.dumps(response).encode('utf-8')
    
    def getNumDocs(self):
        return json.dumps(self.index.getNumDocs()).encode('utf-8')
    
    def getDocIDs(self):
        list_of_docIDs = list(self.index.getDocIDs()) # Since set is not serializable
        return json.dumps(list_of_docIDs).encode('utf-8')

    def run(self):
        self.app.run(host=self.ip, port=self.port, threaded=True)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 PIIServerAPI.py <ip> <port> <index file>")
        sys.exit(1)

    ip = sys.argv[1]
    print("IP:", ip)
    port = int(sys.argv[2])
    print("Port:", port)
    indexFile = sys.argv[3]
    print("IndexFile:", indexFile)

    index = PositionalInvertedIndexLoader.loadFromCompressedFile(indexFile)
    print("Index loaded")
    
    server = PIIServerFlask(index, ip, port)
    server.run()