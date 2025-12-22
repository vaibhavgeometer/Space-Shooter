import pygame
import sys
import os
import random

# Initialize Pygame before importing modules that might use it
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# Import game packages
from game.constants import *
from game import globals
from game.entities import Star
from game import audio
from game import data
from game import core
from game import ui

# Helper function to find resources (works for dev & PyInstaller)
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # Setup Screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    try:
        # Load icon using resource_path to ensure it works in exe
        icon_path = resource_path("game/Icon.png")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Warning: Could not load icon: {e}")

    pygame.display.set_caption("Space Shooter")
    clock = pygame.time.Clock()

    # Initialization
    globals.init_fonts()
    data.load_game_data()
    audio.load_all_sounds()
    audio.play_background_music()
    
    # Init UI
    ui.init_menu_buttons()
    ui.init_settings_buttons()
    ui.init_stats_buttons()
    ui.init_pause_buttons()
    ui.init_game_over_buttons()
    
    # Init Background
    globals.stars = [Star() for _ in range(100)]
    
    globals.last_frame_time = pygame.time.get_ticks()
    
    running = True
    while running:
        clock.tick(60)
        
        # Check global quit flag from UI actions
        if globals.should_quit:
            running = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Global Keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                   if globals.game_state == GameState.PLAYING:
                       globals.game_state = GameState.PAUSED
                   elif globals.game_state == GameState.PAUSED:
                       globals.game_state = GameState.PLAYING
                       globals.last_frame_time = pygame.time.get_ticks()

                # Retry from Game Over
                if event.key == pygame.K_r and globals.game_state == GameState.GAME_OVER:
                    core.start_game()
            
            # Menu Interactions
            if globals.game_state == GameState.MENU:
                for btn in globals.buttons:
                    btn.handle_event(event)

            elif globals.game_state == GameState.SETTINGS:
                for btn in globals.settings_buttons:
                    btn.handle_event(event)
                    
            elif globals.game_state == GameState.STATS:
                for btn in globals.stats_buttons:
                    btn.handle_event(event)

            elif globals.game_state == GameState.PAUSED:
                for btn in globals.pause_buttons:
                    btn.handle_event(event)

            elif globals.game_state == GameState.GAME_OVER:
                for btn in globals.game_over_buttons:
                    btn.handle_event(event)
                    
            # Player Input
            elif globals.game_state == GameState.PLAYING:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                     if globals.player:
                        globals.player.shoot()

        # Drawing and Updates
        screen.fill(BLACK)
        
        # Shake offset
        sx, sy = int(globals.shake_offset[0]), int(globals.shake_offset[1])
        
        if globals.game_state == GameState.MENU:
            ui.draw_menu(screen)
        elif globals.game_state == GameState.SETTINGS:
            ui.draw_settings(screen)
        elif globals.game_state == GameState.STATS:
            ui.draw_stats(screen)
        elif globals.game_state == GameState.PLAYING:
            # Draw Background
            for s in globals.stars:
                s.draw(screen)
            
            core.update_game_logic()
            
            for sprite in globals.all_sprites:
                screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))
                
            ui.draw_hud(screen)
            
        elif globals.game_state == GameState.PAUSED:
            for s in globals.stars: s.draw(screen)
            globals.all_sprites.draw(screen)
            ui.draw_hud(screen)
            ui.draw_pause(screen)

        elif globals.game_state == GameState.GAME_OVER:
            for s in globals.stars: s.draw(screen)
            globals.all_sprites.draw(screen)
            ui.draw_game_over(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
