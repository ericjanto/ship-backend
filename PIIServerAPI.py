import socket
import sys
import threading

from PositionalInvertedIndex import PositionalInvertedIndex

class PIIServerAPI:

    def __init__(self, index, ip, port):
        self.index = index

        self.recvSocket = None

        self.initialiseSocket(ip, socket)
        self.clientId = 0
        self.listen()
    
    def process_query(self, message, addr):
        """ Process a query from a client, where message is of types bytes and needs to be converted to a json object """
        json_recv = json.loads(message)
        method = json_recv["method"]
        data = {}
        if method=="requestClientId":
            data["clientId"] = self.clientId
            self.clientId += 1

        elif method == "getDistinctTermsCount":
            data[method] = self.index.getDistinctTermsCount()

        elif method == "getEnglishTermsCount":
            data[method] = self.index.getEnglishTermsCount()

        elif method == "getTermFrequency":
            pairs = json_recv["pairs"]
            for term, docID in pairs:
                data[(method, term, docID)] = self.index.getTermFrequency(term, docID)

        elif method == "getDocFrequency":
            terms = json_recv["terms"]
            for term in terms:
                data[(method, term)] = self.index.getDocFrequency(term)

        elif method == "getDocumentsTermOccursIn":
            terms = json_recv["terms"]
            for term in terms:
                data[(method,term)] = self.index.getDocumentsTermOccursIn(term)

        elif method == "getPostingList":
            pairs = json_recv["pairs"]
            for (term, docID) in pairs:
                data[(method, term, docID)] = self.index.getPostingList(term, docID)

        else:
            print("Error: invalid method")
            data = None
        response = {"request_id": request_id, "client_id":client_id, "data": data}
        self.recvSocket.sendto(json.dumps(response).encode(), addr)

    def initialiseSocket(self, ipAddr, socketNo):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvSocket.bind((ipAddr, socketNo))

    def listen(self):
        self.recvSocket.listen(5)
        while True:
            message, addr = client.recv(4096)
            threading.Thread(target=process_query, args=(message, addr)).start()
