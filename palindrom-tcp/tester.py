import socket
import time
import random

SERVER_IP = '127.0.0.1'
SERVER_PORT = 2020
test_num = 0
correct_tests = 0

invalid_tests_numbers = []

def test1(socket):
    print("TEST1")
    print("Sending ", b'kajak\r\n','\n')
    sock.send(b'kajak\r\n')
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

def test2(socket):
    print("TEST2")
    print("Sending ", b'Ala i kot\r\n','\n')
    sock.send(b'Ala i kot\r\n')
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

def test3(socket):
    print("TEST3")
    print("Sending ", b'xyz\r\nucho oko\r\n','\n')
    sock.send(b'xyz\r\nucho oko\r\n')
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

def test4(socket):
    print("TEST4")

    req = b'ABBA 1972\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))

    req = b'Ola ma psa.\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))

    req = b' nadmiarowe   spacje \r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))

    req = b'a i o u w z\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')


def test5(socket):
    print("TEST5")
    req = b'oraz\x00zero\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

def test6(socket):
    print("TEST6")
    req = b'kot'
    print("Sending ", req)
    sock.send(req)
    time.sleep(random.random())
    req = b'\r\npies'
    print("Sending ", req)
    sock.send(req)
    time.sleep(random.random())
    time.sleep(1)
    req = b'\r\nkrowa'
    print("Sending ", req)
    sock.send(req)
    time.sleep(random.random())
    req = b'\r\nmalpa\r\n'
    print("Sending ", req)
    sock.send(req)
    time.sleep(random.random())
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print(sock.recv(1024))
    print(sock.recv(1024))
    print('\n')

def test7(socket):
    print("TEST6")
    requests = [w + ' ' for w in "abcdefghijklmnopqrstuvwxy"]
    for r in requests:
        print("Sending ", r)
        sock.send(r.encode())
        time.sleep(random.random())
    req = b'z\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

    
def test8(socket):
    print("TEST8")
    req = b'aLA i kot\r\nmagDa gesler\r\nkajak i\r\n'
    print("Sending ", req)
    sock.send(req)
    print(sock.recv(1024))
    sock.shutdown(1)
    print(sock.recv(1024))
    print('\n')

tests = [test1, test2, test3, test4, test5, test6, test8]

try:
    for test in tests:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if sock is not None:
            # sock.settimeout(10)
            sock.connect((SERVER_IP, SERVER_PORT))
            test(sock)


except socket.timeout:
    print("Socket timeout")
except socket.error as e:
    print("socket error", e)



