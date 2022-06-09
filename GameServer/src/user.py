import socket
from typing import List
from database import Database
from utils import *

class UserHandler():
    IDLE: int = 0
    MATCHMAKING: int = 1
    PLAYING: int = 2

    def __init__(self, connection: socket.socket, env_config: dict, database: Database) -> None:
        self.username: str = ""
        self.elo = -1
        
        self.logged: bool = False
        self.connected: bool = True
        self.status: int = self.IDLE # 0=nothing, 1=matchmaking, 2=playing
        
        self.database: Database = database
        self.env_config: dict = env_config
        self.connection: socket  = connection
    
    def handler(self) -> None:
        version_check: str = receive_data(self).split("|")
        if len(version_check) != 2: 
            send_data(self, "--version_FAIL")
        elif version_check[0] != "--version":
            send_data(self, "--version_FAIL")
        elif version_check[1] != self.env_config["version"]:
            send_data(self, "--version_FAIL")
        else:
            send_data(self, "--version_OK")

        while True:
            data: str = receive_data(self)
            data: List[str] = data.split("|")

            if data[0] == "--quit": 
                self.close()

            elif data[0] == "--login" and len(data) == 3:
                if self.login(data[1], data[2]):
                    send_data(self, "--login_success|{:.2f}".format(self.elo))
                else:
                    send_data(self, "--login_failure")

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