from threading import Lock, Thread
from typing import List
import time
import random
import socket
from utils import send_data, send_data_udp, receive_data_udp, expected_score
from game_utils import *
import user_handler
from database import Database

RENDEZVOUS = ('lbartolini.ddns.net', 9000)

class Room():
    TICK: int = 71
    GAME_PORT: int = 4000
    INPUT_PORT: int = 4001
    MAX_SCORE = 5
    K_ELO = 20
    
    def __init__(self, database: Database) -> None:
        self.playing: bool = False

        self.player_one: user_handler.UserHandler = None
        self.player_two: user_handler.UserHandler = None
        self.n_players: int = 0

        self.buffer_one: List[int] = []
        self.mutex_buffer_one: Lock = Lock()
        self.buffer_two: List[int] = []
        self.mutex_buffer_two: Lock = Lock()

        self.database = database
        self.simulation = Simulation()

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
        self.player_one.status = user_handler.UserHandler.IDLE
        self.player_two.status = user_handler.UserHandler.IDLE
        self.__init__(self.database)

    def add_action_one(self, action: int) -> None:
        with self.mutex_buffer_one:
            self.buffer_one.append(action)
    
    def pop_action_one(self) -> int:
        with self.mutex_buffer_one:
            x = self.buffer_one.pop(0) if len(self.buffer_one)>0 else 0
        
        return x
    
    def add_action_two(self, action: int) -> None:
        with self.mutex_buffer_two:
            self.buffer_two.append(action)
    
    def pop_action_two(self) -> int:
        with self.mutex_buffer_two:
            x = self.buffer_two.pop(0) if len(self.buffer_two)>0 else 0
        
        return x

    def handle_input_one(self):
        self.udp_input_one.sendto(f"I|{self.player_one.username}", RENDEZVOUS)
        port = int(self.udp_input_one.recvfrom(32))

        dest: tuple[str, int] = (self.player_one.connection.getpeername()[0], port)
        send_data_udp(self.udp_input_one, dest, "--init")

        while self.playing:
            msg, addr = receive_data_udp(self.udp_input_one)
            if addr == dest:
                self.add_action_one(msg)

    def handle_input_two(self):
        self.udp_input_two.sendto(f"I|{self.player_two.username}", RENDEZVOUS)
        port = int(self.udp_input_two.recvfrom(32))

        dest: tuple[str, int] = (self.player_two.connection.getpeername()[0], port)
        send_data_udp(self.udp_input_two, dest, "--init")

        while self.playing:
            msg, addr = receive_data_udp(self.udp_input_two)
            if addr == dest:
                self.add_action_two(msg)

    def handle_game(self) -> None:
        self.udp_game.sendto(f"G|{self.player_one.username}", RENDEZVOUS)
        port_one = int(self.udp_game.recvfrom(32))

        self.udp_game.sendto(f"G|{self.player_two.username}", RENDEZVOUS)
        port_two = int(self.udp_game.recvfrom(32))

        dest_one: tuple[str, int] = (self.player_one.connection.getpeername()[0], port_one)
        dest_two: tuple[str, int] = (self.player_two.connection.getpeername()[0], port_two)

        while self.playing:
            if self.simulation.score_left >= self.MAX_SCORE or not self.player_two.connected:
                # vince player one
                diff_one = expected_score(self.player_two.elo, self.player_one.elo)
                diff_two = expected_score(self.player_one.elo, self.player_two.elo)
                change_one = self.K_ELO * (1 - diff_one)
                change_two = self.K_ELO * (0 - diff_two)

                send_data_udp(self.udp_game, dest_one, f"--W|{change_one}")
                send_data_udp(self.udp_game, dest_two, f"--L|{change_two}")

                self.database.log_game(self.player_one.username, self.player_two.username, change_one, change_two)
                self.reset()
                return

            elif self.simulation.score_right >= self.MAX_SCORE or not self.player_one.connected:
                # vince player two
                diff_one = expected_score(self.player_two.elo, self.player_one.elo)
                diff_two = expected_score(self.player_one.elo, self.player_two.elo)
                change_one = self.K_ELO * (0 - diff_one)
                change_two = self.K_ELO * (1 - diff_two)

                print(change_one, change_two)

                send_data_udp(self.udp_game, dest_one, f"--L|{change_one}")
                send_data_udp(self.udp_game, dest_two, f"--W|{change_two}")

                self.database.log_game(self.player_one.username, self.player_two.username, change_one, change_two)
                self.reset()
                return

            self.simulation.simulate([str(self.pop_action_one()), str(self.pop_action_two())])
            game_string = self.simulation.export_state()
            send_data_udp(self.udp_game, dest_one, game_string)
            send_data_udp(self.udp_game, dest_two, game_string)

            time.sleep(1/self.TICK)

    def start_game(self) -> None:
        self.player_one.status = user_handler.UserHandler.PLAYING
        self.player_two.status = user_handler.UserHandler.PLAYING
        self.playing = True

        send_data(self.player_one, f"--found|1|{self.player_two.username}|{self.player_two.elo}")
        send_data(self.player_two, f"--found|2|{self.player_one.username}|{self.player_one.elo}")

        cThread = Thread(target=self.handle_input_one, args=())
        cThread.deamon = True
        cThread.start()

        cThread = Thread(target=self.handle_input_two, args=())
        cThread.deamon = True
        cThread.start()

        cThread = Thread(target=self.handle_game, args=())
        cThread.deamon = True
        cThread.start()

    def __str__(self) -> str:
        p1 = f"P1 [{self.player_one.username if self.player_one is not None else 'None'}]"
        p2 = f"P2 [{self.player_two.username if self.player_two is not None else 'None'}]"

        return p1 + "vs" + p2

class Matchmaking():
    LOOP_WAIT: float = 0.2

    ELO_TRIES: int = 5  # tries to go to the next level of range
    ELO_DIFFERENCE: List[int] = [50, 100, 300]

    def __init__(self, database: Database, n_rooms: int = 20) -> None:
        self.rooms: List[Room] = [Room(database) for _ in range(n_rooms)]
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