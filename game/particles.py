import pygame
import random
import math
from . import globals
from .utils import add_shake

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed_range=(2, 6), life_range=(20, 40), size_range=(2,6)):
        super().__init__()
        self.color = color
        self.size = random.randint(*size_range)
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(*life_range)
        self.original_life = self.life

    def update(self):
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
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
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.life = 15
        self.original_life = 15
        self.vy = random.uniform(1, 3)
        self.vx = random.uniform(-0.5, 0.5)

    def update(self):
        self.pos_y += self.vy
        self.pos_x += self.vx
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        self.life -= 1
        if self.life <= 0:
            self.kill()
        
        alpha = int(200 * (self.life / self.original_life))
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (*self.color, alpha), (3, 3), 2)

def create_explosion(x, y, color, count=15):
    add_shake(4)
    for _ in range(count):
        p = Particle(x, y, color)
        globals.all_sprites.add(p)
        globals.particles.add(p)
