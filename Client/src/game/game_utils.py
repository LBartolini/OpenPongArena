import pygame


class Utils:
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600


class ColorPalette:
    WHITE: tuple[int, int, int] = (255, 255, 255)
    BLACK: tuple[int, int, int] = (0, 0, 0)


class Paddle:
    HEIGHT: int = 100
    WIDTH: int = 10
    SPEED: int = 10
    COLOR: tuple[int, int, int] = ColorPalette.WHITE

    START_POSITION_X: int = WIDTH
    START_POSITION_Y: int | float = (Utils.WINDOW_HEIGHT - HEIGHT) / 2

    def __init__(self) -> None:
        self.pos_x: int = self.START_POSITION_X
        self.pos_y: float = self.START_POSITION_Y
        self.color: tuple[int, int, int] = self.COLOR
        self.rect: pygame.Rect = pygame.Rect(
            self.pos_x, self.pos_y, self.WIDTH, self.HEIGHT)

    def move_up(self) -> None:
        self.pos_y -= self.SPEED
        self.rect.y = self.pos_y

    def move_down(self) -> None:
        self.pos_y += self.SPEED
        self.rect.y = self.pos_y

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.COLOR, self.rect)

    def reset_position(self) -> None:
        self.pos_x = self.START_POSITION_X
        self.pos_y = self.START_POSITION_Y
        self.rect = pygame.Rect(self.pos_x, self.pos_y,
                                self.WIDTH, self.HEIGHT)

    def get_position(self) -> tuple[int, int]:
        return self.pos_x, self.pos_y
