import socket
from cryptography.fernet import Fernet
import utils

config = utils.open_environment()
fernet = Fernet(config['key'])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.13', 5000))
print("connected")

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(('0.0.0.0', 4001))

sock.send(fernet.encrypt(bytes("--version|0.0", "utf-8")))
print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

sock.send(fernet.encrypt(bytes("--login|cristian|Cristian#1", "utf-8")))
#sock.send(fernet.encrypt(bytes("--login|cioncio|lorebart", "utf-8")))
print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

sock.send(fernet.encrypt(bytes("--searching", "utf-8")))

print(fernet.decrypt(sock.recv(1024)).decode("utf-8"))

while True:
    print(utils.receive_data_udp(udp, 1024)[0])

sock.send(fernet.encrypt(bytes("--quit", "utf-8")))
sock.close()