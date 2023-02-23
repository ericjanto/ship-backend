import socket
import sys
import threading

from PositionalInvertedIndex import PositionalInvertedIndex

class PIIServerAPI:

    def __init__(self, index, ip, port):
        self.index = index

        self.recvSocket = None

        self.initialiseSocket(ip, socket)

        self.listen()

    def initialiseSocket(self, ipAddr, socketNo):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvSocket.bind((ipAddr, socketNo))

    def listen(self):

