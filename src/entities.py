import pygame
import math
import heapq
from settings import *

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def heuristic(a, b):
    # Euclidean distance
    return math.hypot(a[0] - b[0], a[1] - b[1])

def get_path(game, start, goal):
    # start and goal are (x, y) grid coordinates
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while frontier:
        current = heapq.heappop(frontier)[1]
        
        if current == goal:
            break
            
        # 8 directions
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            next_node = (current[0] + dx, current[1] + dy)
            
            # Check boundaries
            if 0 <= next_node[0] < game.grid_width and 0 <= next_node[1] < game.grid_height:
                # Check if it's a wall
                if game.pathfinding_grid[next_node[1]][next_node[0]] == '1':
                    continue
                    
                # Prevent cutting corners on diagonals
                if dx != 0 and dy != 0:
                    if game.pathfinding_grid[current[1]+dy][current[0]] == '1' or game.pathfinding_grid[current[1]][current[0]+dx] == '1':
                        continue
                        
                cost = 1.414 if dx != 0 and dy != 0 else 1
                new_cost = cost_so_far[current] + cost
                
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(next_node, goal)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
                    
    # Reconstruct path
    current = goal
    path = []
    if goal not in came_from:
        return [] # No path found
        
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse() # reverse to get path from start to goal
    return path

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # We pass 'game' so the player can access engine variables like Delta Time
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # Grab frames from our new spritesheet loader
        self.frames = {
            'idle': self.game.chars_spritesheet.get_image('survivor1_stand.png'),
            'stand': self.game.chars_spritesheet.get_image('survivor1_stand.png'),
            'gun': self.game.chars_spritesheet.get_image('survivor1_gun.png'),
            'machine': self.game.chars_spritesheet.get_image('survivor1_machine.png'),
            'reload': self.game.chars_spritesheet.get_image('survivor1_reload.png')
        }
        
        # Fallback if XML failed
        if not self.frames['gun']:
            self.frames['gun'] = pygame.Surface((TILESIZE, TILESIZE))
            self.frames['gun'].fill((0, 255, 0))
            self.frames['stand'] = self.frames['gun']
            self.frames['machine'] = self.frames['gun']
            self.frames['idle'] = self.frames['gun']

        self.image = self.frames['gun']
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        
        # Fixed physics hitbox that never rotates
        self.hit_rect = pygame.Rect(0, 0, 35, 35)
        
        # Exact mathematical position floats for Delta Time calculation using Vector2
        self.pos = pygame.math.Vector2(x, y)
        self.hit_rect.center = self.pos
        self.rect.center = self.hit_rect.center
        self.rot = 0
        self.last_shot = 0
        self.vx, self.vy = 0, 0
        self.health = PLAYER_HEALTH
        
        # Animation variables
        self.state = 'idle'
        self.is_running = False
        self.last_anim_update = 0
        self.anim_frame = 0

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        # Check if running
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
            # Normalize diagonal speed so you don't move faster diagonally
            self.vx *= 0.7071
            self.vy *= 0.7071

    def animate(self):
        now = pygame.time.get_ticks()
        
        # 1. Determine State
        if now - self.last_shot < 100:
            self.state = 'shooting'
        elif self.vx != 0 or self.vy != 0:
            self.state = 'running' if self.is_running else 'moving'
        else:
            self.state = 'idle'
            
        # 2. Process Animation Frames based on state
        if self.state == 'shooting':
            self.orig_image = self.frames['machine']
        elif self.state == 'idle':
            self.orig_image = self.frames['gun']
        elif self.state == 'moving' or self.state == 'running':
            # Swap between stand and gun to simulate shoulder bob/arms pumping
            anim_speed = 100 if self.state == 'running' else 200
            if now - self.last_anim_update > anim_speed:
                self.last_anim_update = now
                self.anim_frame = (self.anim_frame + 1) % 2
            
            if self.anim_frame == 0:
                self.orig_image = self.frames['gun']
            else:
                self.orig_image = self.frames['stand']

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vx > 0:
                    self.hit_rect.right = hits[0].rect.left
                if self.vx < 0:
                    self.hit_rect.left = hits[0].rect.right
                self.vx = 0
                self.pos.x = self.hit_rect.centerx
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vy > 0:
                    self.hit_rect.bottom = hits[0].rect.top
                if self.vy < 0:
                    self.hit_rect.top = hits[0].rect.bottom
                self.vy = 0
                self.pos.y = self.hit_rect.centery

    def update(self):
        self.get_keys()
        self.animate()
        
        # Mouse rotation based on the fixed position
        mouse_pos = pygame.mouse.get_pos()
        cam_x = self.game.camera.camera.x
        cam_y = self.game.camera.camera.y
        player_screen_x = self.pos.x + cam_x
        player_screen_y = self.pos.y + cam_y
        
        dx = mouse_pos[0] - player_screen_x
        dy = mouse_pos[1] - player_screen_y
        self.rot = math.degrees(math.atan2(-dy, dx))
        
        # Rotate image (it generates a new surface and a new rect)
        self.image = pygame.transform.rotate(self.orig_image, self.rot)
        self.rect = self.image.get_rect()
        
        # Update X position
        self.pos.x += self.vx * self.game.dt
        self.hit_rect.centerx = round(self.pos.x)
        self.collide_with_walls('x')
        
        # Update Y position
        self.pos.y += self.vy * self.game.dt
        self.hit_rect.centery = round(self.pos.y)
        self.collide_with_walls('y')
        
        # Lock the visual rect to the physics hitbox
        self.rect.center = self.hit_rect.center

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > BULLET_RATE:
            self.last_shot = now
            self.game.bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, self.rot)
            # Bullet(self.game, self.rect.centerx, self.rect.centery, self.rot)
            if getattr(self.game, 'shoot_snd', None):
                self.game.shoot_snd.play()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        try:
            # We use the silencer sprite as a bullet tracer since it's a nice horizontal grey cylinder
            self.orig_image = pygame.image.load("assets/PNG/weapon_silencer.png").convert_alpha()
            # Optional: Tint it yellow to look like a glowing tracer round
            self.orig_image.fill((255, 200, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except FileNotFoundError:
            self.orig_image = pygame.Surface((15, 5), pygame.SRCALPHA)
            self.orig_image.fill((255, 255, 0))
            
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        
        # Trigonometry for velocity
        self.vx = math.cos(math.radians(angle)) * BULLET_SPEED
        self.vy = -math.sin(math.radians(angle)) * BULLET_SPEED # Negative because y goes down
        
        self.spawn_time = pygame.time.get_ticks()

    def fire(self, x, y, angle):
        self.add(self.groups) # Re-add to sprite groups
        self.image = pygame.transform.rotate(self.orig_image, angle)
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.vx = math.cos(math.radians(angle)) * BULLET_SPEED
        self.vy = -math.sin(math.radians(angle)) * BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos.x += self.vx * self.game.dt
        self.pos.y += self.vy * self.game.dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
            
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class BulletPool:
    def __init__(self, game, pool_size=50):
        self.game = game
        # Pre-allocate bullet instances off-screen
        self.pool = [Bullet(game, -1000, -1000, 0) for _ in range(pool_size)]
        
        # Immediately "kill" them so they aren't updated or drawn
        for bullet in self.pool:
            bullet.kill()

    def get_bullet(self, x, y, angle):
        # Find the first inactive bullet
        for bullet in self.pool:
            if not bullet.alive():
                bullet.fire(x, y, angle)
                return bullet
        
        # Optional: Dynamically expand the pool if we run out
        new_bullet = Bullet(self.game, x, y, angle)
        self.pool.append(new_bullet)
        new_bullet.fire(x, y, angle)
        return new_bullet


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

class Zombie(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.zombies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # USE CACHED IMAGE
        self.image = self.game.zombie_img.copy() 
        self.orig_image = self.image

        try:
            self.image = pygame.image.load("assets/PNG/Zombie 1/zoimbie1_stand.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((TILESIZE, TILESIZE))
            self.image.fill((255, 0, 0)) # Red box for zombie

        self.orig_image = self.image
        self.rect = self.image.get_rect()

        self.hit_rect = pygame.Rect(0, 0, 35, 35)
        self.pos = pygame.math.Vector2(x, y)
        self.hit_rect.center = self.pos
        self.rect.center = self.hit_rect.center

        self.rot = 0
        self.vel = pygame.math.Vector2(0, 0)
        self.health = ZOMBIE_HEALTH

        self.path = []
        self.last_path_time = 0
    
    def has_line_of_sight(self):
        # Simple raycast check using distance and steps
        target_dist = self.game.player.pos - self.pos
        distance = target_dist.length()
        
        if distance == 0:
            return True
            
        direction = target_dist.normalize()
        step_size = 15 # Check every 15 pixels
        
        current_pos = pygame.math.Vector2(self.pos)
        
        # March a point forward and check if it hits a wall
        for _ in range(int(distance / step_size)):
            current_pos += direction * step_size
            
            # Check grid for wall
            grid_x = int(current_pos.x // TILESIZE)
            grid_y = int(current_pos.y // TILESIZE)
            
            # Ensure within bounds
            if 0 <= grid_x < self.game.grid_width and 0 <= grid_y < self.game.grid_height:
                if self.game.pathfinding_grid[grid_y][grid_x] == '1':
                    return False # Wall blocking view
        return True

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    self.hit_rect.right = hits[0].rect.left
                if self.vel.x < 0:
                    self.hit_rect.left = hits[0].rect.right
                self.vel.x = 0
                self.pos.x = self.hit_rect.centerx
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    self.hit_rect.bottom = hits[0].rect.top
                if self.vel.y < 0:
                    self.hit_rect.top = hits[0].rect.bottom
                self.vel.y = 0
                self.pos.y = self.hit_rect.centery

    def update(self):
        now = pygame.time.get_ticks()
        
        # ----------------------------------------
        # 1. Pathfinding & Target Selection
        # ----------------------------------------
        if self.has_line_of_sight():
            # Clear A* path and run directly at the player
            self.path = []
            target_pos = self.game.player.pos
        else:
            # Only run heavy A* math if blocked AND 500ms have passed
            if now - self.last_path_time > 500:
                self.last_path_time = now
                start_grid = (int(self.pos.x // TILESIZE), int(self.pos.y // TILESIZE))
                goal_grid = (int(self.game.player.pos.x // TILESIZE), int(self.game.player.pos.y // TILESIZE))
                
                if start_grid != goal_grid:
                    self.path = get_path(self.game, start_grid, goal_grid)
                else:
                    self.path = []

            # If an A* path exists, set the target to the next waypoint
            if self.path:
                next_tile = self.path[0]
                target_pos = pygame.math.Vector2(next_tile[0] * TILESIZE + TILESIZE / 2, next_tile[1] * TILESIZE + TILESIZE / 2)
                
                # If we reached the waypoint, pop it and aim for the next one
                if self.pos.distance_to(target_pos) < 15:
                    self.path.pop(0)
                    if self.path:
                        next_tile = self.path[0]
                        target_pos = pygame.math.Vector2(next_tile[0] * TILESIZE + TILESIZE / 2, next_tile[1] * TILESIZE + TILESIZE / 2)
                    else:
                        target_pos = self.game.player.pos
            else:
                target_pos = self.game.player.pos

        # ----------------------------------------
        # 2. Rotation & Steering 
        # ----------------------------------------
        target_dist = target_pos - self.pos

        if target_dist.length_squared() > 0:
            # Always visually face the player, even if moving sideways to a waypoint
            look_dist = self.game.player.pos - self.pos
            if look_dist.length_squared() > 0:
                self.rot = math.degrees(math.atan2(-look_dist.y, look_dist.x))
                self.image = pygame.transform.rotate(self.orig_image, self.rot)
                self.rect = self.image.get_rect()

            # Boids algorithm: Separation (push away from other zombies)
            direction = target_dist.normalize()
            for zombie in self.game.zombies:
                if zombie != self:
                    dist = self.pos - zombie.pos
                    if 0 < dist.length() < 50: 
                        direction += dist.normalize()

            if direction.length_squared() > 0:
                self.vel = direction.normalize() * ZOMBIE_SPEED
            else:
                self.vel = pygame.math.Vector2(0, 0)
        else:
            self.vel = pygame.math.Vector2(0, 0)

        # ----------------------------------------
        # 3. Apply Velocity & Handle Physics
        # ----------------------------------------
        self.pos += self.vel * self.game.dt

        # Resolve X collisions
        self.hit_rect.centerx = round(self.pos.x)
        self.collide_with_walls('x')

        # Resolve Y collisions
        self.hit_rect.centery = round(self.pos.y)
        self.collide_with_walls('y')

        # Lock the drawing rectangle to the physics rectangle
        self.rect.center = self.hit_rect.center

        # ----------------------------------------
        # 4. Death Check
        # ----------------------------------------
        if self.health <= 0:
            self.kill()
    
    
        