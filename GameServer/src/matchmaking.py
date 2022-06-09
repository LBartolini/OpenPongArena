from room import Room
from threading import Lock
import time
from typing import List
import random
from user import UserHandler

class Matchmaking():
    LOOP_WAIT: float = 1.0

    ELO_TRIES: int = 5 # tries to go to the next level of range
    ELO_DIFFERENCE: List[int] = [50, 100, 300]

    def __init__(self, n_rooms: int = 20) -> None:
        self.rooms: List[Room] = [Room() for _ in range(n_rooms)]
        self.waiting_players = []

        self.mutex_waiting_players = Lock()

    def fill_room(self, room: Room) -> None:
        #TODO
        # cerco casualmente  il primo player, dopodichè il secondo lo cerco casualmente con differenza di ELO di max 50
        # se dopo 5 tentativi non lo trovo passo a differenza di ELO max di 100 e poi 300 e poi nessun limite
        pass

    
    def handle_matchmaking(self) -> None:
        '''
        Thread run indipendently that handles rooms and players
        Loops through free rooms and tries to fill them with adequate players based on their ELO
        '''
        i = 0
        while True:
            with self.mutex_waiting_players:
                if not self.rooms[i].full():
                    self.fill_room(self.rooms[i])

            i = (i+1)%len(self.rooms)
            time.sleep(self.LOOP_WAIT)

    def add_waiting_player(self, player: UserHandler) -> None:
        with self.mutex_waiting_players:
            self.waiting_players.append(player)
