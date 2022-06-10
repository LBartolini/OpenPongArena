import socket
import threading
from user_handler import UserHandler
from typing import List
import utils
from database import Database
import matchmaking

class Server():
    def __init__(self) -> None:
        self.env_config: dict = utils.open_environment()
        
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.connections: List[UserHandler] = []
        self.connections_lock = threading.Lock()

        self.host: str = self.env_config["ip"]
        self.port: int = self.env_config["port"]
        
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)

        self.database = Database(self.env_config['DB'])
        self.matchmaking = matchmaking.Matchmaking()
        print("Listening...")

    def search_connected_username(self, username) -> bool:
        with self.connections_lock:
            for user_connected in self.connections:
                if user_connected.username == username:
                    return True
            
            return False

    def remove_connection(self, user):
        with self.connections_lock:
            try:
                self.connections.remove(user)
            except:
                pass

    def run(self) -> None:
        '''
        Handles initial connection from Client to the Server
        '''
        cThread = threading.Thread(target=self.matchmaking.handle_matchmaking, args=())
        cThread.deamon = True
        cThread.start()

        while True:
            ret: tuple[socket.socket, socket._RetAddress] = self.sock.accept()
            connection: socket.socket = ret[0]
            address: socket._RetAddress = ret[1]
            user: UserHandler = UserHandler(connection, self.env_config, self.database, self.matchmaking, self)
            with self.connections_lock:
                self.connections.append(user)
            print(f"Client Connected [{address}]")

            cThread = threading.Thread(target=user.handler, args=())
            cThread.deamon = True
            cThread.start()


if __name__ == "__main__":
    server: Server = Server()
    try:
        server.run()
    except Exception as e:
        server.sock.close()
