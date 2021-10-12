import socket

from google.protobuf.internal import decoder


class Server:
    def __init__(self, host, port, handles):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.handles = handles

    def run(self):
        self.socket.connect((self.host, self.port))
        while True:
            try:
                decoder._DecodeVarint32
                msg = self.socket.recv(1024)
                print(msg)
            except:
                pass

    def send(self, message):
        pass


class Handler:
    def active(self):
        pass

    def inactive(self):
        pass

    def read(self):
        pass
