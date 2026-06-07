import pygame
import sys
import os
from settings import *
from tilemap import TiledMap
from camera import Camera  
from entities import Player, Obstacle, Zombie

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load data, initialize sprite groups
        self.load_data()

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        assets_folder = os.path.join(os.path.dirname(game_folder), 'assets')
        self.map = TiledMap(os.path.join(assets_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def build_pathfinding_grid(self):
        self.grid_width = self.map.width // TILESIZE
        self.grid_height = self.map.height // TILESIZE
        self.pathfinding_grid = [['0' for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for wall in self.walls:
            # Mark all cells that intersect this wall as '1'
            start_x = max(0, wall.rect.left // TILESIZE)
            end_x = min(self.grid_width - 1, wall.rect.right // TILESIZE)
            start_y = max(0, wall.rect.top // TILESIZE)
            end_y = min(self.grid_height - 1, wall.rect.bottom // TILESIZE)
            
            for y in range(start_y, end_y + 1):
                for x in range(start_x, end_x + 1):
                    self.pathfinding_grid[y][x] = '1'

    def new(self):
        # Initializes a new game, sets up sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'zombie':
                Zombie(self, tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                
        self.build_pathfinding_grid()
                    
        # Initialize the Camera bounds based on the parsed map size
        self.camera = Camera(self.map.width, self.map.height)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            # Delta Time in seconds
            self.dt = self.clock.tick(FPS) / 1000.0 
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # Update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player) # Will be implemented when player is added
        
        # Bullet - Zombie collisions
        # groupcollide(group1, group2, dokill1, dokill2) -> returns a dictionary
        hits = pygame.sprite.groupcollide(self.zombies, self.bullets, False, True)
        for zombie in hits:
            zombie.health -= BULLET_DAMAGE

    def draw(self):
        # Fill BG first just in case
        self.screen.fill(BG_COLOR)
        
        # Blit the entire rendered TMX map image
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        
        # We will loop through all sprites and apply the camera offset before drawing
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
        pygame.display.flip()

    def events(self):
        # Event Catching
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.shoot()