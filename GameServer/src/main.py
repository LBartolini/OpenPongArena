import socket
import threading
from user import UserHandler
from typing import List
import utils
from database import Database


class Server():
    def __init__(self, env_config: dict) -> None:
        self.env_config: dict = utils.open_environment()
        
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connections: List[UserHandler] = []
        self.host: str = self.env_config["ip"]
        self.port: int = self.env_config["port"]
        
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        self.database = Database(self.env_config['DB'])
        print("Listening...")

    def run(self) -> None:
        '''
        Initial connection from Client to the Server
        '''
        while True:
            ret: tuple[socket.socket, socket._RetAddress] = self.sock.accept()
            connection: socket.socket = ret[0]
            address: socket._RetAddress = ret[1]
            user: UserHandler = UserHandler(connection, self.env_config, self.database)
            self.connections.append(user)
            print(f"Client Connected [{address}]")

            cThread = threading.Thread(target=user.handler, args=())
            cThread.deamon = True
            cThread.start()


if __name__ == "__main__":
    server: Server = Server()
    try:
        server.run()
    except:
        server.sock.close()
