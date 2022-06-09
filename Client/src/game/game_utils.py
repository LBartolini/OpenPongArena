import pygame


class Window:
    WIDTH, HEIGHT = 800, 600
    RESOLUTION = (WIDTH, HEIGHT)


class Game:
    FPS = 72


class ColorPalette:
    WHITE: tuple[int, int, int] = (255, 255, 255)
    BLACK: tuple[int, int, int] = (0, 0, 0)


class Paddle:
    HEIGHT: int = 100
    WIDTH: int = 10
    SPEED: int = 10
    COLOR: tuple[int, int, int] = ColorPalette.WHITE

    START_POSITION_X: int = WIDTH
    START_POSITION_Y: int | float = (Window.HEIGHT - HEIGHT) / 2

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
