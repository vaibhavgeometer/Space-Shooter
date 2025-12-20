import pygame
import random
import sys
import json
import os
from enum import Enum
from datetime import datetime, timedelta

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# High score file
HIGH_SCORE_FILE = "high_score.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5
        self.health = 100

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        play_sound("shoot")

    def take_damage(self, damage):
        self.health -= damage
        return self.health > 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 3)
        self.shoot_timer = random.randint(20, 60)

    def update(self):
        self.rect.y += self.speed
        self.shoot_timer -= 1

        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.shoot_timer = random.randint(20, 60)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 5

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Game variables
player = None
score = 0
wave = 1
enemy_spawn_timer = 0
game_state = GameState.MENU
game_start_time = None
high_score = 0
sounds = {}


def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                high_score = data.get("high_score", 0)
        except:
            high_score = 0
    else:
        high_score = 0


def load_background_music():
    """Load or generate background music"""
    global background_music
    try:
        background_music = generate_background_music()
    except:
        background_music = None


def play_background_music():
    """Start playing background music in a loop"""
    try:
        if background_music:
            background_music.set_volume(music_volume)
            background_music.play(-1)  # -1 means loop indefinitely
    except:
        pass


def stop_background_music():
    """Stop background music"""
    try:
        pygame.mixer.stop()
    except:
        pass


def save_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump({"high_score": high_score}, f)
    except:
        pass


def create_sound(frequency, duration, wave_type="sine", decay=True):
    """Create a simple sound effect programmatically"""
    try:
        sample_rate = 22050
        frames = int(sample_rate * duration)
        t = pygame.numpy.arange(frames) / sample_rate
        
        if wave_type == "sine":
            wave = pygame.numpy.sin(2 * 3.14159 * frequency * t)
        elif wave_type == "square":
            wave = pygame.numpy.sign(pygame.numpy.sin(2 * 3.14159 * frequency * t))
        else:  # triangle
            wave = 2 * pygame.numpy.abs(2 * (t * frequency - pygame.numpy.floor(t * frequency + 0.5))) - 1
        
        # Apply decay envelope
        if decay:
            envelope = pygame.numpy.exp(-3 * t)
        else:
            envelope = 1
        
        wave = wave * envelope
        wave = (wave * 32767 * 0.3).astype(pygame.numpy.int16)
        sound_array = pygame.numpy.zeros((frames, 2), dtype=pygame.numpy.int16)
        sound_array[:, 0] = wave
        sound_array[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(sound_array)
        return sound
    except:
        return None


def generate_background_music():
    """Generate light background music pattern"""
    try:
        sample_rate = 22050
        duration = 4  # 4 seconds loop
        frames = int(sample_rate * duration)
        t = pygame.numpy.arange(frames) / sample_rate
        
        # Create a simple chord progression
        freq1 = 330  # E
        freq2 = 247  # B
        freq3 = 196  # G
        
        # Mix frequencies with envelope
        wave = pygame.numpy.zeros(frames)
        
        # First section (0-1s): E chord
        mask1 = t < 1
        wave += mask1 * pygame.numpy.sin(2 * 3.14159 * freq1 * t) * 0.2
        
        # Second section (1-2s): B note
        mask2 = (t >= 1) & (t < 2)
        wave += mask2 * pygame.numpy.sin(2 * 3.14159 * freq2 * t) * 0.2
        
        # Third section (2-3s): G note
        mask3 = (t >= 2) & (t < 3)
        wave += mask3 * pygame.numpy.sin(2 * 3.14159 * freq3 * t) * 0.2
        
        # Fourth section (3-4s): E note
        mask4 = t >= 3
        wave += mask4 * pygame.numpy.sin(2 * 3.14159 * freq1 * t) * 0.2
        
        # Apply smooth envelope
        envelope = pygame.numpy.ones(frames) * 0.5
        wave = wave * envelope
        wave = (wave * 32767).astype(pygame.numpy.int16)
        
        sound_array = pygame.numpy.zeros((frames, 2), dtype=pygame.numpy.int16)
        sound_array[:, 0] = wave
        sound_array[:, 1] = wave
        
        music = pygame.sndarray.make_sound(sound_array)
        return music
    except:
        return None


def play_sound(sound_type):
    """Play sound effects"""
    try:
        if sound_type == "shoot":
            sound = create_sound(600, 0.08, "square", True)
            if sound:
                sound.play()
        elif sound_type == "explosion":
            sound = create_sound(150, 0.25, "triangle", True)
            if sound:
                sound.play()
        elif sound_type == "powerup":
            # Play a two-tone powerup sound
            sound1 = create_sound(800, 0.1, "sine", False)
            sound2 = create_sound(1000, 0.1, "sine", False)
            if sound1:
                sound1.play()
        elif sound_type == "gameover":
            # Descending tone
            sound = create_sound(150, 0.6, "sine", True)
            if sound:
                sound.play()
    except:
        pass  # Silently fail if sound system has issues


# Game variables
player = None
score = 0
wave = 1
enemy_spawn_timer = 0
game_state = GameState.MENU
game_start_time = None
high_score = 0
background_music = None
music_volume = 0.3


def start_game():
    global player, score, wave, enemy_spawn_timer, game_state, all_sprites, enemies, bullets, enemy_bullets, powerups, game_start_time
    
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
    all_sprites.add(player)
    
    score = 0
    wave = 1
    enemy_spawn_timer = 0
    game_state = GameState.PLAYING
    game_start_time = datetime.now()
    play_background_music()


def draw_menu():
    screen.fill(BLACK)
    title = big_font.render("SPACE SHOOTER", True, GREEN)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title, title_rect)
    
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
    screen.blit(high_score_text, high_score_rect)
    
    instruction1 = font.render("Press SPACE to Start", True, WHITE)
    instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH // 2, 280))
    screen.blit(instruction1, instruction1_rect)
    
    instruction2 = font.render("Arrow Keys to Move", True, WHITE)
    instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH // 2, 350))
    screen.blit(instruction2, instruction2_rect)
    
    instruction3 = font.render("Z to Shoot", True, WHITE)
    instruction3_rect = instruction3.get_rect(center=(SCREEN_WIDTH // 2, 420))
    screen.blit(instruction3, instruction3_rect)


def draw_game():
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Calculate elapsed time
    elapsed_time = (datetime.now() - game_start_time).total_seconds()
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    # Draw HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    timer_text = font.render(f"Time: {minutes}:{seconds:02d}", True, WHITE)
    screen.blit(timer_text, (10, 50))
    
    high_score_display = font.render(f"Best: {high_score}", True, YELLOW)
    screen.blit(high_score_display, (10, 90))
    
    health_text = font.render(f"Health: {player.health}", True, GREEN if player.health > 50 else RED)
    screen.blit(health_text, (SCREEN_WIDTH - 250, 10))
    
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    screen.blit(wave_text, (SCREEN_WIDTH // 2 - 50, 10))


def draw_game_over():
    global high_score
    
    # Update high score if current score is better
    if score > high_score:
        high_score = score
        save_high_score()
    
    elapsed_time = (datetime.now() - game_start_time).total_seconds()
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    screen.fill(BLACK)
    game_over_text = big_font.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
    screen.blit(game_over_text, game_over_rect)
    
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(final_score_text, final_score_rect)
    
    final_time_text = font.render(f"Time Survived: {minutes}:{seconds:02d}", True, WHITE)
    final_time_rect = final_time_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
    screen.blit(final_time_text, final_time_rect)
    
    final_wave_text = font.render(f"Waves Survived: {wave}", True, WHITE)
    final_wave_rect = final_wave_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
    screen.blit(final_wave_text, final_wave_rect)
    
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
    screen.blit(high_score_text, high_score_rect)
    
    restart_text = font.render("Press SPACE to Return to Menu", True, GREEN)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 480))
    screen.blit(restart_text, restart_rect)
    
    play_sound("gameover")


def update_game():
    global score, wave, enemy_spawn_timer, game_state
    
    all_sprites.update()
    
    # Spawn enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer > max(20, 60 - wave * 5):
        enemy = Enemy(random.randint(40, SCREEN_WIDTH - 40), -40)
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_timer = 0
    
    # Enemy shooting
    for enemy in enemies:
        enemy.shoot()
    
    # Check bullet-enemy collisions
    collisions = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for collision in collisions:
        score += 10
        play_sound("explosion")
        
        # Spawn powerup randomly
        if random.random() < 0.3:
            powerup = PowerUp(collision.rect.centerx, collision.rect.centery, "health")
            all_sprites.add(powerup)
            powerups.add(powerup)
    
    # Check player-powerup collisions
    powerup_collisions = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in powerup_collisions:
        player.health = min(100, player.health + 25)
        play_sound("powerup")
    
    # Check player-enemy_bullet collisions
    enemy_bullet_collisions = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for bullet in enemy_bullet_collisions:
        if not player.take_damage(10):
            game_state = GameState.GAME_OVER
    
    # Check player-enemy collisions
    enemy_collisions = pygame.sprite.spritecollide(player, enemies, True)
    for enemy in enemy_collisions:
        if not player.take_damage(20):
            game_state = GameState.GAME_OVER
    
    # Wave progression
    if len(enemies) == 0 and enemy_spawn_timer > 30:
        wave += 1
        enemy_spawn_timer = 0


# Main game loop
load_high_score()
load_background_music()
play_background_music()
running = True
game_over_sound_played = False

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == GameState.MENU:
                    start_game()
                    game_over_sound_played = False
                elif game_state == GameState.GAME_OVER:
                    game_state = GameState.MENU
                    game_over_sound_played = False
            if event.key == pygame.K_z and game_state == GameState.PLAYING:
                player.shoot()
    
    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.PLAYING:
        update_game()
        draw_game()
    elif game_state == GameState.GAME_OVER:
        if not game_over_sound_played:
            draw_game_over()
            game_over_sound_played = True
        else:
            draw_game_over()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
