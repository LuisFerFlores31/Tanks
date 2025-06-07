import math
import heapq
from collections import deque

class Node:
    def __init__(self, x, z, g_cost=0, h_cost=0):
        self.x = x
        self.z = z
        self.g_cost = g_cost  # Cost from start to current node
        self.h_cost = h_cost  # Heuristic cost from current node to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = None

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class BotTank:
    def __init__(self, x, z, rotation):
        self.x = x
        self.z = z
        self.rotation = rotation
        self.path = []
        self.current_target = None
        self.grid_size = 10  # Size of each grid cell
        self.grid = {}  # Dictionary to store grid cells and their states

    def initialize_grid(self, dim_board, obstacles):
        """Initialize the grid with obstacles"""
        for x in range(-dim_board, dim_board + 1, self.grid_size):
            for z in range(-dim_board, dim_board + 1, self.grid_size):
                self.grid[(x, z)] = self.is_obstacle(x, z, obstacles)

    def is_obstacle(self, x, z, obstacles):
        """Check if a position contains an obstacle"""
        for obstacle in obstacles:
            if abs(obstacle.Position[0] - x) < 5 and abs(obstacle.Position[2] - z) < 5:
                return True
        return False

    def get_neighbors(self, node):
        """Get valid neighboring nodes"""
        neighbors = []
        directions = [(0, self.grid_size), (self.grid_size, 0), 
                     (0, -self.grid_size), (-self.grid_size, 0)]
        
        for dx, dz in directions:
            new_x = node.x + dx
            new_z = node.z + dz
            
            if (new_x, new_z) in self.grid and not self.grid[(new_x, new_z)]:
                neighbors.append(Node(new_x, new_z))
        
        return neighbors

    def heuristic(self, node, goal):
        """Calculate heuristic cost using Manhattan distance"""
        return abs(node.x - goal.x) + abs(node.z - goal.z)

    def a_star(self, start_pos, goal_pos):
        """A* pathfinding algorithm"""
        start = Node(start_pos[0], start_pos[1])
        goal = Node(goal_pos[0], goal_pos[1])
        
        open_set = []
        closed_set = set()
        
        heapq.heappush(open_set, start)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if abs(current.x - goal.x) < self.grid_size and abs(current.z - goal.z) < self.grid_size:
                path = []
                while current:
                    path.append((current.x, current.z))
                    current = current.parent
                return path[::-1]
            
            closed_set.add((current.x, current.z))
            
            for neighbor in self.get_neighbors(current):
                if (neighbor.x, neighbor.z) in closed_set:
                    continue
                
                g_cost = current.g_cost + self.grid_size
                h_cost = self.heuristic(neighbor, goal)
                
                if neighbor not in open_set:
                    neighbor.g_cost = g_cost
                    neighbor.h_cost = h_cost
                    neighbor.f_cost = g_cost + h_cost
                    neighbor.parent = current
                    heapq.heappush(open_set, neighbor)
                else:
                    if g_cost < neighbor.g_cost:
                        neighbor.g_cost = g_cost
                        neighbor.f_cost = g_cost + neighbor.h_cost
                        neighbor.parent = current
        
        return None

    def bfs(self, start_pos, goal_pos):
        """Breadth-First Search algorithm"""
        start = Node(start_pos[0], start_pos[1])
        goal = Node(goal_pos[0], goal_pos[1])
        
        queue = deque([start])
        visited = set([(start.x, start.z)])
        
        while queue:
            current = queue.popleft()
            
            if abs(current.x - goal.x) < self.grid_size and abs(current.z - goal.z) < self.grid_size:
                path = []
                while current:
                    path.append((current.x, current.z))
                    current = current.parent
                return path[::-1]
            
            for neighbor in self.get_neighbors(current):
                if (neighbor.x, neighbor.z) not in visited:
                    visited.add((neighbor.x, neighbor.z))
                    neighbor.parent = current
                    queue.append(neighbor)
        
        return None

    def minimax(self, depth, is_maximizing, alpha, beta, position, target_position):
        """Minimax algorithm with alpha-beta pruning"""
        if depth == 0:
            return self.evaluate_position(position, target_position)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in self.get_possible_moves(position):
                eval = self.minimax(depth - 1, False, alpha, beta, move, target_position)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_possible_moves(position):
                eval = self.minimax(depth - 1, True, alpha, beta, move, target_position)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_position(self, position, target_position):
        """Evaluate the current position"""
        distance = math.sqrt((position[0] - target_position[0])**2 + 
                           (position[1] - target_position[1])**2)
        return -distance  # Negative because we want to minimize distance

    def get_possible_moves(self, position):
        """Get possible moves from current position"""
        moves = []
        directions = [(0, self.grid_size), (self.grid_size, 0), 
                     (0, -self.grid_size), (-self.grid_size, 0)]
        
        for dx, dz in directions:
            new_x = position[0] + dx
            new_z = position[1] + dz
            
            if (new_x, new_z) in self.grid and not self.grid[(new_x, new_z)]:
                moves.append((new_x, new_z))
        
        return moves

    def update(self, player_position, obstacles):
        """Update bot's position and behavior"""
        if not self.path:
            self.initialize_grid(200, obstacles)  # 200 is the DimBoard value
            self.path = self.a_star((self.x, self.z), player_position)
        
        if self.path:
            target = self.path[0]
            dx = target[0] - self.x
            dz = target[1] - self.z
            
            # Calculate rotation needed
            target_rotation = math.degrees(math.atan2(dx, dz))
            rotation_diff = (target_rotation - self.rotation) % 360
            
            # Update rotation
            if abs(rotation_diff) > 5:
                if rotation_diff > 180:
                    self.rotation -= 5
                else:
                    self.rotation += 5
            else:
                # Move towards target
                distance = math.sqrt(dx*dx + dz*dz)
                if distance > 5:
                    self.x += dx * 0.1
                    self.z += dz * 0.1
                else:
                    self.path.pop(0)  # Remove reached target from path 