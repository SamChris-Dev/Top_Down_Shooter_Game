import math
import pygame
from collections import deque
from core.settings import TILESIZE

def heuristic(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

class FlowField:
    def __init__(self, game):
        self.game = game
        self.grid_width = game.grid_width
        self.grid_height = game.grid_height
        self.flow_grid = [[pygame.math.Vector2(0, 0) for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.target_grid_pos = None

    def update_field(self, target_grid_pos):
        # Only recalculate if the target has actually moved to a new grid cell
        if self.target_grid_pos == target_grid_pos:
            return 
            
        self.target_grid_pos = target_grid_pos

        # 1. Generate Integration Field (BFS/Dijkstra)
        cost_grid = [[float('inf') for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        queue = deque()
        
        tx, ty = target_grid_pos
        if 0 <= tx < self.grid_width and 0 <= ty < self.grid_height:
            cost_grid[ty][tx] = 0
            queue.append((tx, ty))

        # Neighbors: N, S, E, W, NE, NW, SE, SW
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1)]
        
        while queue:
            cx, cy = queue.popleft()
            current_cost = cost_grid[cy][cx]

            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    if self.game.pathfinding_grid[ny][nx] == '1':
                        continue # Wall
                        
                    # Diagonal wall check (prevent cutting corners)
                    if dx != 0 and dy != 0:
                        if self.game.pathfinding_grid[cy+dy][cx] == '1' or self.game.pathfinding_grid[cy][cx+dx] == '1':
                            continue

                    move_cost = 1.414 if dx != 0 and dy != 0 else 1
                    new_cost = current_cost + move_cost

                    if new_cost < cost_grid[ny][nx]:
                        cost_grid[ny][nx] = new_cost
                        queue.append((nx, ny))

        # 2. Generate Vector Flow Field
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.game.pathfinding_grid[y][x] == '1':
                    continue

                min_cost = cost_grid[y][x]
                best_dir = pygame.math.Vector2(0, 0)

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                        if self.game.pathfinding_grid[ny][nx] == '1':
                            continue
                            
                        # Diagonal wall check (prevent flowing through corners)
                        if dx != 0 and dy != 0:
                            if self.game.pathfinding_grid[y+dy][x] == '1' or self.game.pathfinding_grid[y][x+dx] == '1':
                                continue
                                
                        if cost_grid[ny][nx] < min_cost:
                            min_cost = cost_grid[ny][nx]
                            best_dir = pygame.math.Vector2(dx, dy).normalize()
                
                self.flow_grid[y][x] = best_dir

    def get_dir(self, pos):
        """O(1) lookup of the flow direction for a given world position."""
        grid_x = int(pos.x // TILESIZE)
        grid_y = int(pos.y // TILESIZE)
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.flow_grid[grid_y][grid_x]
        return pygame.math.Vector2(0, 0)
