import os
import socket
import json
from cryptography.fernet import Fernet

def open_environment() -> dict:
    with open(os.path.join(os.path.dirname(__file__), '..', 'environment.json')) as f:
        return json.load(f)

fernet = Fernet(open_environment()["key"])

def send_data(user, message: str) -> None:
    global fernet

    try:
        user.connection.send(fernet.encrypt(bytes(message, "utf-8")))
    except Exception:
        user.close()

def receive_data(user, length: int = 2048) -> str:
    global fernet

    try:
        x = fernet.decrypt(user.connection.recv(length)).decode("utf-8")
        
        return x
    except Exception:
        user.close()

def send_data_udp(udp_socket: socket.socket, destination: tuple[str, int], message: str) -> None:
    global fernet

    try:
        udp_socket.sendto(fernet.encrypt(bytes(message, "utf-8")), destination)
    except Exception:
        print("failed")

def receive_data_udp(udp_socket: socket.socket, length: int = 2048) -> tuple:
    global fernet

    try:
        message, address = udp_socket.recvfrom(length)
        x = fernet.decrypt(message).decode("utf-8")
        
        return x, address
    except Exception:
        return "", None