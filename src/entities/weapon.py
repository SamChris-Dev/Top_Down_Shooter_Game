import pygame
import random
from systems.audio import audio_manager

class Weapon:
    def __init__(self, game, name, damage, fire_rate, spread, bullet_speed, lifetime, sound_name):
        self.game = game
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.spread = spread
        self.bullet_speed = bullet_speed
        self.lifetime = lifetime
        self.sound_name = sound_name
        self.last_shot = 0

    def shoot(self, x, y, angle):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            
            # Apply spread
            final_angle = angle + random.uniform(-self.spread, self.spread)
            
            # Fire bullet using the pool
            self.game.bullet_pool.get_bullet(
                x, y, final_angle, self.damage, self.bullet_speed, self.lifetime
            )
            
            # Play sound
            snd = self.game.asset_manager.load_sound(self.sound_name)
            if snd:
                audio_manager.play_sound(snd)
                
            return True # Shot fired
        return False

class Pistol(Weapon):
    def __init__(self, game):
        super().__init__(game, "Pistol", damage=25, fire_rate=250, spread=2, bullet_speed=500, lifetime=1000, sound_name='audio/shoot.wav')

class Shotgun(Weapon):
    def __init__(self, game):
        super().__init__(game, "Shotgun", damage=15, fire_rate=800, spread=15, bullet_speed=450, lifetime=600, sound_name='audio/shoot.wav')

    def shoot(self, x, y, angle):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            
            # Shotgun fires multiple pellets
            for _ in range(5):
                final_angle = angle + random.uniform(-self.spread, self.spread)
                speed = self.bullet_speed * random.uniform(0.8, 1.2)
                self.game.bullet_pool.get_bullet(
                    x, y, final_angle, self.damage, speed, self.lifetime
                )
                
            snd = self.game.asset_manager.load_sound(self.sound_name)
            if snd:
                audio_manager.play_sound(snd)
            return True
        return False

class SMG(Weapon):
    def __init__(self, game):
        super().__init__(game, "SMG", damage=15, fire_rate=100, spread=8, bullet_speed=600, lifetime=800, sound_name='audio/shoot.wav')

class AssaultRifle(Weapon):
    def __init__(self, game):
        super().__init__(game, "Assault Rifle", damage=30, fire_rate=150, spread=3, bullet_speed=700, lifetime=1000, sound_name='audio/shoot.wav')

class SniperRifle(Weapon):
    def __init__(self, game):
        super().__init__(game, "Sniper Rifle", damage=100, fire_rate=1200, spread=0, bullet_speed=1500, lifetime=1500, sound_name='audio/shoot.wav')
