import pygame
from systems.effects import spawn_particles, screen_shake
from core.settings import *

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class ExplosiveBarrel(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls, game.barrels
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        pygame.draw.rect(self.image, DARK_GRAY, (0, 10, 40, 5))
        pygame.draw.rect(self.image, DARK_GRAY, (0, 25, 40, 5))
        
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = self.pos
        self.hit_rect = self.rect.copy()
        
        self.health = 50

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.explode()
            
    def explode(self):
        # VFX
        spawn_particles(self.game, self.pos.x, self.pos.y, RED, count=40, speed_range=(100, 400), size_range=(5, 12))
        spawn_particles(self.game, self.pos.x, self.pos.y, YELLOW, count=20, speed_range=(50, 300), size_range=(5, 15))
        screen_shake.shake(20, 400)
        
        # SFX
        snd = self.game.asset_manager.load_sound('audio/hit.wav') # Ideally an explosion sound
        from systems.audio import audio_manager
        if snd:
            audio_manager.play_sound(snd, volume_scale=1.5)
            
        # AoE Damage to Zombies
        for zombie in self.game.zombies:
            dist = zombie.pos.distance_to(self.pos)
            if dist < 200:
                zombie.health -= 150
                
        # AoE Damage to Player
        if hasattr(self.game, 'player') and self.game.player.alive():
            dist = self.game.player.pos.distance_to(self.pos)
            if dist < 200:
                self.game.player.take_damage(50)
                
        # Scorch mark decal on the map
        scorch = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(scorch, (0, 0, 0, 150), (75, 75), 75)
        self.game.map_img.blit(scorch, (self.pos.x - 75, self.pos.y - 75))
        
        self.kill()
