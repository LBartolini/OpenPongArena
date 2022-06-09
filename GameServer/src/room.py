from user import UserHandler

class Room():
    
    def __init__(self) -> None:
        self.player_one: UserHandler = None
        self.player_two: UserHandler = None

    def add_player(self, player: UserHandler) -> None:
        if self.player_one is None and self.player_two is not player:
            self.player_one = player
        elif self.player_two is None and self.player_one is not player:
            self.player_two = player

    def full(self) -> bool:
        return self.player_one is not None and self.player_two is not None

    def reset_room(self) -> None:
        self.player_one = None
        self.player_two = None

    def __str__(self) -> str:
        return self.player_one.username + " vs " + self.player_two.username