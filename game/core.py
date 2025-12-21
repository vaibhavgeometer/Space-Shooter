
import pygame
import random
from .constants import *
from . import globals
from .entities import Player, Enemy, PowerUp
from .particles import create_explosion
from .audio import play_sound
from .data import save_game_data
from .utils import update_shake, add_shake

def start_game():
    globals.all_sprites.empty()
    globals.enemies.empty()
    globals.bullets.empty()
    globals.enemy_bullets.empty()
    globals.powerups.empty()
    globals.particles.empty()
    
    globals.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
    globals.all_sprites.add(globals.player)
    
    globals.score = 0
    globals.wave = 1
    globals.enemy_spawn_timer = 0
    globals.game_state = GameState.PLAYING
    globals.game_time = 0.0
    globals.last_frame_time = pygame.time.get_ticks()
    
    play_sound("wave")

def update_game_logic():
    current_time = pygame.time.get_ticks()
    dt = (current_time - globals.last_frame_time) / 1000.0
    globals.last_frame_time = current_time
    globals.game_time += dt
    
    update_shake()
    
    # Difficulty scaling
    diff_mult = DIFFICULTY_PARAMS[globals.current_difficulty][1]
    
    if globals.game_time < 120:
        base_diff = 1.0 + (globals.game_time / 60.0)
    else:
        base_diff = 3.0 + ((globals.game_time - 120) / 30.0)
    
    difficulty = base_diff * diff_mult
        
    globals.all_sprites.update()
    
    # Spawning
    globals.enemy_spawn_timer += 1
    spawn_rate = max(15, int(60 / (difficulty * 0.8)))
    
    if globals.enemy_spawn_timer > spawn_rate:
        e = Enemy(random.randint(40, SCREEN_WIDTH-40), -50, difficulty)
        globals.all_sprites.add(e)
        globals.enemies.add(e)
        globals.enemy_spawn_timer = 0
        
    for enemy in globals.enemies:
        enemy.shoot()
        
    # Collisions
    # Bullet -> Enemy
    hits = pygame.sprite.groupcollide(globals.enemies, globals.bullets, False, True) # Enemy, Bullet, KillE?, KillB?
    for enemy, hit_bullets in hits.items():
        # Using hit points
        enemy.hp -= len(hit_bullets)
        if enemy.hp <= 0:
            globals.score += 1 * (3 if enemy.type=="elite" else 1)
            create_explosion(enemy.rect.centerx, enemy.rect.centery, enemy.color)
            play_sound("explosion")
            enemy.kill()
            
            # Powerup
            if random.random() < 0.25:
                p = PowerUp(enemy.rect.centerx, enemy.rect.centery, "heal")
                globals.all_sprites.add(p)
                globals.powerups.add(p)
        else:
            play_sound("hit")
            
    # Player -> Enemy/Bullet
    if globals.player and pygame.sprite.spritecollide(globals.player, globals.enemies, True):
        play_sound("explosion")
        create_explosion(globals.player.rect.centerx, globals.player.rect.centery, NEON_RED)
        if not globals.player.take_damage(20):
            globals.game_state = GameState.GAME_OVER
            save_game_data()
            play_sound("gameover")
            
    hits = pygame.sprite.spritecollide(globals.player, globals.enemy_bullets, True)
    if hits:
        play_sound("hit")
        if not globals.player.take_damage(10 * len(hits)):
            globals.game_state = GameState.GAME_OVER
            save_game_data()
            play_sound("gameover")

    # Powerups
    hits = pygame.sprite.spritecollide(globals.player, globals.powerups, True)
    for p in hits:
        globals.player.health = min(globals.player.max_health, globals.player.health + 30)
        play_sound("powerup")
        
    # Wave Manager
    if int(globals.game_time) // 30 > globals.wave:
        globals.wave += 1
        play_sound("wave")
