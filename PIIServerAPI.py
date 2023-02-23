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

    def process_request(self, message, addr):

        response = self.process_query(message)

        self.recvSocket.sendto(json.dumps(response).encode(), addr)

    def process_query(self, message):
        """
        Takes the JSON request received from the client,
        runs the requested operation against the index, and wraps
        the result in another JSON object.
        """
        json_recv = json.loads(message)
        method = json_recv["method"]
        data = {}

        if method == "requestClientId":
            data["clientId"] = self.clientId
            self.clientId += 1

        elif method == "getDistinctTermsCount":
            data["distinctTermCount"] = self.index.getDistinctTermsCount()

        elif method == "getEnglishTermsCount":
            data["englishTermCount"] = self.index.getEnglishTermsCount()

        elif method == "getTermFrequency":
            pairs = json_recv["pairs"]
            for term, docID in pairs:
                data[(term, docID)] = self.index.getTermFrequency(term, docID)

        elif method == "getDocFrequency":
            terms = json_recv["terms"]
            for term in terms:
                data[term] = self.index.getDocFrequency(term)

        elif method == "getDocumentsTermOccursIn":
            terms = json_recv["terms"]
            for term in terms:
                data[term] = self.index.getDocumentsTermOccursIn(term)

        elif method == "getPostingList":
            pairs = json_recv["pairs"]
            for (term, docID) in pairs:
                data[(term, docID)] = self.index.getPostingList(term, docID)

        else:
            print("Error: invalid method")
            # We need to return something if an invalid request is
            # sent, else the client will never stop waiting for a response.
            data["invalidQueryType"] = True
        data["requestID"] = json_recv["requestID"]
        data["clientID"] = json_recv["clientID"]

        return data

    def initialiseSocket(self, ipAddr, socketNo):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvSocket.bind((ipAddr, socketNo))

    def listen(self):
        self.recvSocket.listen(5)
        while True:
            message, addr = client.recv(4096)
            threading.Thread(target=process_request, args=(message, addr)).start()
