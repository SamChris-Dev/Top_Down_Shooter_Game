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

class DamageNumber(pygame.sprite.Sprite):
    def __init__(self, game, x, y, amount, color=WHITE):
        self.groups = game.all_sprites, game.particles # Use particles group so it doesn't collide
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        font = game.asset_manager.get_font('arial', 20)
        self.image = font.render(str(int(amount)), True, color)
        self.rect = self.image.get_rect()
        
        # Add random slight offset so numbers don't perfectly stack
        x += random.randint(-15, 15)
        y += random.randint(-15, 15)
        
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 800 # 800ms
        self.vy = -50 # float upwards at 50px/sec

    def update(self):
        self.pos.y += self.vy * self.game.dt
        self.rect.center = self.pos
        
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.lifetime:
            self.kill()
        else:
            # Fade out
            alpha = max(0, 255 - int(255 * ((now - self.spawn_time) / self.lifetime)))
            self.image.set_alpha(alpha)

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
