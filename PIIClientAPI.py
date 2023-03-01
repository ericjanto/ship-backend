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
        self.threadDict = {}
        self.clientID = self.requestHandler(self.requestClientId)
        #t = Thread(target=self.listen)
        #t.start()
        #t.join()

    def requestHandler(self, function, **args):
        """
        Starts a thread for the assoicated target function,
        then puts the thread to sleep until listen recieves a response for the request
        then then the output is returned """
        self.threadDict[self.requestID] = Thread(target=function, args=args)
        self.threadDict[self.requestID].start()

    def joinThreadDict(self):
        for thread in self.threadDict.values():
            thread.join()
    
    
    # def listen(self):
    #     # self.socket.listen()
        
    #     while True:
    #         try:
    #             response = self.clientSocket.recv(4096).decode()
    #             if response!="":
    #                 t = Thread(target=self.handleResponse, args=(response,))
    #                 t.start()
    #                 # t.join()
    #         except Exception as e:
    #             print(e)
    #             print("Client shutting down...")
    #             self.clientSocket.close()
    #             break

    # def handleResponse(self, response):
    #     if response!="":
    #         response = json.loads(response)
    #     print(response)
    #     return response
    
    def send_and_recv(self, message):
        self.requestID = (self.requestID + 1) % 1000000 
        self.clientSocket.sendall(json.dumps(message).encode())
        response = self.clientSocket.recv(4096).decode()
        print(json.loads(response))

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

        self.requestID += 1

        return request
    
    def requestClientId(self):
        """ Method that requests a client id from the server """
        message = {"method": "requestClientId", "requestID": self.requestID}
        self.send_and_recv(message)

    
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


    def getDocFrequency(self, terms) -> int:
        if type(terms) == str:
            terms = [terms]
        message = self.generateRequest("getDocFrequency", terms=terms)
        self.send_and_recv(message)
        
    def getDocumentsTermOccursIn(self, terms) -> List[int]:
        if type(terms) == str:
            terms = [terms]
        message = self.generateRequest("getDocumentsTermOccursIn", terms=terms)
        self.send_and_recv(message)

    def getPostingList(self, terms, docIDs) -> List[int]:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("getPostingList",
                                       pairs=list(zip(terms, docIDs)))
        self.send_and_recv(message)


    def tfidf(self, terms, docIDs) -> float:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("tfidf",
                                       pairs=list(zip(terms, docIDs)))
        self.send_and_recv(message)

    def getNumDocs(self) -> int:
        message = self.generateRequest("getNumDocs")
        self.send_and_recv(message)
        

    def getDocIDs(self) -> Set[int]:
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
    client.requestHandler(client.endServerConnection)
    client.joinThreadDict()

        