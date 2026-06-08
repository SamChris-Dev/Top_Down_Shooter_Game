import pygame
import sys
import os

# Ensure the src directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings import *
from core.camera import Camera
from core.assets import asset_manager
from tilemap import TiledMap
from entities.player import Player
from entities.zombie import Zombie
from entities.obstacle import Obstacle
from entities.bullet import BulletPool
from systems.pathfinding import FlowField
from systems.wave_manager import WaveManager
from systems.effects import screen_shake, spawn_particles
from ui.hud import HUD
from ui.menu import Menu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        self.asset_manager = asset_manager
        self.menu = Menu(self)
        self.hud = HUD(self)
        
        self.load_data()

    def load_data(self):
        assets_folder = self.asset_manager.assets_dir
        self.map = TiledMap(os.path.join(assets_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        
    def build_pathfinding_grid(self):
        self.grid_width = self.map.width // TILESIZE
        self.grid_height = self.map.height // TILESIZE
        self.pathfinding_grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for wall in self.walls:
            start_x = max(0, wall.rect.left // TILESIZE)
            end_x = min(self.grid_width - 1, wall.rect.right // TILESIZE)
            start_y = max(0, wall.rect.top // TILESIZE)
            end_y = min(self.grid_height - 1, wall.rect.bottom // TILESIZE)
            
            for y in range(start_y, end_y + 1):
                for x in range(start_x, end_x + 1):
                    self.pathfinding_grid[y][x] = '1'
                    
        # Initialize Flow Field
        self.flow_field = FlowField(self)

    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.bullet_pool = BulletPool(self, pool_size=50)
        self.wave_manager = WaveManager(self)
        
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'zombie':
                Zombie(self, tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                
        self.build_pathfinding_grid()
        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False
        
        # Start the first wave
        self.wave_manager.start_wave()
        
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0 
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        if hasattr(self, 'player'):
            self.camera.update(self.player)
            
            # Update Flow Field based on player position
            target_grid = (int(self.player.pos.x // TILESIZE), int(self.player.pos.y // TILESIZE))
            self.flow_field.update_field(target_grid)
            
        self.wave_manager.update()
        
        # Bullet - Zombie collisions
        hits = pygame.sprite.groupcollide(self.zombies, self.bullets, False, False)
        for zombie, bullets in hits.items():
            for bullet in bullets:
                zombie.health -= bullet.damage
                bullet.kill()
                
                # Blood particles
                spawn_particles(self, zombie.pos.x, zombie.pos.y, RED, count=10, speed_range=(50, 200))
                
                snd = self.asset_manager.load_sound('audio/hit.wav')
                from systems.audio import audio_manager
                if snd:
                    audio_manager.play_sound(snd)

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Apply screen shake offset
        shake_x, shake_y = screen_shake.get_offset()
        
        # Draw Map
        map_rect = self.camera.apply_rect(self.map_rect)
        map_rect.x += shake_x
        map_rect.y += shake_y
        self.screen.blit(self.map_img, map_rect)
        
        # Draw Sprites
        for sprite in self.all_sprites:
            sprite_rect = self.camera.apply(sprite)
            sprite_rect.x += shake_x
            sprite_rect.y += shake_y
            self.screen.blit(sprite.image, sprite_rect)
            
        self.hud.draw()
        
        if self.paused:
            self.menu.show_pause_screen()

        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                if event.key == pygame.K_e and hasattr(self, 'player') and not self.paused:
                    self.player.switch_weapon(1)
                if event.key == pygame.K_q and hasattr(self, 'player') and not self.paused:
                    self.player.switch_weapon(-1)
            
            # Continuous shooting
            if pygame.mouse.get_pressed()[0]:
                if hasattr(self, 'player') and not self.paused:
                    self.player.shoot()

    def quit(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    g = Game()
    g.menu.show_start_screen()
    while g.running:
        g.new()
        g.menu.show_go_screen()
