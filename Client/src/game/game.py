import socket
from . import game_utils
import pygame
import os
import threading
from cryptography.fernet import Fernet
import utils


class Game:
    def __init__(self, username: str, elo: float, socket: socket.socket) -> None:
        self.username: str = username
        self.elo: float = elo
        self.sock: socket.socket = socket
        self.sock.settimeout(None)  # set the socket to blocking mode

        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            game_utils.Window.RESOLUTION)
        pygame.display.set_caption("Open Pong Arena")
        pygame.display.set_icon(pygame.image.load(os.path.join(os.path.dirname(
            __file__), '..', '..', 'assets', 'icon.png')))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont('Arial', 45)
        self.font: pygame.font.Font = pygame.font.SysFont('Arial', 15)

        self.opponent: tuple[str, int | float] | None = None
        self.running: bool = True
        self.found: int = -1  # -1 == not found, 0 == searching, 1 == found
        self.is_home: bool = True
        self.is_waiting: bool = False
        self.is_playing: bool = False
        self.init_home()
        self.run()

    def init_home(self) -> None:
        self.user_info = '{} ({})'.format(self.username, self.elo)
        self.title = 'Open Pong Arena'
        self.start_text = 'Click anywhere or press Enter/Space to enter Matchmaking.'
        self.quit_text = 'Press Esc or close Window to Quit.'
        start_width, start_height = self.font.size(self.start_text)
        quit_width, quit_height = self.font.size(self.quit_text)

        # lambda: False --> means that the button is not clickable and it represent a label
        self.start_btn = game_utils.Button(self.start_text, game_utils.Window.WIDTH / 2 - start_width / 2,
                                           game_utils.Window.HEIGHT / 2 - start_height / 2, start_width,
                                           start_height, 15, game_utils.ColorPalette.BLACK, on_click=lambda: False)
        self.quit_btn = game_utils.Button(self.quit_text, game_utils.Window.WIDTH / 2 - quit_width / 2,
                                          game_utils.Window.HEIGHT / 2 + 2 * quit_height, quit_width,
                                          quit_height, 15, game_utils.ColorPalette.BLACK, on_click=lambda: False)

    def wait_for_game(self) -> None:
        self.is_home = False
        self.is_waiting = True

    def start_game(self) -> None:
        self.is_waiting = False
        self.is_playing = True

    def quit(self) -> None:
        f = Fernet(utils.get_fernet_key())
        self.running = False
        self.sock.send(f.encrypt('--quit'.encode()))
        self.sock.close()
        pygame.quit()
        exit()

    def draw(func: callable, *args, **kwargs):
        def wrapper(self, *args, **kwargs):
            self.screen.fill(game_utils.ColorPalette.BLACK)
            func(self, *args, **kwargs)
            pygame.display.flip()
        return wrapper

    @draw
    def draw_home(self):
        #  At the top left corner of the screen we want to show the username and the ELO
        #  Title: "Open Pong Arena"
        #  Click or Press Enter/Space to Start
        #  Click or Press Esc to Quit
        user_info_w, user_info_h = self.font.size(self.user_info)
        self.screen.blit(self.font.render(self.user_info, True, game_utils.ColorPalette.WHITE),
                         (user_info_w * 1/3, user_info_h * 4/3))
        title_width, title_height = self.title_font.size(self.title)
        self.screen.blit(self.title_font.render(self.title, True, game_utils.ColorPalette.WHITE),
                         (game_utils.Window.WIDTH / 2 - title_width / 2, game_utils.Window.HEIGHT / 2 - title_height * 2))
        self.start_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)
        self.start_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    @draw
    def draw_game(self) -> None:
        ...

    @draw
    def draw_waiting_for_player(self):
        #  display on text "Waiting for another player to join..."
        self.wait_text = "Waiting for another player to join..."
        wait_width, wait_height = self.font.size(self.wait_text)
        self.screen.blit(self.font.render(self.wait_text, True, game_utils.ColorPalette.WHITE), (
            game_utils.Window.WIDTH / 2 - wait_width / 2, game_utils.Window.HEIGHT / 2 - wait_height / 2))

    def run(self) -> None:
        while self.running:
            self.clock.tick(game_utils.Game.FPS)
            if self.is_home:
                self.draw_home()
                self.home_events()  # events handler for home screen
            elif self.is_waiting:
                self.draw_waiting_for_player()
                # start a thread that waits for the server to find an opponent
                if self.found == -1:
                    threading.Thread(target=self.handle_match).start()
                    self.found = 0
                self.waiting_events()  # events handler for waiting screen
            elif self.is_playing:
                self.draw_game()
                self.game_events()  # events handler for game screen

    def home_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.wait_for_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.wait_for_game()

    def waiting_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def game_events(self) -> None:
        pass

    def handle_match(self) -> None:
        f = Fernet(utils.get_fernet_key())
        #  Let the server know that we are searching for a match
        self.sock.send(f.encrypt('--searching'.encode()))
        #  Wait for the server to send us a match
        #  The client will receive a response like this...
        #  --found|<opponent_username>|<opponent_elo>

        #  TODO: catch the exception (ConnectionAbortedError) if the user has quit the game
        response = f.decrypt(self.sock.recv(1024)).decode()
        self.opponent = (response.split('|')[1], float(response.split('|')[2]))
        self.found = 1

        self.start_game()
        while self.is_playing:
            if not self.running:
                self.quit()
            else:
                pass


if __name__ == '__main__':
    Game('test', 1500, socket.socket())
