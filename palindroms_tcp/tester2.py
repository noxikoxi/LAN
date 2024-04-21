import random
import time
import socket

server_address = ('localhost', 2020)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)


def sendReq(req, sock):
    print("Sending ", req)
    sock.send(req)
    time.sleep(random.random() * 2)


print("TEST")
sendReq(b'kot', sock)
sendReq(b'\r\npies', sock)
print(sock.recv(1024))
sendReq(b'\r\nszczur', sock)
sendReq(b'\r\nmalpa\r\n', sock)
sendReq(b'Elo ', sock)
sendReq(b'Siema\r\n', sock)
sendReq(b'abc', sock)
sendReq(b'cba\r\n ', sock)
print(sock.recv(1024))
sock.shutdown(1)
print(sock.recv(1024))