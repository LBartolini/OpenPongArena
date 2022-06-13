import socket
from cryptography.fernet import Fernet
import utils
import time

config = utils.open_environment()
fernet = Fernet(config['Key'])
TICK = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 5000))
print("connected")

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(('0.0.0.0', 4001))

sock.send(fernet.encrypt(bytes("--version|0.0", "utf-8")))
print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

#sock.send(fernet.encrypt(bytes("--login|cristian|Cristian#1", "utf-8")))
sock.send(fernet.encrypt(bytes("--login|cioncio|lorebart", "utf-8")))
print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

sock.send(fernet.encrypt(bytes("--searching", "utf-8")))

print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

_, addr = utils.receive_data_udp(udp, 1024)
print(addr)
i = 0
while True:
    utils.send_data_udp(udp, addr, i)

    i += 1
    i %= 4

    time.sleep(1/TICK)

sock.send(fernet.encrypt(bytes("--quit", "utf-8")))
sock.close()