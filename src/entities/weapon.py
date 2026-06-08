import pygame
import random
from systems.audio import audio_manager
from systems.effects import spawn_particles

class Weapon:
    def __init__(self, game, name, damage, fire_rate, spread, bullet_speed, lifetime, sound_name, mag_size, reserve_ammo, reload_time):
        self.game = game
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.spread = spread
        self.bullet_speed = bullet_speed
        self.lifetime = lifetime
        self.sound_name = sound_name
        self.last_shot = 0
        
        self.mag_size = mag_size
        self.current_ammo = mag_size
        self.max_reserve = reserve_ammo
        self.reserve_ammo = reserve_ammo
        self.reload_time = reload_time
        self.is_reloading = False
        self.reload_start_time = 0

    def update(self):
        if self.is_reloading:
            if pygame.time.get_ticks() - self.reload_start_time > self.reload_time:
                self.is_reloading = False
                needed = self.mag_size - self.current_ammo
                if self.reserve_ammo >= needed:
                    self.current_ammo += needed
                    self.reserve_ammo -= needed
                else:
                    self.current_ammo += self.reserve_ammo
                    self.reserve_ammo = 0

    def reload(self):
        if not self.is_reloading and self.current_ammo < self.mag_size and self.reserve_ammo > 0:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()

    def shoot(self, x, y, angle):
        if self.is_reloading or self.current_ammo <= 0:
            return False
            
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            self.current_ammo -= 1
            
            # Apply spread
            final_angle = angle + random.uniform(-self.spread, self.spread)
            
            # Fire bullet using the pool
            self.game.bullet_pool.get_bullet(
                x, y, final_angle, self.damage, self.bullet_speed, self.lifetime
            )
            
            # Muzzle flash
            spawn_particles(self.game, x, y, (255, 255, 0), count=3, duration=50, speed_range=(20, 50), size_range=(3, 6))
            
            # Play sound with dynamic volume for variety
            snd = self.game.asset_manager.load_sound(self.sound_name)
            if snd:
                audio_manager.play_sound(snd, volume_scale=random.uniform(0.8, 1.0))
                
            return True # Shot fired
        return False

class Pistol(Weapon):
    def __init__(self, game):
        # Pistol has infinite reserve ammo
        super().__init__(game, "Pistol", damage=25, fire_rate=250, spread=2, bullet_speed=500, lifetime=1000, sound_name='audio/shoot.wav', mag_size=12, reserve_ammo=9999, reload_time=1000)
    
    def update(self):
        if self.is_reloading:
            if pygame.time.get_ticks() - self.reload_start_time > self.reload_time:
                self.is_reloading = False
                self.current_ammo = self.mag_size

class Shotgun(Weapon):
    def __init__(self, game):
        super().__init__(game, "Shotgun", damage=15, fire_rate=800, spread=15, bullet_speed=450, lifetime=600, sound_name='audio/shoot.wav', mag_size=6, reserve_ammo=24, reload_time=2000)

    def shoot(self, x, y, angle):
        if self.is_reloading or self.current_ammo <= 0:
            return False
            
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.last_shot = now
            self.current_ammo -= 1
            
            # Shotgun fires multiple pellets
            for _ in range(5):
                final_angle = angle + random.uniform(-self.spread, self.spread)
                speed = self.bullet_speed * random.uniform(0.8, 1.2)
                self.game.bullet_pool.get_bullet(
                    x, y, final_angle, self.damage, speed, self.lifetime
                )
                
            # Muzzle flash
            spawn_particles(self.game, x, y, (255, 255, 0), count=8, duration=50, speed_range=(30, 80), size_range=(3, 6))
            
            snd = self.game.asset_manager.load_sound(self.sound_name)
            if snd:
                audio_manager.play_sound(snd, volume_scale=random.uniform(0.8, 1.0))
            return True
        return False

class SMG(Weapon):
    def __init__(self, game):
        super().__init__(game, "SMG", damage=15, fire_rate=100, spread=8, bullet_speed=600, lifetime=800, sound_name='audio/shoot.wav', mag_size=30, reserve_ammo=90, reload_time=1500)

class AssaultRifle(Weapon):
    def __init__(self, game):
        super().__init__(game, "Assault Rifle", damage=30, fire_rate=150, spread=3, bullet_speed=700, lifetime=1000, sound_name='audio/shoot.wav', mag_size=20, reserve_ammo=60, reload_time=1800)

class SniperRifle(Weapon):
    def __init__(self, game):
        super().__init__(game, "Sniper Rifle", damage=100, fire_rate=1200, spread=0, bullet_speed=1500, lifetime=1500, sound_name='audio/shoot.wav', mag_size=5, reserve_ammo=15, reload_time=2500)
