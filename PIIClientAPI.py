import socket
import json

class PIIClientAPI:
    def __init__(self, HOST, PORT):
        """ Creates a tcp socket and connects to the server """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.requestID = 0
        self.clientID = self.requestClientId()
        self.threadDict = {}
        self.listen()

    def requestHandler(self, function, **args):
        """
        Starts a thread for the assoicated target function,
        then puts the thread to sleep until listen recieves a response for the request
        then then the output is returned """
        self.threadDict[self.requestID] = threading.Thread(target=function, args=args)
        self.threadDict[self.requestID].start()
    
    def listen(self):
        self.recvSocket.listen(5)
        while True:
            message, addr = client.recv(4096)
            threading.Thread(target=self.recv).start()
    
    def recv(self):
        response = self.socket.recv(4096) 
        json_recv = json.loads(response)
        return json_recv

    def send(self):
        self.requestID = (self.requestID + 1) % 1000000 
        self.socket.send(json.dumps(message).encode())

    def requestClientId(self):
        """ Method that requests a client id from the server """
        message = {"method": "requestClientId", "requestID": self.requestID}
        self.send(message)
        

    def send_and_recv(self, message):
        """ Method that sends a json message and receives a json response """
        self.requestID = (self.requestID + 1) % 1000000 
        self.socket.send(json.dumps(message).encode())

    def generateRequest(self, method, terms=[], docIDs=[], pairs=[]):
        if type(terms) is str:
            terms = [terms]
        if type(docIDS) is int:
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

    
    def getDistinctTermsCount(self):
        message = self.generateRequest("getDistinctTermsCount")
        self.send(message)
        
    
    # NB: not super accurate, because some languages have words which consist of ascii characters only (e.g. "amore" in Italian)
    def getEnglishTermsCount(self):
        message = self.generateRequest("getEnglishTermsCount")
        self.send(message)

    def getTermFrequency(self, terms, docIDs) -> int:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("getTermFrequency",
                                       pairs=list(zip(terms, docIDs)))
        self.send(message)


    def getDocFrequency(self, terms) -> int:
        if type(terms) == str:
            terms = [terms]
        message = self.generateRequest("getDocFrequency", terms=terms)
        self.send(message)
        
    def getDocumentsTermOccursIn(self, terms) -> List[int]:
        if type(terms) == str:
            terms = [terms]
        message = self.generateRequest("getDocumentsTermOccursIn", terms=terms)
        self.send(message)

    def getPostingList(self, terms, docIDs) -> List[int]:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("getPostingList",
                                       pairs=list(zip(terms, docIDs)))
        self.send(message)


    def tfidf(self, terms, docIDs) -> float:
        if type(terms) == str:
            terms = [terms]
        if type(docIDs) == int:
            docIDs = [docIDs]
        message = self.generateRequest("tfidf",
                                       pairs=list(zip(terms, docIDs)))
        self.send(message)

    def getNumDocs(self) -> int:
        message = self.generateRequest("getNumDocs")
        self.send(message)
        

    def getDocIDs(self) -> Set[int]:
        message = sel.generateRequest("getDocIDs")
        self.send(message)
        