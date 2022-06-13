import json
import os
from cryptography.fernet import Fernet
import socket

WINDOW_WIDTH, WINDOW_HEIGHT = 400, 200
TIMEOUT = 5


def open_environment() -> dict:
    """
    Open the environment file and return the data.
    """
    with open(os.path.join(os.path.dirname(__file__), '..', 'environment.json'), 'r') as f:
        return json.load(f)


def get_fernet_key() -> bytes:
    """
    Get the fernet key from the environment file.
    """
    return bytes(open_environment()['Key'], 'utf-8')


fernet = Fernet(get_fernet_key())


def send_tcp(socket: socket.socket, data: str) -> None:
    """
    Send data over a TCP socket.
    """
    socket.send(fernet.encrypt(bytes(data, 'utf-8')))


def recv_tcp(socket: socket.socket) -> str:
    """
    Receive data over a TCP socket.
    """
    return fernet.decrypt(socket.recv(1024)).decode('utf-8')


def send_udp(socket: socket.socket, dest: tuple[str, int], data: str) -> None:
    """
    Send data over a UDP socket.
    """
    socket.sendto(fernet.encrypt(bytes(data, 'utf-8')), dest)


def recv_udp(socket: socket.socket) -> tuple[str, tuple[str, int]]:
    """
    Receive data over a UDP socket.
    """
    msg, addr = socket.recvfrom(1024)
    msg = fernet.decrypt(msg).decode('utf-8')
    return msg, addr


def get_version() -> str:
    """
    Get the version from the environment file.
    """
    return open_environment()['Version']


if __name__ == '__main__':
    print(open_environment()['Version'])
