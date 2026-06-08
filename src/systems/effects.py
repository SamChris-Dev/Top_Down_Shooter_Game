import pygame
import random
from core.settings import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, color, duration, speed_range, size_range):
        self.groups = game.all_sprites, game.particles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.size = random.randint(*size_range)
        self.color = color
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        
        angle = random.uniform(0, 360)
        speed = random.uniform(*speed_range)
        self.vel = pygame.math.Vector2(1, 0).rotate(angle) * speed
        
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

def spawn_particles(game, x, y, color, count=5, duration=200, speed_range=(50, 150), size_range=(2, 5)):
    for _ in range(count):
        Particle(game, x, y, color, duration, speed_range, size_range)

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.start_time = 0
        self.active = False
        
    def shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.active = True
        
    def get_offset(self):
        if not self.active:
            return 0, 0
            
        now = pygame.time.get_ticks()
        if now - self.start_time > self.duration:
            self.active = False
            return 0, 0
            
        x_offset = random.randint(-self.intensity, self.intensity)
        y_offset = random.randint(-self.intensity, self.intensity)
        return x_offset, y_offset

screen_shake = ScreenShake()
