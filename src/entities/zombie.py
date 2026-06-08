import pygame
import math
from core.settings import *
from systems.collision import collide_with_walls

class ZombieState:
    IDLE = 0
    PATROL = 1
    CHASE = 2
    ATTACK = 3
    DEAD = 4

class Zombie(pygame.sprite.Sprite):
    def __init__(self, game, x, y, health=ZOMBIE_HEALTH, speed=ZOMBIE_SPEED):
        self.groups = game.all_sprites, game.zombies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.orig_image = self.game.asset_manager.load_image("PNG/Zombie 1/zoimbie1_stand.png")
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()

        self.hit_rect = ZOMBIE_HIT_RECT.copy()
        self.pos = pygame.math.Vector2(x, y)
        self.hit_rect.center = self.pos
        self.rect.center = self.hit_rect.center

        self.rot = 0
        self.vel = pygame.math.Vector2(0, 0)
        self.base_speed = speed
        self.health = health
        
        # FSM State
        self.state = ZombieState.IDLE
        self.last_attack_time = 0

        self.path = []
        self.last_path_time = 0
    
    def has_line_of_sight(self):
        target_dist = self.game.player.pos - self.pos
        distance = target_dist.length()
        
        if distance > ZOMBIE_VISION_RANGE:
            return False
            
        if distance == 0:
            return True
            
        direction = target_dist.normalize()
        step_size = 15
        current_pos = pygame.math.Vector2(self.pos)
        
        for _ in range(int(distance / step_size)):
            current_pos += direction * step_size
            grid_x = int(current_pos.x // TILESIZE)
            grid_y = int(current_pos.y // TILESIZE)
            
            if 0 <= grid_x < self.game.grid_width and 0 <= grid_y < self.game.grid_height:
                if self.game.pathfinding_grid[grid_y][grid_x] == '1':
                    return False
        return True

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.state = ZombieState.DEAD
            
        if self.state == ZombieState.DEAD:
            # Could play death animation here
            self.kill()
            return
            
        target_dist = self.game.player.pos - self.pos
        distance_to_player = target_dist.length()
        
        # State transitions
        if distance_to_player < ZOMBIE_ATTACK_RANGE:
            self.state = ZombieState.ATTACK
        elif distance_to_player < ZOMBIE_VISION_RANGE and self.has_line_of_sight():
            self.state = ZombieState.CHASE
        else:
            self.state = ZombieState.IDLE # Or patrol
            
        # State Execution
        if self.state == ZombieState.ATTACK:
            self.vel = pygame.math.Vector2(0, 0)
            if now - self.last_attack_time > ZOMBIE_ATTACK_COOLDOWN:
                self.last_attack_time = now
                self.game.player.take_damage(ZOMBIE_DAMAGE)
                
        elif self.state == ZombieState.CHASE:
            self.path = []
            target_pos = self.game.player.pos
            self.move_towards(target_pos)
            
        elif self.state == ZombieState.IDLE:
            target_dir = self.game.flow_field.get_dir(self.pos)
            if target_dir.length_squared() > 0:
                target_pos = self.pos + target_dir * 100
                self.move_towards(target_pos)
            else:
                self.vel = pygame.math.Vector2(0, 0)
                
        # Always face player if moving or attacking
        if distance_to_player > 0 and self.state != ZombieState.IDLE:
            self.rot = math.degrees(math.atan2(-target_dist.y, target_dist.x))
            self.image = pygame.transform.rotate(self.orig_image, self.rot)
            self.rect = self.image.get_rect()

        # Apply Velocity
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = round(self.pos.x)
        collide_with_walls(self, self.game.walls, 'x')

        self.hit_rect.centery = round(self.pos.y)
        collide_with_walls(self, self.game.walls, 'y')

        self.rect.center = self.hit_rect.center

    def move_towards(self, target_pos):
        target_dist = target_pos - self.pos
        if target_dist.length_squared() > 0:
            direction = target_dist.normalize()
            
            # Boids algorithm: Separation
            for zombie in self.game.zombies:
                if zombie != self:
                    dist = self.pos - zombie.pos
                    if 0 < dist.length() < 50: 
                        direction += dist.normalize()

            if direction.length_squared() > 0:
                self.vel = direction.normalize() * self.base_speed
            else:
                self.vel = pygame.math.Vector2(0, 0)
