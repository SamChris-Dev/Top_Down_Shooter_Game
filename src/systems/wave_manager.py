import pygame
import random
from core.settings import *

class WaveManager:
    def __init__(self, game):
        self.game = game
        self.current_wave = 0
        self.zombies_to_spawn = 0
        self.zombies_alive = 0
        self.spawn_delay = 1000 # ms
        self.last_spawn_time = 0
        self.wave_active = False
        self.wave_transition_time = 3000 # ms break between waves
        self.wave_end_time = 0

    def start_wave(self):
        self.current_wave += 1
        # Formula: Wave 1 = 5, Wave 2 = 10, Wave 3 = 15...
        self.zombies_to_spawn = self.current_wave * 5
        self.zombies_alive = 0
        self.wave_active = True
        print(f"Wave {self.current_wave} started!")

    def update(self):
        now = pygame.time.get_ticks()

        # Update alive count
        self.zombies_alive = len(self.game.zombies)

        if not self.wave_active:
            if now - self.wave_end_time > self.wave_transition_time:
                self.start_wave()
            return

        if self.zombies_to_spawn > 0:
            if now - self.last_spawn_time > self.spawn_delay:
                self.spawn_zombie()
                self.last_spawn_time = now
        elif self.zombies_alive == 0:
            # Wave complete
            self.wave_active = False
            self.wave_end_time = now
            print(f"Wave {self.current_wave} complete!")
            
            # Update best wave
            from systems.save_manager import save_manager
            best = save_manager.get("best_wave")
            if self.current_wave > best:
                save_manager.update("best_wave", self.current_wave)

    def spawn_zombie(self):
        # Find a valid spawn location outside camera if possible, or random on map
        # For simplicity, pick a random tile that is not a wall
        while True:
            x = random.randint(0, self.game.map.width)
            y = random.randint(0, self.game.map.height)
            
            grid_x = int(x // TILESIZE)
            grid_y = int(y // TILESIZE)
            
            if 0 <= grid_x < self.game.grid_width and 0 <= grid_y < self.game.grid_height:
                if self.game.pathfinding_grid[grid_y][grid_x] == '0':
                    # Safe to spawn
                    from entities.zombie import Zombie
                    # Scale health/speed based on wave
                    health = ZOMBIE_HEALTH + (self.current_wave * 10)
                    speed = ZOMBIE_SPEED + (self.current_wave * 2)
                    Zombie(self.game, x, y, health, speed)
                    self.zombies_to_spawn -= 1
                    break
