import pygame
from .constants import Difficulty, GameState

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
particles = pygame.sprite.Group()

# Game State Variables
player = None
score = 0
wave = 1
high_score = 0
games_played = 0
enemy_spawn_timer = 0
game_state = GameState.MENU
game_time = 0.0
last_frame_time = 0
# Management Data
game_data = {}
current_difficulty = Difficulty.NORMAL

# Audio
sounds = {}
background_music = None
music_volume = 0.3
sfx_volume = 0.3

# UI
buttons = []
settings_buttons = []
stats_buttons = []
pause_buttons = []
game_over_buttons = []
controls_buttons = []

# Background
stars = []

# Control
should_quit = False

# Fonts (Initialized later)
font_sm = None
font_md = None
font_lg = None
font_xl = None

# Screen Shake
shake_offset = [0, 0]
shake_intensity = 0

def init_fonts():
    global font_sm, font_md, font_lg, font_xl
    try:
        FONT_NAME = pygame.font.match_font('consolas', 'couriernew', 'monospace')
    except:
        FONT_NAME = None
    
    font_sm = pygame.font.Font(FONT_NAME, 20)
    font_md = pygame.font.Font(FONT_NAME, 32)
    font_lg = pygame.font.Font(FONT_NAME, 64)
    font_xl = pygame.font.Font(FONT_NAME, 96)
