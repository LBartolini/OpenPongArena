import socket

from . import game_utils
import pygame
import os
import threading
from cryptography.fernet import Fernet
import utils
import time

RENDEZVOUS = ('lbartolini.ddns.net', 9000)

class Game:
    def __init__(self, username: str, elo: float, sock: socket.socket) -> None:
        self.username: str = username
        self.elo: float = elo
        self.sock: socket.socket = sock
        self.sock.settimeout(None)  # set the socket to blocking mode

        self.input_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.input_socket.bind(('0.0.0.0', 4001))
        self.game_socket.bind(('0.0.0.0', 4000))
        self.input_dest: tuple[str, int] = None

        self.sim = None

        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            game_utils.Window.RESOLUTION)
        pygame.display.set_caption("Open Pong Arena")
        pygame.display.set_icon(pygame.image.load(os.path.join(os.path.dirname(
            __file__), '..', '..', 'assets', 'icon.png')))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont('Arial', 45)
        self.font: pygame.font.Font = pygame.font.SysFont('Arial', 15)
        self.timer = 0

        self.opponent: tuple[str, float] = None
        self.running: bool = True
        self.found: int = -1  # -1 == not found, 0 == searching, 1 == found
        self.is_home: bool = True
        self.is_waiting: bool = False
        self.is_playing: bool = False
        self.has_won = False
        self.has_lost = False
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

    def won(self) -> None:
        # the player was playing
        self.is_playing = False
        self.has_won = True

    def lost(self) -> None:
        # the player was playing
        self.is_playing = False
        self.has_lost = True

    def go_home(self) -> None:
        self.found = -1
        self.has_won = False
        self.has_lost = False
        self.is_playing = False
        self.is_home = True
        self.init_home()

    def quit(self) -> None:
        self.running = False
        try:
            f = Fernet(utils.get_fernet_key())
            self.sock.send(f.encrypt('--quit'.encode()))
            self.sock.close()
        except Exception:
            pass
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
        b = self.sim.ball
        paddle_left, paddle_right = self.sim.paddle_left, self.sim.paddle_right
        user_info_w, user_info_h = self.font.size(self.user_info)
        opponent_info = '{} ({})'.format(self.opponent[0], self.opponent[1])
        opponent_info_w, opponent_info_h = self.font.size(opponent_info)
        if self.player_side == '1':
            # the user info must be displayed on the left side of the screen, and the opponent
            # info must be displayed on the right side of the screen
            self.screen.blit(self.font.render(self.user_info, True, game_utils.ColorPalette.WHITE),
                             (user_info_w * 1/3, user_info_h * 4/3))
            self.screen.blit(self.font.render(opponent_info, True, game_utils.ColorPalette.WHITE),
                             (game_utils.Window.WIDTH - opponent_info_w - opponent_info_w * 1/3, opponent_info_h * 4/3))
        else:
            # the user info must be displayed on the right side of the screen, and the opponent
            # info must be displayed on the left side of the screen
            self.screen.blit(self.font.render(opponent_info, True, game_utils.ColorPalette.WHITE),
                             (opponent_info_w * 1/3, opponent_info_h * 4/3))
            self.screen.blit(self.font.render(self.user_info, True, game_utils.ColorPalette.WHITE),
                             (game_utils.Window.WIDTH - user_info_w - user_info_w * 1/3, user_info_h * 4/3))
        score = '{} - {}'.format(self.sim.score_left, self.sim.score_right)
        score_w, score_h = self.font.size(score)
        self.screen.blit(self.font.render(score, True, game_utils.ColorPalette.WHITE),
                         (game_utils.Window.WIDTH / 2 - score_w / 2, score_h * 4/3))

        # draw the ball
        pygame.draw.circle(self.screen, game_utils.ColorPalette.WHITE,
                           (int(b.pos_x), int(b.pos_y)), int(b.RADIUS))

        # draw the paddles (we have to color the player paddle in green)
        if self.player_side == '1':
            pygame.draw.rect(self.screen, game_utils.ColorPalette.LIGHT_GREEN,
                             (int(paddle_left.pos_x), int(paddle_left.pos_y), int(paddle_left.WIDTH), int(paddle_left.HEIGHT)))
            pygame.draw.rect(self.screen, game_utils.ColorPalette.WHITE,
                             (int(paddle_right.pos_x), int(paddle_right.pos_y), int(paddle_right.WIDTH), int(paddle_right.HEIGHT)))
        else:
            pygame.draw.rect(self.screen, game_utils.ColorPalette.WHITE,
                             (int(paddle_left.pos_x), int(paddle_left.pos_y), int(paddle_left.WIDTH), int(paddle_left.HEIGHT)))
            pygame.draw.rect(self.screen, game_utils.ColorPalette.LIGHT_GREEN,
                             (int(paddle_right.pos_x), int(paddle_right.pos_y), int(paddle_right.WIDTH), int(paddle_right.HEIGHT)))

    @ draw
    def draw_waiting_for_player(self):
        #  display on text "Waiting for another player to join..."
        self.wait_text = "Waiting for another player to join..."
        wait_width, wait_height = self.font.size(self.wait_text)
        self.screen.blit(self.font.render(self.wait_text, True, game_utils.ColorPalette.WHITE), (
            game_utils.Window.WIDTH / 2 - wait_width / 2, game_utils.Window.HEIGHT / 2 - wait_height / 2))

    @draw
    def draw_win(self):
        #  display on text "You won!"
        self.win_text = "You Won!"
        win_width, win_height = self.font.size(self.win_text)
        self.screen.blit(self.font.render(self.win_text, True, game_utils.ColorPalette.WHITE), (
            game_utils.Window.WIDTH / 2 - win_width / 2, game_utils.Window.HEIGHT / 2 - win_height / 2))

    @draw
    def draw_lose(self):
        #  display on text "You lost!"
        self.lose_text = "You Lost!"
        lose_width, lose_height = self.font.size(self.lose_text)
        self.screen.blit(self.font.render(self.lose_text, True, game_utils.ColorPalette.WHITE), (
            game_utils.Window.WIDTH / 2 - lose_width / 2, game_utils.Window.HEIGHT / 2 - lose_height / 2))

    def run(self) -> None:
        while self.running:
            self.clock.tick(game_utils.Game.FPS)
            if self.is_home:
                self.home_events()  # events handler for home screen
                self.draw_home()
            elif self.is_waiting:
                # start a thread that waits for the server to find an opponent
                if self.found == -1:
                    threading.Thread(target=self.handle_match).start()
                    self.found = 0
                self.waiting_events()  # events handler for waiting screen
                self.draw_waiting_for_player()
            elif self.is_playing:
                self.game_events()  # events handler for game screen
                self.draw_game()
            elif self.has_won:
                self.won_events() # events handler for winning screen
                self.draw_win()
                self.timer += 1
                if self.timer >= game_utils.Game.WIN_TIME:
                    self.timer = 0
                    self.go_home()
            elif self.has_lost:
                self.lost_events()
                self.draw_lose()
                self.timer += 1
                if self.timer >= game_utils.Game.LOSE_TIME:
                    self.timer = 0
                    self.go_home()

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
        action = ('0', '0')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if self.input_dest is not None:
                    # 1: UP, -1: DOWN, 0: NO_ACTION
                    if event.key == pygame.K_UP:
                        utils.send_udp(self.input_socket, self.input_dest, '1')
                        action = ('1', '0') if self.player_side == '1' else (
                            '0', '1')
                    elif event.key == pygame.K_DOWN:
                        utils.send_udp(self.input_socket,
                                       self.input_dest, '-1')
                        action = (
                            '-1', '0') if self.player_side == '1' else ('0', '-1')
        self.sim.simulate(action)

    def won_events(self):
        # user will be prompted a winning screen for 3 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def lost_events(self):
        # user will be prompted a lose screen for 3 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            

    def handle_match(self) -> None:
        f = Fernet(utils.get_fernet_key())
        #  Let the server know that we are searching for a match
        self.sock.send(f.encrypt('--searching'.encode()))
        #  Wait for the server to send us a match
        #  The client will receive a response like this...
        #  --found|<player_one|player_two>|<opponent_username>|<opponent_elo>

        #  TODO: catch the exception (ConnectionAbortedError) if the user has quit the game
        response = f.decrypt(self.sock.recv(1024)).decode().split('|')
        self.player_side = response[1]
        # player_side == 1: left player
        # player_side == 2: right player
        self.opponent = (response[2], float(response[3]))
        self.found = 1

        self.input_socket.sendto(f"I|{self.username}", RENDEZVOUS)
        self.game_socket.sendto(f"G|{self.username}", RENDEZVOUS)

        self.sim = game_utils.Simulation()

        self.start_game()
        _, self.input_dest = utils.recv_udp(self.input_socket)
        while self.is_playing:
            if not self.running:
                self.quit()
            else:
                msg, _ = utils.recv_udp(self.game_socket)
                if msg[:2] == '--':
                    #  --W|new_elo or --L|new_elo
                    result = msg.replace('--', '').split('|')[0] 
                    self.elo += float(msg.split('|')[1])
                    if result == 'W':
                        self.won()
                    elif result == 'L':
                        self.lost()
                    break

                self.sim.import_state(msg)


if __name__ == '__main__':
    Game('test', 1500, socket.socket())
