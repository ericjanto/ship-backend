import socket
import json
from threading import Thread, Lock
from typing import List, Set
import sys

class PIIClientAPI:
    def __init__(self, HOST, PORT):
        """ Creates a tcp socket and connects to the server """
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((HOST, PORT))
        self.requestID = 0
        self.threadDict = dict()
        self.lock = Lock()
        self.responseDict = dict()
        self.clientID = self.requestClientId() # Not put through a request handler as it needs to complete before any other requests can be made

    def requestHandler(self, function, **args):
        """
        Starts a thread for the assoicated target function,
        then puts the thread to sleep until listen recieves a response for the request
        then then the output is returned """
        self.requestID = (self.requestID + 1) % 1000000 
        self.threadDict[self.requestID] = Thread(target=function, args=args.values())
        self.threadDict[self.requestID].start()


    def joinThreadDict(self):
        for thread in self.threadDict.values():
            thread.join()
        print(self.responseDict)

    def responseHandler(self, response):
        """ Handles the response from the server """
        json_recv = json.loads(response)
        requestID = json_recv["requestID"]
        clientID = json_recv["clientID"]
        if requestID == 1:
            return clientID
        self.clientID = clientID
        if requestID in self.threadDict and json_recv["clientID"] == self.clientID and "response" in json_recv:
            with self.lock:
                self.responseDict[requestID] = json_recv["response"]
        else:
            raise Exception("Invalid requestID received from server")

    
    def send_and_recv(self, message):
        self.clientSocket.sendall(json.dumps(message).encode())
        response = self.clientSocket.recv(4096).decode()
        return self.responseHandler(response)

    def generateRequest(self, method, terms=[], docIDs=[], pairs=[]):
        if type(terms) is str:
            terms = [terms]
        if type(docIDs) is int:
            docIDs = [docIDs]
        if type(pairs) is tuple:
            pairs = []

        request = {
            "clientID": self.clientID,
            "requestID": self.requestID,
            "method" : method,
            "terms" : terms,
            "docIDs" : docIDs,
            "pairs" : pairs
        }

        return request
    
    def requestClientId(self):
        """ Method that requests a client id from the server """
        self.requestID = (self.requestID + 1) % 1000000
        message = {"method": "requestClientId", "requestID": self.requestID}
        return self.send_and_recv(message)

    
    def getDistinctTermsCount(self):
        message = self.generateRequest("getDistinctTermsCount")
        self.send_and_recv(message)
        
    
    # NB: not super accurate, because some languages have words which consist of ascii characters only (e.g. "amore" in Italian)
    def getEnglishTermsCount(self):
        message = self.generateRequest("getEnglishTermsCount")
        self.send_and_recv(message)


    def getTermFrequency(self, terms, docIDs) -> int:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("getTermFrequency",
                                       pairs=list(zip(terms, docIDs)))
        self.send_and_recv(message)


    def getDocFrequency(self, terms) -> dict:
        if type(terms) == str:
            terms = [terms]
        print(terms)
        message = self.generateRequest("getDocFrequency", terms=terms)
        self.send_and_recv(message)
        
    def getDocumentsTermOccursIn(self, terms) -> dict:
        if type(terms) == str:
            terms = [terms]
        message = self.generateRequest("getDocumentsTermOccursIn", terms=terms)
        self.send_and_recv(message)

    def getPostingList(self, terms, docIDs) -> dict:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("getPostingList",
                                       pairs=list(zip(terms, docIDs)))
        self.send_and_recv(message)


    def tfidf(self, terms, docIDs) -> dict:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("tfidf",
                                       pairs=list(zip(terms, docIDs)))
        self.send_and_recv(message)

    def getNumDocs(self) -> dict:
        message = self.generateRequest("getNumDocs")
        self.send_and_recv(message)
        
        

    def getDocIDs(self) -> dict:
        message = self.generateRequest("getDocIDs")
        self.send_and_recv(message)
        

    def endServerConnection(self):
        message = self.generateRequest("endServerConnection")
        self.send_and_recv(message)


### main method to open a client requeusting the server for docIDs
if __name__ == "__main__":
    HOST = "localhost"
    PORT = 5000
    client = PIIClientAPI(HOST, PORT)
    client.requestHandler(client.getDistinctTermsCount)
    client.requestHandler(client.getEnglishTermsCount)
    client.requestHandler(client.getDocFrequency, terms=["appl", "mang", "dov"])
    client.requestHandler(client.endServerConnection)
    client.joinThreadDict()

        