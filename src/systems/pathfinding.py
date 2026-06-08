import math
import heapq
from core.settings import TILESIZE

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
