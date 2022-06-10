from threading import Lock
import time
from typing import List
import random
import user_handler

class Room():
    
    def __init__(self) -> None:
        self.player_one: user_handler.UserHandler = None
        self.player_two: user_handler.UserHandler = None
        self.n_players = 0

    def add_player(self, player: user_handler.UserHandler) -> None:
        if self.player_one is None and self.player_two is not player:
            self.player_one = player
            self.n_players += 1
        elif self.player_two is None and self.player_one is not player:
            self.player_two = player
            self.n_players += 1

    def full(self) -> bool:
        return self.player_one is not None and self.player_two is not None

    def reset_room(self) -> None:
        self.player_one = None
        self.player_two = None
        self.n_players = 0

    def start_game(self):
        self.player_one.status = user_handler.UserHandler.PLAYING
        self.player_two.status = user_handler.UserHandler.PLAYING

    def __str__(self) -> str:
        p1 = f"P1 [{self.player_one.username if self.player_one is not None else 'None'}]"
        p2 = f"P2 [{self.player_two.username if self.player_two is not None else 'None'}]"

        return p1 + "vs" + p2

class Matchmaking():
    LOOP_WAIT: float = 1.0

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
            print("check room ", i)
            with self.mutex_waiting_players:
                if not self.rooms[i].full() and len(self.waiting_players)>=2:
                    self.fill_room(self.rooms[i])
                    # TODO check if room is full then start the game
                    print("fill room: "+str(self.rooms[i]))

            i = (i+1) % len(self.rooms)
            time.sleep(self.LOOP_WAIT)

    def add_waiting_player(self, player: user_handler.UserHandler) -> None:
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