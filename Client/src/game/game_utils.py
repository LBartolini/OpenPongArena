import pygame
import math
import threading


class Window:
    WIDTH, HEIGHT = 800, 600
    RESOLUTION = (WIDTH, HEIGHT)


class Game:
    FPS = 71


class ColorPalette:
    WHITE: tuple[int, int, int] = (255, 255, 255)
    BLACK: tuple[int, int, int] = (0, 0, 0)
    LIGHT_GREEN: tuple[int, int, int] = (50, 255, 50)


class Paddle:
    HEIGHT: int = 100
    WIDTH: int = 10
    SPEED: int = 15
    PADDING: int = 10

    START_POSITION_Y: int = (Window.HEIGHT - HEIGHT) / 2

    def __init__(self, position: str = "") -> None:
        if position == "left":
            self.start_pos = self.PADDING
        elif position == "right":
            self.start_pos = Window.WIDTH - self.WIDTH - self.PADDING
        self.pos_x = self.start_pos
        self.pos_y: float = self.START_POSITION_Y

    def move_up(self) -> None:
        if self.pos_y > 0:
            self.pos_y -= self.SPEED

    def move_down(self) -> None:
        if self.pos_y + self.HEIGHT < Window.HEIGHT:
            self.pos_y += self.SPEED

    def reset_position(self) -> None:
        self.pos_x = self.start_pos
        self.pos_y = self.START_POSITION_Y

    def get_position(self) -> tuple[int, int]:
        return self.pos_x, self.pos_y


class Button:
    """
    The Button class is used to represent a button in pygame.
    The button should have a text on it and when it is clicked it executes the bound function.
    """

    def __init__(self, text: str, pos_x: int, pos_y: int, width: int, height: int,
                 font_size: int, color: tuple[int, int, int],
                 on_click: callable,
                 on_hover: callable = None) -> None:
        self.text: str = text
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.width: int = width
        self.height: int = height
        self.font_size: int = font_size
        self.color: tuple[int, int, int] = color
        self.on_click: callable = on_click
        self.on_hover: callable = on_hover
        self.rect: pygame.Rect = pygame.Rect(
            self.pos_x, self.pos_y, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.SysFont('Arial', self.font_size)
        text = font.render(self.text, True, ColorPalette.WHITE)
        text_rect = text.get_rect()
        text_rect.center = self.rect.center
        surface.blit(text, text_rect)

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)


class Ball:
    RADIUS: int = 5
    SPEED: int = 5
    ANGLE: int = 180  # default start angle (0 <= angle <= 360)
    MAX_BOUNCE_ANGLE = 45  # degrees

    START_POSITION_X: float = Window.WIDTH / 2
    START_POSITION_Y: float = Window.HEIGHT / 2

    def __init__(self, angle: int) -> None:
        self.pos_x:  float = self.START_POSITION_X
        self.pos_y: float = self.START_POSITION_Y
        self.angle: int = angle
        self.speed = self.SPEED

    def reset(self) -> None:
        self.pos_x = self.START_POSITION_X
        self.pos_y = self.START_POSITION_Y
        self.angle = self.ANGLE

    def set_coords(self, x: int, y: int) -> None:
        self.pos_x = x
        self.pos_y = y

    def move(self) -> None:
        self.pos_x += self.speed * math.cos(math.radians(self.angle))
        self.pos_y += self.speed * math.sin(math.radians(self.angle))

    def is_touching_horizontal_edges(self) -> int:
        # 0 ==> not touching lateral edges
        # 1 ==> touching left edge
        # 2 ==> touching right edge
        if self.__is_touching_left_edge():
            return 1
        elif self.__is_touching_right_edge():
            return 2
        else:
            return 0

    def __is_touching_left_edge(self) -> bool:
        return self.pos_x - self.RADIUS <= Paddle.WIDTH

    def __is_touching_right_edge(self) -> bool:
        return self.pos_x + self.RADIUS >= Window.WIDTH - Paddle.WIDTH

    def is_touching_vertical_edges(self) -> bool:
        # 0 ==> not touching vertical edges
        # 1 ==> touching up edge
        # 2 ==> touching bottom edge
        if self.__is_touching_up_edge():
            self.pos_y = self.RADIUS + 1
            return 1
        elif self.__is_touching_bottom_edge():
            self.pos_y = Window.HEIGHT - self.RADIUS - 1
            return 2
        else:
            return 0

    def __is_touching_up_edge(self) -> bool:
        return self.pos_y - self.RADIUS <= 0

    def __is_touching_bottom_edge(self) -> bool:
        return self.pos_y + self.RADIUS >= Window.HEIGHT

    def bounce(self, psx: Paddle, pdx: Paddle) -> None:
        # if the ball is touching the paddle, bounce it
        if psx.pos_x + psx.WIDTH >= self.pos_x - self.RADIUS and psx.pos_y + psx.HEIGHT >= self.pos_y >= psx.pos_y:

            psx_center_y = psx.pos_y + psx.HEIGHT / 2
            intersect_y = psx_center_y - (self.pos_y - self.RADIUS)
            intersect_y /= psx.HEIGHT / 2
            self.angle = -(intersect_y * self.MAX_BOUNCE_ANGLE)
            self.angle = int(self.angle)
            self.pos_x = psx.pos_x + Paddle.PADDING + self.RADIUS
        elif pdx.pos_x <= self.pos_x + self.RADIUS and pdx.pos_y + pdx.HEIGHT >= self.pos_y >= pdx.pos_y:
            # print(f'ball: {self.pos_x}, {self.pos_y}, {self.angle}, paddle: {pdx.pos_x}, {pdx.pos_y}')
            pdx_center_y = pdx.pos_y + pdx.HEIGHT / 2
            intersect_y = pdx_center_y - (self.pos_y - self.RADIUS)
            intersect_y /= pdx.HEIGHT / 2
            self.angle = -(180 - (intersect_y * self.MAX_BOUNCE_ANGLE))
            self.angle = int(self.angle)
            self.pos_x = pdx.pos_x - Paddle.PADDING - self.RADIUS

    def reverse_angle(self):
        self.angle = -self.angle


class Simulation:
    def __init__(self) -> None:
        self.ball: Ball = Ball(angle=Ball.ANGLE)
        self.paddle_left, self.paddle_right = Paddle(
            position='left'), Paddle(position='right')
        self.score_left, self.score_right = 0, 0

        self.mutex = threading.Lock()

    def simulate(self, paddle_actions: tuple[str, str]) -> None:
        with self.mutex:
            #  if ball is touching one of the vertical edges we have to change its angle
            if self.ball.is_touching_vertical_edges() != 0:
                self.ball.reverse_angle()
            elif self.ball.is_touching_horizontal_edges() == 1:
                #  left edge
                self.paddle_left.reset_position()
                self.paddle_right.reset_position()
                self.ball.reset()
                self.score_right += 1
                return 2
            elif self.ball.is_touching_horizontal_edges() == 2:
                #  right edge
                self.paddle_left.reset_position()
                self.paddle_right.reset_position()
                self.ball.reset()
                self.score_left += 1
                return 1
            self.ball.bounce(self.paddle_left, self.paddle_right)
            self.ball.move()
            if paddle_actions[0] == "1":
                self.paddle_left.move_up()
            elif paddle_actions[0] == "-1":
                self.paddle_left.move_down()
            if paddle_actions[1] == "1":
                self.paddle_right.move_up()
            elif paddle_actions[1] == "-1":
                self.paddle_right.move_down()

    def export_state(self) -> str:
        with self.mutex:
            return f'{int(self.ball.pos_x)},{int(self.ball.pos_y)},{int(self.ball.angle)},{int(self.paddle_left.pos_x)},{int(self.paddle_left.pos_y)},{int(self.paddle_right.pos_x)},{int(self.paddle_right.pos_y)},{int(self.score_left)},{int(self.score_right)}'

    def import_state(self, state: str):
        with self.mutex:
            args = state.split(',')
            self.ball.set_coords(int(args[0]), int(args[1]))
            self.ball.angle = int(args[2])
            self.paddle_left.set_coords(int(args[3]), int(args[4]))
            self.paddle_right.set_coords(int(args[5]), int(args[6]))
            self.score_left = int(args[7])
            self.score_right = int(args[8])
