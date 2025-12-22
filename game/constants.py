import pygame
from enum import Enum

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game Version
VERSION = "v1"

# Colors (Neon/Cyberpunk Palette)
BLACK = (10, 10, 18)
WHITE = (255, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 20, 60)
NEON_BLUE = (20, 200, 255)
NEON_YELLOW = (255, 230, 20)
NEON_ORANGE = (255, 140, 20)
NEON_PURPLE = (180, 20, 255)
DARK_UI = (20, 25, 40)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SETTINGS = 5
    STATS = 6
    CONTROLS = 7

class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXTREME = 4
    NIGHTMARE = 5

DIFFICULTY_PARAMS = {
    Difficulty.EASY: ("EASY", 0.7),
    Difficulty.NORMAL: ("NORMAL", 1.0),
    Difficulty.HARD: ("HARD", 1.5),
    Difficulty.EXTREME: ("EXTREME", 2.0),
    Difficulty.NIGHTMARE: ("NIGHTMARE", 3.0)
}
