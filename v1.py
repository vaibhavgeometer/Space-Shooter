import pygame
import random
import sys
import json
import os
import math
import numpy as np
from enum import Enum
from datetime import datetime, timedelta

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# High score file
HIGH_SCORE_FILE = "high_score.json"

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

# Fonts
try:
    # Try to find a monospace font
    FONT_NAME = pygame.font.match_font('consolas', 'couriernew', 'monospace')
except:
    FONT_NAME = None

font_sm = pygame.font.Font(FONT_NAME, 20)
font_md = pygame.font.Font(FONT_NAME, 32)
font_lg = pygame.font.Font(FONT_NAME, 64)
font_xl = pygame.font.Font(FONT_NAME, 96)

# Screen Shake
shake_offset = [0, 0]
shake_intensity = 0

def add_shake(amount):
    global shake_intensity
    shake_intensity = min(shake_intensity + amount, 25)

def update_shake():
    global shake_intensity, shake_offset
    if shake_intensity > 0:
        shake_intensity *= 0.9
        angle = random.uniform(0, math.pi * 2)
        offset = shake_intensity # radius
        shake_offset[0] = math.cos(angle) * offset
        shake_offset[1] = math.sin(angle) * offset
        if shake_intensity < 0.5:
            shake_intensity = 0
            shake_offset = [0, 0]
    else:
        shake_offset = [0, 0]

# --- Entities ---

class Star:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, SCREEN_HEIGHT) # Start sparsely populated

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -10
        self.z = random.uniform(0.5, 3.0) # Depth/Speed factor
        self.size = random.uniform(1, 3)
        self.brightness = random.randint(100, 255)

    def update(self, speed_mult=1.0):
        self.y += (1 + self.z) * speed_mult
        if self.y > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        # Parallax blending
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size / 2))

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed_range=(2, 6), life_range=(20, 40), size_range=(2,6)):
        super().__init__()
        self.color = color
        self.size = random.randint(*size_range)
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(*life_range)
        self.original_life = self.life

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vx *= 0.95 # Drag
        self.vy *= 0.95
        self.life -= 1
        
        if self.life <= 0:
            self.kill()
        else:
            # Re-draw with alpha
            alpha = int(255 * (self.life / self.original_life))
            self.image.fill((0,0,0,0)) # Clear
            
            # Glow effect
            rgb = self.color[:3]
            pygame.draw.circle(self.image, (*rgb, alpha), (self.size, self.size), self.size)

class TrailParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.life = 15
        self.original_life = 15
        self.vy = random.uniform(1, 3)
        self.vx = random.uniform(-0.5, 0.5)

    def update(self):
        self.rect.y += self.vy
        self.rect.x += self.vx
        self.life -= 1
        if self.life <= 0:
            self.kill()
        
        alpha = int(200 * (self.life / self.original_life))
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*self.color, alpha), (3, 3), 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Size for collision
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 6
        self.health = 100
        self.max_health = 100
        self.last_shot = 0
        self.shoot_delay = 180 
        self.tilt = 0 # For visual banking logic

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            dx = -1
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            dx = 1
        
        self.rect.x += dx * self.speed
        
        # Tilt effect
        target_tilt = dx * -15
        self.tilt = self.tilt * 0.8 + target_tilt * 0.2
        
        # Engine trails
        if random.random() < 0.8:
            offset_x = random.randint(-5, 5)
            p = TrailParticle(self.rect.centerx + offset_x, self.rect.bottom - 5, NEON_BLUE)
            all_sprites.add(p)
            particles.add(p)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            bullet_left = Bullet(self.rect.centerx - 10, self.rect.top + 10)
            bullet_right = Bullet(self.rect.centerx + 10, self.rect.top + 10)
            all_sprites.add(bullet_left, bullet_right)
            bullets.add(bullet_left, bullet_right)
            play_sound("shoot")
            self.last_shot = now
            add_shake(2)

    def take_damage(self, damage):
        self.health -= damage
        add_shake(10)
        return self.health > 0

    def draw(self, surface):
        # Calculate polygon points based on tilt
        cx, cy = self.rect.centerx, self.rect.centery
        w, h = self.width, self.height
        
        # Standard sprite groups use .image property. Let's update .image
        self.image.fill((0,0,0,0))
        
        # Local coordinates for image
        w, h = self.width, self.height
        local_points = [
            (w/2, 0),
            (0, h),
            (w/2, h*0.8),
            (w, h)
        ]

        # Draw ship body
        pygame.draw.polygon(self.image, NEON_GREEN, local_points)
        pygame.draw.polygon(self.image, WHITE, local_points, 2) # Outline
        
        # Cockpit
        pygame.draw.circle(self.image, NEON_BLUE, (int(w//2), int(h//2)), 6)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, difficulty=1.0):
        super().__init__()
        self.width = 44
        self.height = 40
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.difficulty = difficulty
        self.speed = random.uniform(1.5, 3.5) * (1 + (difficulty - 1) * 0.3)
        self.shoot_timer = random.randint(30, 80)
        self.angle = 0
        self.rot_speed = random.uniform(-2, 2)
        
        # Determine Type/Color
        if difficulty > 2.5 and random.random() < 0.3:
            self.type = "elite"
            self.color = NEON_PURPLE
            self.hp = 3
        else:
            self.type = "normal"
            self.color = NEON_RED if  random.random() < 0.5 else NEON_ORANGE
            self.hp = 1
            
        self.draw_enemy()

    def draw_enemy(self):
        w, h = self.width, self.height
        self.image.fill((0,0,0,0))
        
        if self.type == "elite":
            # Hexagon
            points = [
                (w//2, 0), (w, h*0.3), (w, h*0.7),
                (w//2, h), (0, h*0.7), (0, h*0.3)
            ]
            pygame.draw.polygon(self.image, self.color, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
        else:
            # Invader shape (roughly)
            rects = [
                (w*0.2, 0, w*0.6, h*0.4),
                (0, h*0.4, w, h*0.3),
                (w*0.2, h*0.7, w*0.1, h*0.3),
                (w*0.7, h*0.7, w*0.1, h*0.3)
            ]
            for r in rects:
                pygame.draw.rect(self.image, self.color, r)
            
            # Eyes
            eye_color = NEON_YELLOW
            pygame.draw.rect(self.image, eye_color, (w*0.3, h*0.4, 6, 6))
            pygame.draw.rect(self.image, eye_color, (w*0.7-6, h*0.4, 6, 6))

    def update(self):
        self.rect.y += self.speed
        
        # Wiggle motion
        self.rect.x += math.sin(pygame.time.get_ticks() / 200.0 + self.rect.y) * 2
        
        self.shoot_timer -= 1
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet_speed = 6 + (self.difficulty - 1) * 1.5
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, bullet_speed, self.color)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            
            base_rate = 60 if self.type == "normal" else 40
            self.shoot_timer = random.randint(max(20, int(base_rate / self.difficulty)), max(40, int(base_rate*2 / self.difficulty)))
            play_sound("enemy_shoot")

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        # Glowing effect drawn on surface
        color = NEON_YELLOW
        # Core
        pygame.draw.rect(self.image, WHITE, (2, 5, 4, 10))
        # Glow
        pygame.draw.rect(self.image, (*color, 100), (0, 0, 8, 20), border_radius=4)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -12

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=5, color=NEON_RED):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 4)
        pygame.draw.circle(self.image, WHITE, (5, 5), 2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        # Draw Cross
        color = NEON_GREEN
        pygame.draw.rect(self.image, color, (8, 0, 8, 24))
        pygame.draw.rect(self.image, color, (0, 8, 24, 8))
        pygame.draw.rect(self.image, WHITE, (0, 0, 24, 24), 2)
        
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        # Pulse size
        scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 100.0)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- Globals & Setup ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
particles = pygame.sprite.Group()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEON SPACE SHOOTER")
clock = pygame.time.Clock()

stars = [Star() for _ in range(100)]
player = None
score = 0
wave = 1
enemy_spawn_timer = 0
game_state = GameState.MENU
game_time = 0.0 
last_frame_time = 0
high_score = 0
sounds = {}
background_music = None
music_volume = 0.3

# --- Audio System ---
def create_sound(frequency, duration, wave_type="sine", decay=True):
    try:
        sample_rate = 44100
        frames = int(sample_rate * duration)
        t = np.arange(frames) / sample_rate
        
        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "noise":
            wave = np.random.uniform(-1, 1, frames)
        elif wave_type == "sawtooth":
             wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            wave = np.sin(2 * np.pi * frequency * t)

        if decay:
            envelope = np.exp(-4 * t / duration)
            wave = wave * envelope
        
        wave = (wave * 32767 * 0.3).astype(np.int16)
        sound_array = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(sound_array)
    except Exception as e:
        return None

def generate_background_music():
    try:
        sample_rate = 44100
        duration = 12.0
        frames = int(sample_rate * duration)
        t = np.arange(frames) / sample_rate
        
        # Cyberpunk Bass Line
        freqs = [110, 110, 130.8, 98] # A2, A2, C3, G2
        wave = np.zeros(frames)
        beat_len = frames // 16
        
        for i in range(16):
            # Bass
            f = freqs[(i // 4) % 4]
            start = i * beat_len
            end = (i+1) * beat_len
            sect_t = t[start:end]
            w = np.sign(np.sin(2 * np.pi * f * sect_t)) * 0.5 # Square bass
            # Low pass filter approx via simple smoothing? No, just keep it raw for retro feel
            w *= np.exp(-3 * (sect_t - sect_t[0])) # Pluck envelope
            wave[start:end] += w
            
            # Hi-hats
            if i % 2 == 0:
                noise = np.random.uniform(-0.1, 0.1, len(sect_t))
                noise *= np.exp(-20 * (sect_t - sect_t[0]))
                wave[start:end] += noise

        # Arpeggios
        arp_freqs = [440, 554, 659, 880]
        for i in range(32):
             f = arp_freqs[i % 4]
             if i % 8 > 4: f *= 1.5 # Variation
             start = int(i * (frames / 32))
             end = int((i+1) * (frames / 32))
             if end > frames: break
             sect_t = t[start:end]
             w = np.sin(2 * np.pi * f * sect_t) * 0.1
             w *= np.exp(-5 * (sect_t - sect_t[0]))
             wave[start:end] += w

        wave = (wave * 32767 * 0.2).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
    except:
        return None

def load_all_sounds():
    global sounds, background_music
    print("Synthesizing Audio...")
    sounds["shoot"] = create_sound(880, 0.15, "square")
    if sounds["shoot"]: sounds["shoot"].set_volume(0.3)
    
    sounds["enemy_shoot"] = create_sound(220, 0.2, "sawtooth")
    if sounds["enemy_shoot"]: sounds["enemy_shoot"].set_volume(0.25)
    
    sounds["explosion"] = create_sound(50, 0.5, "noise")
    if sounds["explosion"]: sounds["explosion"].set_volume(0.4)
    
    sounds["powerup"] = create_sound(1200, 0.3, "sine")
    if sounds["powerup"]: sounds["powerup"].set_volume(0.4)
    
    sounds["gameover"] = create_sound(100, 2.0, "sawtooth")
    
    sounds["hit"] = create_sound(150, 0.2, "noise")
    sounds["wave"] = create_sound(300, 1.0, "sine")
    
    background_music = generate_background_music()
    print("Audio Ready.")

def play_sound(name):
    if name in sounds and sounds[name]:
        sounds[name].play()

def play_background_music():
    if background_music:
        background_music.set_volume(music_volume)
        background_music.play(-1)

# --- Management Functions ---
def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                high_score = data.get("high_score", 0)
        except:
            high_score = 0

def save_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump({"high_score": high_score}, f)
    except:
        pass

def create_explosion(x, y, color, count=15):
    add_shake(4)
    for _ in range(count):
        p = Particle(x, y, color)
        all_sprites.add(p)
        particles.add(p)

def start_game():
    global player, score, wave, enemy_spawn_timer, game_state, game_time, last_frame_time
    
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    particles.empty()
    
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
    all_sprites.add(player)
    
    score = 0
    wave = 1
    enemy_spawn_timer = 0
    game_state = GameState.PLAYING
    game_time = 0.0
    last_frame_time = pygame.time.get_ticks()
    
    play_sound("wave")

# --- Drawing Functions ---
def draw_ui_panel(rect, color=DARK_UI, border=NEON_BLUE):
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(temp, (*color, 200), (0,0,rect.width, rect.height), border_radius=10)
    pygame.draw.rect(temp, border, (0,0,rect.width, rect.height), 2, border_radius=10)
    screen.blit(temp, rect)

def draw_hud():
    # Top Bar Panel
    panel_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
    draw_ui_panel(panel_rect, (10, 10, 15), (50, 50, 100))
    
    # Score
    score_txt = font_md.render(f"SCORE: {score:06d}", True, WHITE)
    screen.blit(score_txt, (20, 15))
    
    # Timer (Fixed logic)
    mins = int(game_time // 60)
    secs = int(game_time % 60)
    # Use formatted string with Monospace assumption helper if font allows, otherwise just text
    time_str = f"{mins:02d}:{secs:02d}"
    
    # Timer Box
    timer_surf = font_md.render(time_str, True, NEON_YELLOW)
    timer_rect = timer_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
    screen.blit(timer_surf, timer_rect)
    
    # Health Bar
    bar_width = 200
    bar_height = 20
    x, y = SCREEN_WIDTH - 220, 20
    
    # Border
    pygame.draw.rect(screen, WHITE, (x-2, y-2, bar_width+4, bar_height+4), 2)
    # Background
    pygame.draw.rect(screen, (50, 0, 0), (x, y, bar_width, bar_height))
    # Fill
    health_pct = max(0, player.health / player.max_health)
    fill_width = int(bar_width * health_pct)
    fill_color = NEON_GREEN if health_pct > 0.5 else (NEON_RED if health_pct < 0.25 else NEON_ORANGE)
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, bar_height))
    
    # Wave
    wave_txt = font_sm.render(f"WAVE {wave}", True, NEON_BLUE)
    screen.blit(wave_txt, (SCREEN_WIDTH//2 - 30, 65))

def draw_menu():
    screen.fill(BLACK)
    # Animated background
    for star in stars:
        star.update(0.5)
        star.draw(screen)
        
    # Title
    title = font_xl.render("NEON SHOOTER", True, NEON_BLUE)
    # Glow effect for title (draw multiple times slightly offset/transparent)
    t_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
    for offset in range(3, 0, -1):
        glow = font_xl.render("NEON SHOOTER", True, (0, 100, 255))
        glow.set_alpha(50)
        screen.blit(glow, (t_rect.x - offset, t_rect.y))
        screen.blit(glow, (t_rect.x + offset, t_rect.y))
        
    screen.blit(title, t_rect)
    
    # Blinking text
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        start_txt = font_md.render("- PRESS SPACE -", True, WHITE)
        s_rect = start_txt.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(start_txt, s_rect)
        
    score_txt = font_md.render(f"HIGH SCORE: {high_score}", True, NEON_YELLOW)
    screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH//2, 400)))
    
    controls = font_sm.render("ARROWS: Move | Z: Shoot | P: Pause", True, (150, 150, 150))
    screen.blit(controls, controls.get_rect(center=(SCREEN_WIDTH//2, 500)))

def draw_game_over():
    # Overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0,0))
    
    over_txt = font_xl.render("MISSION FAILED", True, NEON_RED)
    screen.blit(over_txt, over_txt.get_rect(center=(SCREEN_WIDTH//2, 200)))
    
    score_txt = font_md.render(f"FINAL SCORE: {score}", True, WHITE)
    screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH//2, 300)))
    
    restart_txt = font_md.render("PRESS R TO RETRY", True, NEON_GREEN)
    screen.blit(restart_txt, restart_txt.get_rect(center=(SCREEN_WIDTH//2, 400)))

def update_game_logic():
    global score, wave, enemy_spawn_timer, game_state, game_time, last_frame_time
    
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_frame_time) / 1000.0
    last_frame_time = current_time
    game_time += dt
    
    update_shake()
    
    # Difficulty scaling
    if game_time < 120:
        difficulty = 1.0 + (game_time / 60.0)
    else:
        difficulty = 3.0 + ((game_time - 120) / 30.0)
        
    all_sprites.update()
    
    # Starfield background speed
    for s in stars:
        s.update(1.0 + difficulty * 0.1)
        
    # Spawning
    enemy_spawn_timer += 1
    spawn_rate = max(15, int(60 / (difficulty * 0.8)))
    
    if enemy_spawn_timer > spawn_rate:
        e = Enemy(random.randint(40, SCREEN_WIDTH-40), -50, difficulty)
        all_sprites.add(e)
        enemies.add(e)
        enemy_spawn_timer = 0
        
    for enemy in enemies:
        enemy.shoot()
        
    # Collisions
    # Bullet -> Enemy
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True) # Enemy, Bullet, KillE?, KillB?
    for enemy, hit_bullets in hits.items():
        # Using hit points
        enemy.hp -= len(hit_bullets)
        if enemy.hp <= 0:
            score += 100 * (3 if enemy.type=="elite" else 1)
            create_explosion(enemy.rect.centerx, enemy.rect.centery, enemy.color)
            play_sound("explosion")
            enemy.kill()
            
            # Powerup
            if random.random() < 0.1:
                p = PowerUp(enemy.rect.centerx, enemy.rect.centery, "heal")
                all_sprites.add(p)
                powerups.add(p)
        else:
            play_sound("hit")
            
    # Player -> Enemy/Bullet
    if pygame.sprite.spritecollide(player, enemies, True):
        play_sound("explosion")
        create_explosion(player.rect.centerx, player.rect.centery, NEON_RED)
        if not player.take_damage(20):
            game_state = GameState.GAME_OVER
            save_high_score()
            play_sound("gameover")
            
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    if hits:
        play_sound("hit")
        if not player.take_damage(10 * len(hits)):
            game_state = GameState.GAME_OVER
            save_high_score()
            play_sound("gameover")

    # Powerups
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for p in hits:
        player.health = min(player.max_health, player.health + 30)
        play_sound("powerup")
        
    # Wave Manager
    if int(game_time) // 30 > wave:
        wave += 1
        play_sound("wave")

# Main Loop
load_high_score()
load_all_sounds()
play_background_music()

running = True
last_frame_time = pygame.time.get_ticks()

while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state == GameState.MENU:
                start_game()
            elif event.key == pygame.K_r and game_state in [GameState.GAME_OVER, GameState.PAUSED, GameState.PLAYING]:
                start_game()
            elif event.key == pygame.K_p:
                if game_state == GameState.PLAYING:
                    game_state = GameState.PAUSED
                elif game_state == GameState.PAUSED:
                    game_state = GameState.PLAYING
                    last_frame_time = pygame.time.get_ticks()
            elif event.key == pygame.K_z and game_state == GameState.PLAYING:
                player.shoot()

    # Drawing and Updates
    screen.fill(BLACK)
    
    # Shake offset
    sx, sy = int(shake_offset[0]), int(shake_offset[1])
    
    if game_state == GameState.MENU:
        draw_menu()
    elif game_state == GameState.PLAYING:
        # Draw Background
        for s in stars:
            s.draw(screen)
        
        update_game_logic()
        
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x + sx, sprite.rect.y + sy))
            
        draw_hud()
        
    elif game_state == GameState.PAUSED:
        for s in stars: s.draw(screen)
        all_sprites.draw(screen)
        draw_hud()
        
        # Pause Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        screen.blit(overlay, (0,0))
        txt = font_lg.render("PAUSED", True, WHITE)
        screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        
    elif game_state == GameState.GAME_OVER:
        for s in stars: s.draw(screen)
        all_sprites.draw(screen)
        draw_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
