import pygame
import math
from core.settings import *
from systems.collision import collide_with_walls
from entities.weapon import Pistol, Shotgun, SMG, AssaultRifle, SniperRifle
from systems.effects import screen_shake

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Weapons setup
        self.weapons = [
            Pistol(game),
            Shotgun(game),
            SMG(game),
            AssaultRifle(game),
            SniperRifle(game)
        ]
        self.weapon_index = 0
        self.current_weapon = self.weapons[self.weapon_index]
        
        # Sprites
        sheet = self.game.asset_manager.load_spritesheet(
            'Spritesheet/spritesheet_characters.png',
            'Spritesheet/spritesheet_characters.xml',
            'characters'
        )
        
        self.frames = {
            'idle': self.game.asset_manager.get_sprite('characters', 'survivor1_stand.png'),
            'stand': self.game.asset_manager.get_sprite('characters', 'survivor1_stand.png'),
            'gun': self.game.asset_manager.get_sprite('characters', 'survivor1_gun.png'),
            'machine': self.game.asset_manager.get_sprite('characters', 'survivor1_machine.png'),
            'reload': self.game.asset_manager.get_sprite('characters', 'survivor1_reload.png')
        }

        self.image = self.frames['gun']
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        
        self.hit_rect = PLAYER_HIT_RECT.copy()
        self.pos = pygame.math.Vector2(x, y)
        self.hit_rect.center = self.pos
        self.rect.center = self.hit_rect.center
        self.rot = 0
        
        self.vx, self.vy = 0, 0
        self.health = PLAYER_HEALTH
        self.score = 0
        
        # Invulnerability frames
        self.invulnerable = False
        self.invulnerable_duration = 1000
        self.last_hit_time = 0
        
        # Dash mechanic
        self.is_dashing = False
        self.dash_speed = PLAYER_RUN_SPEED * 2.5
        self.dash_duration = 200
        self.dash_cooldown = 1500
        self.last_dash_time = 0
        
        # Animation variables
        self.state = 'idle'
        self.is_running = False
        self.last_anim_update = 0
        self.anim_frame = 0

    def get_keys(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Dash input
        if keys[pygame.K_SPACE] and now - self.last_dash_time > self.dash_cooldown:
            self.is_dashing = True
            self.last_dash_time = now
            self.invulnerable = True # i-frames during dash
            
        if self.is_dashing:
            if now - self.last_dash_time > self.dash_duration:
                self.is_dashing = False
                self.invulnerable = False
            else:
                # Keep moving in the current direction at dash speed
                if self.vx == 0 and self.vy == 0:
                    self.vx = self.dash_speed # default dash right if no input
                else:
                    vec = pygame.math.Vector2(self.vx, self.vy).normalize()
                    self.vx = vec.x * self.dash_speed
                    self.vy = vec.y * self.dash_speed
                return # Skip normal movement input

        self.vx, self.vy = 0, 0
        self.is_running = keys[pygame.K_LSHIFT]
        current_speed = PLAYER_RUN_SPEED if self.is_running else PLAYER_SPEED
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = current_speed
            
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071
            
        if keys[pygame.K_c]:
            self.current_weapon.reload()

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.current_weapon.is_reloading:
            self.state = 'reloading'
        elif now - self.current_weapon.last_shot < 100:
            self.state = 'shooting'
        elif self.vx != 0 or self.vy != 0:
            self.state = 'running' if self.is_running else 'moving'
        else:
            self.state = 'idle'
            
        if self.state == 'reloading':
            self.orig_image = self.frames['reload']
        elif self.state == 'shooting':
            self.orig_image = self.frames['machine']
        elif self.state == 'idle':
            self.orig_image = self.frames['gun']
        elif self.state == 'moving' or self.state == 'running':
            anim_speed = 100 if self.state == 'running' else 200
            if now - self.last_anim_update > anim_speed:
                self.last_anim_update = now
                self.anim_frame = (self.anim_frame + 1) % 2
            
            if self.anim_frame == 0:
                self.orig_image = self.frames['gun']
            else:
                self.orig_image = self.frames['stand']
                
        # Damage flash
        if self.invulnerable:
            # Blink effect
            if (now // 100) % 2 == 0:
                # Tint red
                flash = pygame.Surface(self.orig_image.get_size(), pygame.SRCALPHA)
                flash.fill((255, 0, 0, 100))
                self.orig_image = self.orig_image.copy()
                self.orig_image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def switch_weapon(self, direction):
        self.weapon_index = (self.weapon_index + direction) % len(self.weapons)
        self.current_weapon = self.weapons[self.weapon_index]
        print(f"Switched to {self.current_weapon.name}")

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.last_hit_time = now
            screen_shake.shake(10, 200) # Heavy shake on hit
            
            snd = self.game.asset_manager.load_sound('audio/hit.wav')
            from systems.audio import audio_manager
            if snd:
                audio_manager.play_sound(snd)
                
            if self.health <= 0:
                # Update high score in save manager
                from systems.save_manager import save_manager
                high_score = save_manager.get("high_score", 0)
                if self.score > high_score:
                    save_manager.update("high_score", self.score)
                self.game.playing = False

    def update(self):
        now = pygame.time.get_ticks()
        
        # Check i-frames
        if self.invulnerable and now - self.last_hit_time > self.invulnerable_duration:
            self.invulnerable = False
            
        self.get_keys()
        self.animate()
        
        # Update current weapon (reloading logic)
        self.current_weapon.update()
        
        mouse_pos = pygame.mouse.get_pos()
        cam_x = self.game.camera.camera.x
        cam_y = self.game.camera.camera.y
        player_screen_x = self.pos.x + cam_x
        player_screen_y = self.pos.y + cam_y
        
        dx = mouse_pos[0] - player_screen_x
        dy = mouse_pos[1] - player_screen_y
        self.rot = math.degrees(math.atan2(-dy, dx))
        
        self.image = pygame.transform.rotate(self.orig_image, self.rot)
        self.rect = self.image.get_rect()
        
        self.pos.x += self.vx * self.game.dt
        self.hit_rect.centerx = round(self.pos.x)
        collide_with_walls(self, self.game.walls, 'x')
        
        self.pos.y += self.vy * self.game.dt
        self.hit_rect.centery = round(self.pos.y)
        collide_with_walls(self, self.game.walls, 'y')
        
        self.rect.center = self.hit_rect.center

    def shoot(self):
        if self.current_weapon.shoot(self.rect.centerx, self.rect.centery, self.rot):
            screen_shake.shake(2, 50) # Light shake on shoot
