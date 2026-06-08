import pygame
import sys
import os
from settings import *
from tilemap import TiledMap
from camera import Camera  
from entities import Player, Obstacle, Zombie, collide_hit_rect
from spritesheet import Spritesheet

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Load data, initialize sprite groups
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        elif align == "ne":
            text_rect.topright = (x, y)
        elif align == "sw":
            text_rect.bottomleft = (x, y)
        elif align == "se":
            text_rect.bottomright = (x, y)
        elif align == "n":
            text_rect.midtop = (x, y)
        elif align == "s":
            text_rect.midbottom = (x, y)
        elif align == "e":
            text_rect.midright = (x, y)
        elif align == "w":
            text_rect.midleft = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        assets_folder = os.path.join(os.path.dirname(game_folder), 'assets')
        self.map = TiledMap(os.path.join(assets_folder, 'map.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        
        # Load the character spritesheet
        ss_img = os.path.join(assets_folder, 'Spritesheet', 'spritesheet_characters.png')
        ss_xml = os.path.join(assets_folder, 'Spritesheet', 'spritesheet_characters.xml')
        self.chars_spritesheet = Spritesheet(ss_img, ss_xml)

        # Load sounds
        pygame.mixer.init()
        audio_folder = os.path.join(assets_folder, 'audio')
        try:
            self.shoot_snd = pygame.mixer.Sound(os.path.join(audio_folder, 'shoot.wav'))
            self.hit_snd = pygame.mixer.Sound(os.path.join(audio_folder, 'hit.wav'))
            self.shoot_snd.set_volume(0.5)
            self.hit_snd.set_volume(0.8)
        except FileNotFoundError:
            self.shoot_snd = None
            self.hit_snd = None

        self.chars_spritesheet = Spritesheet(ss_img, ss_xml)
        try:
            self.zombie_img = pygame.image.load(os.path.join(assets_folder, 'PNG', 'Zombie 1', 'zoimbie1_stand.png')).convert_alpha()
        except FileNotFoundError:
            self.zombie_img = pygame.Surface((TILESIZE, TILESIZE))
            self.zombie_img.fill((255, 0, 0))


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
        
        # Initialize Bullet Pool
        from entities import BulletPool # Make sure to import it at the top
        self.bullet_pool = BulletPool(self, pool_size=30)

        
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
        self.paused = False
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            # Delta Time in seconds
            self.dt = self.clock.tick(FPS) / 1000.0 
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pygame.quit()
        sys.exit()

    def update(self):
        # Update portion of the game loop
        self.all_sprites.update()
        if hasattr(self, 'player'):
            self.camera.update(self.player) # Will be implemented when player is added
        
        # Bullet - Zombie collisions
        hits = pygame.sprite.groupcollide(self.zombies, self.bullets, False, True)
        for zombie in hits:
            zombie.health -= BULLET_DAMAGE
            if self.hit_snd:
                self.hit_snd.play()

        # Zombie - Player collisions
        if hasattr(self, 'player'):
            hits = pygame.sprite.spritecollide(self.player, self.zombies, False, collide_hit_rect)
            for hit in hits:
                self.player.health -= ZOMBIE_DAMAGE
                # Minor knockback or stop their velocity so they don't instakill instantly frame-by-frame
                hit.vel = pygame.math.Vector2(0, 0)
                if self.player.health <= 0:
                    self.playing = False

    def draw(self):
        # Fill BG first just in case
        self.screen.fill(BG_COLOR)
        
        # Blit the entire rendered TMX map image
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        
        # We will loop through all sprites and apply the camera offset before drawing
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
        # Draw HUD
        if hasattr(self, 'player'):
            self.draw_text(f"Health: {int(self.player.health)}", pygame.font.match_font('arial'), 24, WHITE, 20, 20, align="nw")

        # Draw Pause Screen Overlay
        if self.paused:
            dim_screen = pygame.Surface(self.screen.get_size()).convert_alpha()
            dim_screen.fill((0, 0, 0, 180))
            self.screen.blit(dim_screen, (0, 0))
            self.draw_text("PAUSED", pygame.font.match_font('arial'), 64, RED, WIDTH / 2, HEIGHT / 2, align="center")

        pygame.display.flip()

    def events(self):
        # Event Catching
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and hasattr(self, 'player') and not self.paused:
                    self.player.shoot()

    def wait_for_key(self):
        pygame.event.clear()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pygame.KEYUP:
                    waiting = False

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text(TITLE, pygame.font.match_font('arial'), 64, WHITE, WIDTH / 2, HEIGHT / 4, align="center")
        self.draw_text("WASD to move, Mouse to aim/shoot, LSHIFT to sprint", pygame.font.match_font('arial'), 22, WHITE, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press any key to play", pygame.font.match_font('arial'), 36, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # Only show game over if we actually ran the game
        if not self.running:
            return

        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", pygame.font.match_font('arial'), 64, RED, WIDTH / 2, HEIGHT / 4, align="center")
        self.draw_text("Press any key to restart", pygame.font.match_font('arial'), 36, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pygame.display.flip()
        self.wait_for_key()
