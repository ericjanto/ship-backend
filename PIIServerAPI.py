import socket
import sys
import threading
import json
from threading import Lock

from PositionalInvertedIndexLoader import PositionalInvertedIndexLoader

class PIIServerAPI:

    def __init__(self, index, ip, port):
        self.index = index
        self.serverSocket = None
        self.initialiseSocket(ip, port)
        self.clientId = 0
        t = threading.Thread(target=self.listen)
        t.start()
        t.join()
    
    def process_request(self, client_socket):
        while True:
            message = client_socket.recv(4096).decode()
            response = self.process_query(message)
            print("Sending response: " + str(response))
            client_socket.sendall(json.dumps(response).encode())
            if "endServerConnection" in response and response["endServerConnection"] == True: break
        print("Closing connection")
        client_socket.close()

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
            return data

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

        elif method == "getDocIDs":
            data["docIDs"] = self.index.getDocIDs()

        elif method == "endServerConnection":
            data["endServerConnection"] = True

        else:
            print("Error: invalid method")
            # We need to return something if an invalid request is
            # sent, else the client will never stop waiting for a response.
            data["invalidQueryType"] = True
        data["requestID"] = json_recv["requestID"]
        data["clientID"] = json_recv["clientID"]

        return data

    def initialiseSocket(self, ipAddr, socketNo):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((ipAddr, socketNo))
        self.serverSocket.listen()

    def listen(self):
        while True:
            try:
                client_socket, client_address = self.serverSocket.accept()
                print(f'Accepted connection from {client_address}')
                t = threading.Thread(target=self.process_request, args=(client_socket,))
                t.start()
                t.join()
            except KeyboardInterrupt:
                print("Server shutting down...")
                self.serverSocket.close()
                sys.exit(0)

""" Main method to run the server """
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 PIIServerAPI.py <ip> <port> <index file>")
        sys.exit(1)

    ip = sys.argv[1]
    # if ip == 'localhost':
    #     ip = '127.0.0.1'
    print(ip)
    port = int(sys.argv[2])
    print(port)
    indexFile = sys.argv[3]
    print(indexFile)

    index = PositionalInvertedIndexLoader.loadFromCompressedFile(indexFile)
    print("Index loaded")
    server = PIIServerAPI(index, ip, port)

    print("Server running on {}:{}".format(ip, port))

    