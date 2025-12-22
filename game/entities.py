import pygame
import random
import math
from .constants import *
from . import globals
from .utils import add_shake
from .audio import play_sound
from .particles import TrailParticle

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
        self.pos_y = float(y)
        self.speed = speed

    def update(self):
        self.pos_y += self.speed
        self.rect.y = int(self.pos_y)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

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
        self.pos_x = float(self.rect.x)
        self.speed = 6
        self.health = 100
        self.max_health = 100
        self.last_shot = 0
        self.shoot_delay = 180 
        self.tilt = 0 # For visual banking logic

    def update(self):
        keys = pygame.key.get_pressed()
        dx = 0
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            dx = -1
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH:
            dx = 1
        
        self.pos_x += dx * self.speed
        self.rect.x = int(self.pos_x)

        # Clamp
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x)
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.pos_x = float(self.rect.x)
        
        # Tilt effect
        target_tilt = dx * -15
        self.tilt = self.tilt * 0.8 + target_tilt * 0.2
        
        # Engine trails
        if random.random() < 0.8:
            offset_x = random.randint(-5, 5)
            p = TrailParticle(self.rect.centerx + offset_x, self.rect.bottom - 5, NEON_BLUE)
            globals.all_sprites.add(p)
            globals.particles.add(p)
            
        self.update_image()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            bullet_left = Bullet(self.rect.centerx - 10, self.rect.top + 10)
            bullet_right = Bullet(self.rect.centerx + 10, self.rect.top + 10)
            globals.all_sprites.add(bullet_left, bullet_right)
            globals.bullets.add(bullet_left, bullet_right)
            play_sound("shoot")
            self.last_shot = now
            add_shake(2)

    def take_damage(self, damage):
        self.health -= damage
        add_shake(10)
        return self.health > 0

    def update_image(self):
        # Calculate polygon points based on tilt
        self.image.fill((0,0,0,0))
        
        # Local coordinates for image
        w, h = self.width, self.height
        
        # Simple tilt skewing
        # We want the top of the ship to lean
        offset_top = self.tilt * 0.5
        
        local_points = [
            (w/2 + offset_top, 0),
            (0, h),
            (w/2, h*0.8),
            (w, h)
        ]

        # Draw ship body
        pygame.draw.polygon(self.image, NEON_GREEN, local_points)
        pygame.draw.polygon(self.image, WHITE, local_points, 2) # Outline
        
        # Cockpit
        pygame.draw.circle(self.image, NEON_BLUE, (int(w//2 + offset_top * 0.5), int(h//2)), 6)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, difficulty=1.0):
        super().__init__()
        self.width = 44
        self.height = 40
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)
        
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
        self.pos_y += self.speed
        
        # Wiggle motion
        self.pos_x += math.sin(pygame.time.get_ticks() / 200.0 + self.pos_y) * 2
        
        self.rect.y = int(self.pos_y)
        self.rect.x = int(self.pos_x)
        
        self.shoot_timer -= 1
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet_speed = 6 + (self.difficulty - 1) * 1.5
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, bullet_speed, self.color)
            globals.all_sprites.add(bullet)
            globals.enemy_bullets.add(bullet)
            
            base_rate = 60 if self.type == "normal" else 40
            self.shoot_timer = random.randint(max(20, int(base_rate / self.difficulty)), max(40, int(base_rate*2 / self.difficulty)))
            play_sound("enemy_shoot")

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
