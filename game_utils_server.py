import pygame
import math


class Utils:
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


class ColorPalette:
    WHITE: tuple[int, int, int] = (255, 255, 255)
    BLACK: tuple[int, int, int] = (0, 0, 0)


class Ball:
    RADIUS: int = 5
    SPEED: int = 5
    COLOR: tuple[int, int, int] = ColorPalette.WHITE
    ANGLE: int = 0  # default start angle (0 <= angle <= 360)

    START_POSITION_X: int | float = (Utils.WINDOW_WIDTH - RADIUS) / 2
    START_POSITION_Y: int | float = (Utils.WINDOW_HEIGHT - RADIUS) / 2

    def __init__(self, angle: int) -> None:
        self.pos_x: int | float = self.START_POSITION_X
        self.pos_y: int | float = self.START_POSITION_Y
        self.color: tuple[int, int, int] = self.COLOR
        self.angle: int = angle
        self.rect: pygame.Rect = pygame.Rect(
            self.pos_x, self.pos_y, self.RADIUS, self.RADIUS)

    def set_coords(self, x: int, y: int) -> None:
        self.pos_x = x
        self.pos_y = y
        self.rect = pygame.Rect(
            self.pos_x, self.pos_y, self.RADIUS, self.RADIUS)

    def move(self) -> None:
        self.pos_x += self.SPEED * math.cos(math.radians(self.angle))
        self.pos_y += self.SPEED * math.sin(math.radians(self.angle))
        self.rect = pygame.Rect(
            self.pos_x, self.pos_y, self.RADIUS, self.RADIUS)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface=surface, color=self.COLOR, center=(
            self.pos_x, self.pos_y), radius=self.RADIUS)

    def is_touching_edge(self) -> int:
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
        return self.pos_x - self.RADIUS <= 0

    def __is_touching_right_edge(self) -> bool:
        return self.pos_x + self.RADIUS >= Utils.WINDOW_WIDTH

    def bounce(self):
        # TODO: New angle calculation formula
        pass
