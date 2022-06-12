import os
import socket
import json
import traceback
from cryptography.fernet import Fernet

def open_environment() -> dict:
    with open(os.path.join(os.path.dirname(__file__), '..', 'environment.json')) as f:
        return json.load(f)

fernet = Fernet(open_environment()["key"])

def send_data(user, message: str) -> None:
    global fernet

    try:
        user.connection.send(fernet.encrypt(bytes(str(message), "utf-8")))
    except Exception:
        user.close()

def receive_data(user, length: int = 2048) -> str:
    global fernet

    try:
        x = fernet.decrypt(user.connection.recv(length)).decode("utf-8")
        
        return x
    except Exception:
        user.close()

def send_data_udp(udp_socket: socket.socket, destination: tuple[str, int], message: str) -> int:
    global fernet

    try:
        return udp_socket.sendto(fernet.encrypt(bytes(str(message), "utf-8")), destination)
    except Exception:
        print("failed")

def receive_data_udp(udp_socket: socket.socket, length: int = 2048) -> tuple[str, tuple[str, int]]:
    global fernet

    try:
        print("trying")
        message, address = udp_socket.recvfrom(length)
        x = fernet.decrypt(message).decode("utf-8")
        print("ok")
        return x, address
    except Exception:
        print("pippo")
        traceback.print_exc()
        return "", ()