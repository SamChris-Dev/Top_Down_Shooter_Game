import pygame
import math
from core.settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle, damage=BULLET_DAMAGE, speed=BULLET_SPEED, lifetime=BULLET_LIFETIME):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.damage = damage
        self.speed = speed
        self.lifetime = lifetime
        
        try:
            self.orig_image = pygame.image.load("assets/PNG/weapon_silencer.png").convert_alpha()
            self.orig_image.fill((255, 200, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except FileNotFoundError:
            self.orig_image = pygame.Surface((15, 5), pygame.SRCALPHA)
            self.orig_image.fill((255, 255, 0))
            
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = -math.sin(math.radians(angle)) * self.speed
        
        self.spawn_time = pygame.time.get_ticks()

    def fire(self, x, y, angle, damage, speed, lifetime):
        self.add(self.groups)
        self.damage = damage
        self.speed = speed
        self.lifetime = lifetime
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = -math.sin(math.radians(angle)) * self.speed
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos.x += self.vx * self.game.dt
        self.pos.y += self.vy * self.game.dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
            
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
            
        # Screen bounds check
        cam = self.game.camera.camera
        if not (-cam.x - 200 < self.pos.x < -cam.x + WIDTH + 200 and 
                -cam.y - 200 < self.pos.y < -cam.y + HEIGHT + 200):
            self.kill()

class BulletPool:
    def __init__(self, game, pool_size=50):
        self.game = game
        self.pool = [Bullet(game, -1000, -1000, 0) for _ in range(pool_size)]
        
        for bullet in self.pool:
            bullet.kill()

    def get_bullet(self, x, y, angle, damage, speed, lifetime):
        for bullet in self.pool:
            if not bullet.alive():
                bullet.fire(x, y, angle, damage, speed, lifetime)
                return bullet
        
        new_bullet = Bullet(self.game, x, y, angle, damage, speed, lifetime)
        self.pool.append(new_bullet)
        return new_bullet
