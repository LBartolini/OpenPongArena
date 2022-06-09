import socket
from cryptography.fernet import Fernet
from typing import List
from database import Database
from utils import *

class UserHandler():
    def __init__(self, connection: socket.socket, env_config: dict, database: Database) -> None:
        self.username: str = ""
        self.elo = -1
        
        self.logged: bool = False
        self.connected: bool = True
        
        self.database: Database = database
        self.env_config: dict = env_config
        self.connection: socket  = connection
        self.fernet = Fernet(self.env_config["key"])
    
    def handler(self) -> None:
        version_check: str = receive_data(self.connection, self.fernet).split("|")
        if len(version_check) != 2: 
            send_data(self.connection, self.fernet, "--version_FAIL")
        elif version_check[0] != "--version":
            send_data(self.connection, self.fernet, "--version_FAIL")
        elif version_check[1] != self.env_config["version"]:
            send_data(self.connection, self.fernet, "--version_FAIL")
        else:
            send_data(self.connection, self.fernet, "--version_OK")

        while True:
            data: str = receive_data(self.connection, self.fernet)
            data: List[str] = data.split("|")

            if data[0] == "--quit": 
                self.close()

            elif data[0] == "--login" and len(data) == 3:
                if self.login(data[1], data[2]):
                    send_data(self.connection, self.fernet, "--login_success|{:.2f}".format(self.elo))
                else:
                    send_data(self.connection, self.fernet, "--login_failure")

    def login(self, username: str, password: str) -> None:
        res, elo = self.database.verify_user(username, password)
        if not res: 
            return False
        
        self.logged = True
        self.username = username
        self.elo = elo
        return True
    
    def close(self) -> None:
        self.connected = False
        self.connection.close()
        exit()