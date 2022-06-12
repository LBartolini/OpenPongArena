from threading import Lock, Thread
from typing import List
import time
import random
import socket
from utils import send_data, send_data_udp, receive_data_udp
import user_handler

class Room():
    TICK: int = 1
    GAME_PORT: int = 4000
    INPUT_PORT: int = 4001
    
    def __init__(self) -> None:
        self.playing: bool = False

        self.player_one: user_handler.UserHandler = None
        self.player_two: user_handler.UserHandler = None
        self.n_players: int = 0

        self.buffer_one: List[int] = []
        self.mutex_buffer_one: Lock = Lock()
        self.buffer_two: List[int] = []
        self.mutex_buffer_two: Lock = Lock()

        self.udp_input_one = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_input_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_game = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def add_player(self, player: user_handler.UserHandler) -> None:
        if self.player_one is None and self.player_two is not player:
            self.player_one = player
            self.n_players += 1
        elif self.player_two is None and self.player_one is not player:
            self.player_two = player
            self.n_players += 1

    def full(self) -> bool:
        return self.player_one is not None and self.player_two is not None

    def reset(self) -> None:
        self.playing = False

        self.player_one = None
        self.player_two = None
        self.n_players = 0

        self.buffer_one = []
        self.mutex_buffer_one = Lock()
        self.buffer_two = []
        self.mutex_buffer_two = Lock()

        self.udp_input_one.close()
        self.udp_input_two.close()
        self.udp_game.close()

        self.udp_input_one = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_input_two = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_game = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)


    def reset_room(self) -> None:
        self.player_one = None
        self.player_two = None
        self.n_players = 0

    def add_action_one(self, action: int) -> None:
        with self.mutex_buffer_one:
            self.buffer_one.append(action)
    
    def pop_action_one(self) -> int:
        with self.mutex_buffer_one:
            x = self.buffer_one.pop(0) if len(self.buffer_one)>0 else -1
        
        return x
    
    def add_action_two(self, action: int) -> None:
        with self.mutex_buffer_two:
            self.buffer_two.append(action)
    
    def pop_action_two(self) -> int:
        with self.mutex_buffer_two:
            x = self.buffer_two.pop(0) if len(self.buffer_two)>0 else -1
        
        return x

    def handle_input_one(self):
        dest: tuple[str, int] = (self.player_one.connection.getpeername()[0], self.INPUT_PORT)
        send_data_udp(self.udp_input_one, dest, "--init")

        while self.playing:
            msg, addr = receive_data_udp(self.udp_input_one)
            if addr == dest:
                self.add_action_one(msg)

    def handle_input_two(self):
        dest: tuple[str, int] = (self.player_two.connection.getpeername()[0], self.INPUT_PORT)
        send_data_udp(self.udp_input_two, dest, "--init")

        while self.playing:
            msg, addr = receive_data_udp(self.udp_input_two)
            if addr == dest:
                self.add_action_two(msg)

    def start_game(self) -> None:
        self.player_one.status = user_handler.UserHandler.PLAYING
        self.player_two.status = user_handler.UserHandler.PLAYING
        self.playing = True

        send_data(self.player_one, f"--found|{self.player_two.username}|{self.player_two.elo}")
        send_data(self.player_two, f"--found|{self.player_one.username}|{self.player_one.elo}")

        cThread = Thread(target=self.handle_input_one, args=())
        cThread.deamon = True
        cThread.start()

        cThread = Thread(target=self.handle_input_two, args=())
        cThread.deamon = True
        cThread.start()

        #dest_one = (self.player_one.connection.getpeername()[0], 4000)
        #dest_two = (self.player_two.connection.getpeername()[0], 4001)
        
        while True:
            #send_data_udp(self.udp_game, dest_one, "Pippo")
            #send_data_udp(self.udp_game, dest_two, "Pluto")
            with (self.mutex_buffer_one, self.mutex_buffer_two):
                print('\n1:', self.buffer_one)
                print('2:', self.buffer_two)
            
            time.sleep(1/self.TICK)

        # once client receive this, it should start two new threads
        # 1. receive game updates from server and render them (port 4000)
        # 2. wait for user input and send to server (port 4001)
        # IMPORTANT: client should start these UDP sockets at startup to ensure that those ports are unused

        # TODO start 3 threads
        # 1. game: simulate the game and send the update to the clients
        # 2. input_player_one: expects inputs from player one and updates game
        # 3. input_player_two: expects inputs from player two and updates game

    def __str__(self) -> str:
        p1 = f"P1 [{self.player_one.username if self.player_one is not None else 'None'}]"
        p2 = f"P2 [{self.player_two.username if self.player_two is not None else 'None'}]"

        return p1 + "vs" + p2

class Matchmaking():
    LOOP_WAIT: float = 0.2

    ELO_TRIES: int = 5  # tries to go to the next level of range
    ELO_DIFFERENCE: List[int] = [50, 100, 300]

    def __init__(self, n_rooms: int = 20) -> None:
        self.rooms: List[Room] = [Room() for _ in range(n_rooms)]
        self.waiting_players = []

        self.mutex_waiting_players = Lock()

    def fill_room(self, room: Room) -> None:
        # cerco casualmente  il primo player, dopodichè il secondo lo cerco casualmente con differenza di ELO di max 50
        # se dopo 5 tentativi non lo trovo passo a differenza di ELO max di 100 e poi 300 e poi nessun limite
        if room.n_players == 0:
            player_one: user_handler.UserHandler = random.choice(self.waiting_players)
            room.add_player(player_one)
            self.waiting_players.remove(player_one)
        
        player_one: user_handler.UserHandler = room.player_one

        for ELO_RANGE in self.ELO_DIFFERENCE:
            for _ in range(self.ELO_TRIES):
                if len(self.waiting_players)==0: return

                player_two: user_handler.UserHandler = random.choice(self.waiting_players)

                if player_two is not player_one and abs(player_one.elo - player_two.elo) <= ELO_RANGE:
                    room.add_player(player_two)
                    self.waiting_players.remove(player_two)
                    return

        for _ in range(self.ELO_TRIES):
            player_two = random.choice(self.waiting_players)
            if player_two is not player_one:
                room.add_player(player_two)
                self.waiting_players.remove(player_two)
                return

    def handle_matchmaking(self) -> None:
        '''
        Thread run indipendently that handles rooms and players
        Loops through free rooms and tries to fill them with adequate players based on their ELO
        '''
        i = 0
        while True:
            room = self.rooms[i]
            with self.mutex_waiting_players:
                if not room.full() and len(self.waiting_players)>=2:
                    self.fill_room(room)
                    if room.full():
                        print("filled room: "+str(room))
                        room.start_game()
                    

            i = (i+1) % len(self.rooms)
            time.sleep(self.LOOP_WAIT)

    def add_waiting_player(self, player: user_handler.UserHandler) -> None:
        if not player.logged: return

        with self.mutex_waiting_players:
            self.waiting_players.append(player)
            player.status = user_handler.UserHandler.MATCHMAKING
    
    def remove_waiting_player(self, player: user_handler.UserHandler) -> None:
        if player.status == user_handler.UserHandler.MATCHMAKING:
            with self.mutex_waiting_players:
                try:
                    self.waiting_players.remove(player)
                except:
                    pass