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
            Bullet(self.game, self.rect.centerx, self.rect.centery, self.rot)
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

    def update(self):
        self.pos.x += self.vx * self.game.dt
        self.pos.y += self.vy * self.game.dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
            
        if pygame.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

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

        try:
            self.image = pygame.image.load("../assets/PNG/Zombie 1/zoimbie1_stand.png").convert_alpha()
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
        # Recalculate path every 500ms
        if now - self.last_path_time > 500 or not self.path:
            self.last_path_time = now
            # Get grid positions
            start_grid = (int(self.pos.x // TILESIZE), int(self.pos.y // TILESIZE))
            goal_grid = (int(self.game.player.pos.x // TILESIZE), int(self.game.player.pos.y // TILESIZE))

            # Don't pathfind if already in the same cell
            if start_grid != goal_grid:
                self.path = get_path(self.game, start_grid, goal_grid)
            else:
                self.path = []

        # 1. Pursuit Vector Logic via Waypoints
        if self.path:
            # Target is the center of the next tile in the path
            next_tile = self.path[0]
            target_pos = pygame.math.Vector2(next_tile[0] * TILESIZE + TILESIZE / 2, next_tile[1] * TILESIZE + TILESIZE / 2)

            # If we are close enough to the waypoint, move to the next one
            if self.pos.distance_to(target_pos) < 15:
                self.path.pop(0)
                if self.path:
                    next_tile = self.path[0]
                    target_pos = pygame.math.Vector2(next_tile[0] * TILESIZE + TILESIZE / 2, next_tile[1] * TILESIZE + TILESIZE / 2)
                else:
                    target_pos = self.game.player.pos
        else:
            # Fallback to direct pursuit if no path or in same cell
            target_pos = self.game.player.pos

        target_dist = target_pos - self.pos

        if target_dist.length_squared() > 0: # Avoid division by zero
            # 2. Find angle and rotate
            # We face the actual player to look scarier, even if moving towards a waypoint
            look_dist = self.game.player.pos - self.pos
            if look_dist.length_squared() > 0:
                self.rot = math.degrees(math.atan2(-look_dist.y, look_dist.x))
                self.image = pygame.transform.rotate(self.orig_image, self.rot)
                self.rect = self.image.get_rect()

            # 3. Steering - Separation from other zombies
            direction = target_dist.normalize()
            for zombie in self.game.zombies:
                if zombie != self:
                    dist = self.pos - zombie.pos
                    # If another zombie is within 50 pixels, push away from it
                    if 0 < dist.length() < 50: 
                        direction += dist.normalize()

            # 4. Normalize the combined vector and apply speed
            if direction.length_squared() > 0:
                self.vel = direction.normalize() * ZOMBIE_SPEED
            else:
                self.vel = pygame.math.Vector2(0, 0)
        else:
            self.vel = pygame.math.Vector2(0, 0)

        # 5. Apply velocity and handle collisions
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = round(self.pos.x)
        self.collide_with_walls('x')

        self.hit_rect.centery = round(self.pos.y)
        self.collide_with_walls('y')

        # 5. Lock visual rect to hit_rect
        self.rect.center = self.hit_rect.center

        # Check death
        if self.health <= 0:
            self.kill()