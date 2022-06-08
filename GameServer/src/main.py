import socket
import threading
from user import UserHandler
from typing import List
import json


class Server():
    def __init__(self, env_config: dict) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connections: List[UserHandler] = []
        self.host: str = "0.0.0.0"
        self.port: int = 5000
        
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.env_config: dict = env_config
        print("Listening...")

    def run(self) -> None:
        while True:
            ret: tuple[socket.socket, socket._RetAddress] = self.sock.accept()
            connection: socket.socket = ret[0]
            address: socket._RetAddress = ret[1]
            user: UserHandler = UserHandler(connection, self.env_config)
            self.connections.append(user)
            print(f"Client Connected [{address}]")

            cThread = threading.Thread(target=user.handler, args=())
            cThread.deamon = True
            cThread.start()


if __name__ == "__main__":
    with open("environment.json", "r") as f:
        env_config: dict = json.load(f)

    server: Server = Server(env_config)
    try:
        server.run()
    except:
        server.sock.close()
