import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 2020
test_num = 0
correct_tests = 0

invalid_tests_numbers = []

tests = [
    "Ala",
    "Ala ma kota\r\n",
    "Ala kajak mazda opel w eevee",
    "apple banana orange",
    "apple banana orange\n",
    "apple banana orange\r\n",
    "level radar civic kayak omo inwni",
    " Ala banan je",
    "Spacja na koncu ",
    " Ala banan je\r\n",
    "Spacja na koncu \r\n",
    "Spacja na koncu\r\n ",
    "Spacja  dwa  razy w srodku",
    "level&*^%kayak",
    "Ala ma 12 lat",
    "ALA\0 to jest cos",
    "Ala ma\n psa",
    "",
    "\n",
    "\r\n",
    "w"
]
correct = [
    "1/1",
    "1/3\r\n",
    "4/6",
    "0/3",
    "0/3\r\n",
    "0/3\r\n",
    "6/6",
    "ERROR",
    "ERROR",
    "ERROR\r\n",
    "ERROR\r\n",
    "ERROR",
    "ERROR",
    "ERROR",
    "ERROR",
    "ERROR",
    "ERROR",
    "0/0",
    "0/0\r\n",
    "0/0\r\n",
    "1/1"
]

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if sock is not None:
        sock.settimeout(10)

        for test in tests:
            sock.sendto(test.encode(), (SERVER_IP, SERVER_PORT))
            data, server_address = sock.recvfrom(1024)
            if data.decode() == correct[test_num]:
                correct_tests += 1
            else:
                invalid_tests_numbers.append(test_num)
            test_num += 1

        sock.close()

except socket.timeout:
    print("Socket timeout")
except socket.error as e:
    print("socket error", e)

if test_num > 0:
    print(f'Tests score: {correct_tests / test_num}\nIncorrect tests numbers: {invalid_tests_numbers}')


