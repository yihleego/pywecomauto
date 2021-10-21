import socket
import threading
import time

from google.protobuf.internal import decoder, encoder

from pywecomauto import rpa_pb2


class Server:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def run(self):
        self.socket.connect((self.host, self.port))
        thread = threading.Thread(target=self.listen)
        thread.start()
        print('running')

    def listen(self):
        remainder = None
        buf_size = 1024
        while True:
            try:
                if not remainder or len(remainder) <= 0:
                    buf = self.socket.recv(buf_size)
                    print('2-len:', len(buf))
                    size, begin = decoder._DecodeVarint32(buf, 0)
                    end = begin + size
                    message, remainder = self.test(begin, end, buf)
                    print('message2', message)
                else:
                    buf = remainder
                    print('1-len:', len(buf))
                    try:
                        size, begin = decoder._DecodeVarint32(buf, 0)
                        print('长度足够 成功')
                    except:
                        print('长度不够 需要追加', buf_size - len(buf))
                        tmp = self.socket.recv(buf_size - len(buf))
                        buf = buf + tmp
                        size, begin = decoder._DecodeVarint32(buf, 0)
                    end = begin + size
                    message, remainder = self.test(begin, end, buf)
                    print('message1', message)
            except Exception as e:
                print(e)

    def test(self, begin, end, buf):
        remainder = None
        length = len(buf)
        if end > length:
            print('追加', end - length)
            p1 = buf[begin:]
            p2 = self.socket.recv(end - length)
            data = p1 + p2
        else:
            print('多余', length - end)
            data = buf[begin:end]
            if length - end > 0:
                remainder = buf[end:]
        message = rpa_pb2.Message()
        message.ParseFromString(data)
        return message, remainder

    def send(self, content):
        message = rpa_pb2.Message()
        message.id = 3
        message.content = content
        data = message.SerializeToString()
        r = encoder._VarintBytes(len(data)) + data
        self.socket.send(r)


class Handler:
    def active(self):
        pass

    def inactive(self):
        pass

    def read(self):
        pass


if __name__ == '__main__':
    s = Server('localhost', 9999)
    s.run()
    while True:
        time.sleep(1)
        s.send('sb')
