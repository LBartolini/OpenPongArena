import os
import socket
import json
from cryptography.fernet import Fernet

def open_environment() -> dict:
    with open(os.path.join(os.path.dirname(__file__), '..', 'environment.json')) as f:
        return json.load(f)

def send_data(connection: socket.socket, fernet: Fernet, message: str) -> None:
    connection.send(fernet.encrypt(bytes(message)))

def receive_data(connection: socket.socket, fernet: Fernet, length: int = 2048) -> str:
    return fernet.decrypt(connection.recv(length)).decode("utf-8")