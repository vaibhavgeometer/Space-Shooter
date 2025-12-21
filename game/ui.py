import pygame
from .constants import *
from . import globals
from .audio import play_sound, change_volume
from .core import start_game
from .data import change_difficulty

# --- UI Components ---
class Button:
    def __init__(self, text, x, y, width, height, action, text_color=WHITE, bg_color=DARK_UI, border_color=NEON_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.hover_color = tuple(min(c + 50, 255) for c in bg_color)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        color = self.hover_color if is_hovered else self.bg_color
        
        # Draw button body
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)
        
        # Draw text
        # Assuming fonts are initialized in globals
        txt_surf = globals.font_md.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)
        
        return is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                play_sound("shoot") # UI click sound
                self.action()
                return True
        return False

# --- Actions ---
def action_play():
    start_game()

def action_settings():
    globals.game_state = GameState.SETTINGS

def action_stats():
    globals.game_state = GameState.STATS

def action_quit():
    globals.should_quit = True

def action_back():
    globals.game_state = GameState.MENU

# --- Button Initialization ---
def init_menu_buttons():
    globals.buttons = [
        Button("PLAY", SCREEN_WIDTH//2 - 100, 300, 200, 50, action_play, NEON_GREEN),
        Button("SETTINGS", SCREEN_WIDTH//2 - 100, 370, 200, 50, action_settings, NEON_BLUE),
        Button("STATS", SCREEN_WIDTH//2 - 100, 440, 200, 50, action_stats, NEON_PURPLE),
        Button("QUIT", SCREEN_WIDTH//2 - 100, 510, 200, 50, action_quit, NEON_RED)
    ]

def init_settings_buttons():
    globals.settings_buttons = [
        # Volume
        Button("+", 560, 225, 50, 50, lambda: change_volume(0.1), NEON_GREEN, DARK_UI),
        Button("-", 190, 225, 50, 50, lambda: change_volume(-0.1), NEON_RED, DARK_UI),
        
        # Difficulty
        Button(">", 560, 375, 50, 50, lambda: change_difficulty(1), NEON_GREEN, DARK_UI),
        Button("<", 190, 375, 50, 50, lambda: change_difficulty(-1), NEON_RED, DARK_UI),
        
        Button("BACK", SCREEN_WIDTH//2 - 100, 500, 200, 50, action_back, WHITE)
    ]

def init_stats_buttons():
    globals.stats_buttons = [
        Button("BACK", SCREEN_WIDTH//2 - 100, 500, 200, 50, action_back, WHITE)
    ]

def init_pause_buttons():
    globals.pause_buttons = [
        Button("MAIN MENU", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50, action_back, NEON_BLUE)
    ]

def init_game_over_buttons():
    globals.game_over_buttons = [
        Button("MAIN MENU", SCREEN_WIDTH//2 - 100, 480, 200, 50, action_back, NEON_BLUE)
    ]

# --- Drawing Functions ---
def draw_ui_panel(surface, rect, color=DARK_UI, border=NEON_BLUE):
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(temp, (*color, 200), (0,0,rect.width, rect.height), border_radius=10)
    pygame.draw.rect(temp, border, (0,0,rect.width, rect.height), 2, border_radius=10)
    surface.blit(temp, rect)

def draw_hud(screen):
    # Top Bar Panel
    panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
    draw_ui_panel(screen, panel_rect, (10, 10, 15), (50, 50, 100))
    
    # Score
    score_txt = globals.font_md.render(f"SCORE: {globals.score:06d}", True, WHITE)
    screen.blit(score_txt, (20, 15))
    
    # Timer
    mins = int(globals.game_time // 60)
    secs = int(globals.game_time % 60)
    time_str = f"{mins:02d}:{secs:02d}"
    
    # Timer Box
    timer_surf = globals.font_md.render(time_str, True, NEON_YELLOW)
    timer_rect = timer_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
    screen.blit(timer_surf, timer_rect)
    
    # Health Bar
    bar_width = 200
    bar_height = 20
    x, y = SCREEN_WIDTH - 220, 20
    
    pygame.draw.rect(screen, WHITE, (x-2, y-2, bar_width+4, bar_height+4), 2)
    pygame.draw.rect(screen, (50, 0, 0), (x, y, bar_width, bar_height))
    
    if globals.player:
        health_pct = max(0, globals.player.health / globals.player.max_health)
        fill_width = int(bar_width * health_pct)
        fill_color = NEON_GREEN if health_pct > 0.5 else (NEON_RED if health_pct < 0.25 else NEON_ORANGE)
        pygame.draw.rect(screen, fill_color, (x, y, fill_width, bar_height))
    
    # Wave
    wave_txt = globals.font_sm.render(f"WAVE {globals.wave}", True, NEON_BLUE)
    screen.blit(wave_txt, (SCREEN_WIDTH//2 - 30, 65))

def draw_menu(screen):
    screen.fill(BLACK)
    # Animated background
    for star in globals.stars:
        star.update(0.5)
        star.draw(screen)
        
    # Title
    title = globals.font_xl.render("NEON SHOOTER", True, NEON_BLUE)
    t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
    for offset in range(3, 0, -1):
        glow = globals.font_xl.render("NEON SHOOTER", True, (0, 100, 255))
        glow.set_alpha(50)
        screen.blit(glow, (t_rect.x - offset, t_rect.y))
        screen.blit(glow, (t_rect.x + offset, t_rect.y))
    screen.blit(title, t_rect)
    
    # Buttons
    for btn in globals.buttons:
        btn.draw(screen)

    # Footer
    version = globals.font_sm.render("v1.3", True, (50, 50, 60))
    screen.blit(version, (10, SCREEN_HEIGHT - 30))

def draw_settings(screen):
    screen.fill(BLACK)
    for star in globals.stars: star.draw(screen)
    
    title = globals.font_lg.render("SETTINGS", True, NEON_BLUE)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))
    
    # Volume Control
    vol_text = globals.font_md.render(f"MUSIC VOLUME: {int(globals.music_volume * 100)}%", True, WHITE)
    screen.blit(vol_text, vol_text.get_rect(center=(SCREEN_WIDTH//2, 200)))
    
    bar_w, bar_h = 300, 20
    pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH//2 - 150, 240, bar_w, bar_h))
    pygame.draw.rect(screen, NEON_GREEN, (SCREEN_WIDTH//2 - 150, 240, int(bar_w * globals.music_volume), bar_h))
    
    # Difficulty Control
    diff_name, _ = DIFFICULTY_PARAMS[globals.current_difficulty]
    diff_colors = {
        Difficulty.EASY: NEON_GREEN,
        Difficulty.NORMAL: NEON_BLUE,
        Difficulty.HARD: NEON_PURPLE,
        Difficulty.EXTREME: NEON_ORANGE,
        Difficulty.NIGHTMARE: NEON_RED
    }
    diff_col = diff_colors.get(globals.current_difficulty, WHITE)
    diff_label = globals.font_md.render("DIFFICULTY", True, WHITE)
    screen.blit(diff_label, diff_label.get_rect(center=(SCREEN_WIDTH//2, 350)))
    
    diff_txt = globals.font_lg.render(diff_name, True, diff_col)
    screen.blit(diff_txt, diff_txt.get_rect(center=(SCREEN_WIDTH//2, 400)))
    
    for btn in globals.settings_buttons:
        btn.draw(screen)

def draw_stats(screen):
    screen.fill(BLACK)
    for star in globals.stars: star.draw(screen)
    
    title = globals.font_lg.render("STATISTICS", True, NEON_PURPLE)
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))
    
    headers_y = 160
    h1 = globals.font_md.render("DIFFICULTY", True, NEON_BLUE)
    h2 = globals.font_md.render("HIGH SCORE", True, NEON_BLUE)
    h3 = globals.font_md.render("GAMES", True, NEON_BLUE)
    
    screen.blit(h1, h1.get_rect(center=(200, headers_y)))
    screen.blit(h2, h2.get_rect(center=(450, headers_y)))
    screen.blit(h3, h3.get_rect(center=(650, headers_y)))
    
    pygame.draw.line(screen, NEON_BLUE, (50, headers_y + 30), (750, headers_y + 30), 2)
    
    start_y = 220
    row_height = 50
    
    diff_colors = {
        "EASY": NEON_GREEN,
        "NORMAL": NEON_BLUE,
        "HARD": NEON_PURPLE,
        "EXTREME": NEON_ORANGE,
        "NIGHTMARE": NEON_RED
    }
    
    total_games = 0
    
    for i, diff in enumerate(Difficulty):
        name = diff.name
        data = globals.game_data.get(name, {"high_score": 0, "games_played": 0})
        
        c = diff_colors.get(name, WHITE)
        
        t1 = globals.font_md.render(name, True, c)
        screen.blit(t1, t1.get_rect(center=(200, start_y + i * row_height)))
        
        score_val = data["high_score"]
        t2 = globals.font_md.render(f"{score_val:06d}", True, WHITE)
        screen.blit(t2, t2.get_rect(center=(450, start_y + i * row_height)))
        
        games_val = data["games_played"]
        total_games += games_val
        t3 = globals.font_md.render(str(games_val), True, WHITE)
        screen.blit(t3, t3.get_rect(center=(650, start_y + i * row_height)))

    footer_y = start_y + 5 * row_height + 20
    t_total = globals.font_md.render(f"TOTAL GAMES PLAYED: {total_games}", True, NEON_YELLOW)
    screen.blit(t_total, t_total.get_rect(center=(SCREEN_WIDTH//2, footer_y)))
        
    for btn in globals.stats_buttons:
        btn.draw(screen)

def draw_pause(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,150))
    screen.blit(overlay, (0,0))
    
    txt = globals.font_lg.render("PAUSED", True, WHITE)
    screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
    
    for btn in globals.pause_buttons:
        btn.draw(screen)

def draw_game_over(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0,0))
    
    over_txt = globals.font_xl.render("MISSION FAILED", True, NEON_RED)
    screen.blit(over_txt, over_txt.get_rect(center=(SCREEN_WIDTH//2, 200)))
    
    score_txt = globals.font_md.render(f"FINAL SCORE: {globals.score}", True, WHITE)
    screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH//2, 300)))
    
    restart_txt = globals.font_md.render("PRESS R TO RETRY", True, NEON_GREEN)
    screen.blit(restart_txt, restart_txt.get_rect(center=(SCREEN_WIDTH//2, 400)))

    for btn in globals.game_over_buttons:
        btn.draw(screen)
