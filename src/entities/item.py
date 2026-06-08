import pygame
import random
import math
from core.settings import *

class ItemDrop(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type # 'health' or 'ammo'
        
        self.image = pygame.Surface((30, 30))
        if self.type == 'health':
            self.image.fill(GREEN)
            # Draw a cross
            pygame.draw.rect(self.image, WHITE, (10, 5, 10, 20))
            pygame.draw.rect(self.image, WHITE, (5, 10, 20, 10))
        else: # Ammo
            self.image.fill(YELLOW)
            # Draw some bullet shapes
            pygame.draw.rect(self.image, DARK_GRAY, (8, 5, 5, 20))
            pygame.draw.rect(self.image, DARK_GRAY, (17, 5, 5, 20))
            
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        
        # Bobbing animation
        self.spawn_time = pygame.time.get_ticks()
        self.bob_speed = 0.005
        self.bob_height = 5
        
        # Despawn after 15 seconds
        self.lifetime = 15000

    def update(self):
        now = pygame.time.get_ticks()
        
        # Bobbing
        offset = math.sin(now * self.bob_speed) * self.bob_height
        self.rect.centery = self.pos.y + offset
        
        if now - self.spawn_time > self.lifetime:
            self.kill()
