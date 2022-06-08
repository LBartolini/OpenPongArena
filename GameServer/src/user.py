import socket
from cryptography.fernet import Fernet
from typing import List

class UserHandler():
    def __init__(self, connection: socket.socket, env_config: dict) -> None:
        self.id: int = -1
        self.username: str = ""
        
        self.logged: bool = False
        self.connected: bool = True
        
        self.env_config: dict = env_config
        self.connection: socket  = connection
        self.fernet = Fernet(self.env_config["key"])
    
    def handler(self) -> None:
        while True:
            data: str = self.fernet.decrypt(self.connection.recv(4096)).decode("utf-8")
            data: List[str] = data.split("|")

            if data[0] == "--quit": 
                self.close()

            elif data[0] == "--login" and len(data) == 3:
                res: bool = self.login(data[1], data[2]) # username, password
                print(res)

    def login(self, username: str, password: str) -> None:
        if not self.verify_user(): 
            return False
        
        self.logged = True
        #TODO fetch info from db
        return True

    def verify_user(self, username: str, password: str) -> bool:
        # T=success, F=failure
        return False
    
    def close(self) -> None:
        self.connected = False
        self.connection.close()
        exit()