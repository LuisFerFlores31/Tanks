import math
from Bala import Bala, update_and_collide_bullets
import heapq

class Node:
    def __init__(self, position, g_cost=0, h_cost=0, parent=None):
        self.position = position  # (x, z) tuple
        self.g_cost = g_cost  # Cost from start to current node
        self.h_cost = h_cost  # Estimated cost from current to end
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class BotTank:
    def __init__(self, x, z, rotation):
        self.x = x
        self.z = z
        self.rotation = rotation
        self.bullets = []
        self.last_shot_time = 0
        self.shot_cooldown = 1000  # 1 second between shots
        self.shooting_range = 100
        self.movement_speed = 0.7
        self.rotation_speed = 2.0
        self.radio = 2  # Reduced collision radius 10 or 8 originally
        self.health = 5  # Bot starts with 5 health points
        self.alive = True  # Flag to track if bot is alive
        self.current_path = []  # Store the current path
        self.path_update_time = 0
        self.path_update_cooldown = 1000  # Update path more frequently
        self.grid_size = 15  # Adjusted grid size
        self.min_distance = 25  # Minimum distance to maintain from player

    def heuristic(self, pos1, pos2):
        """Calculate distance between two points"""
        dx = pos1[0] - pos2[0]
        dz = pos1[1] - pos2[1]
        return math.sqrt(dx*dx + dz*dz)

    def get_neighbors(self, pos, obstacles):
        """Get valid neighboring positions"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left
        
        for dx, dz in directions:
            new_x = pos[0] + dx * self.grid_size
            new_z = pos[1] + dz * self.grid_size
            
            # Check if position is valid (not colliding with obstacles)
            valid = True
            for obstacle in obstacles:
                d_x = new_x - obstacle.Position[0]
                d_z = new_z - obstacle.Position[2]
                distance = math.sqrt(d_x * d_x + d_z * d_z)
                if distance < (self.radio + obstacle.radio * 1):  # Reduced collision check
                    valid = False
                    break
            
            if valid:
                neighbors.append((new_x, new_z))
        
        return neighbors

    def find_path(self, start_pos, end_pos, obstacles):
        """A* pathfinding algorithm"""
        # Convert 3D positions to 2D (x,z) coordinates
        start_2d = (start_pos[0], start_pos[2])
        end_2d = (end_pos[0], end_pos[2])
        
        start_node = Node(start_2d, 0, self.heuristic(start_2d, end_2d))
        open_set = [start_node]
        closed_set = set()
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if self.heuristic(current.position, end_2d) < 25:  # Adjusted threshold
                path = []
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Reverse path to get start->end
            
            closed_set.add(current.position)
            
            for neighbor_pos in self.get_neighbors(current.position, obstacles):
                if neighbor_pos in closed_set:
                    continue
                
                g_cost = current.g_cost + self.grid_size
                h_cost = self.heuristic(neighbor_pos, end_2d)
                neighbor = Node(neighbor_pos, g_cost, h_cost, current)
                
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)
        
        return []  # No path found

    def take_damage(self):
        """Handle damage taken by the bot"""
        if self.alive:
            self.health -= 1
            if self.health <= 0:
                self.alive = False
                return True  # Return True if bot is destroyed
        return False

    def can_shoot_at_player(self, player_position):
        """Check if bot can shoot at player"""
        if not self.alive:
            return False
            
        # Calculate distance to player
        dx = player_position[0] - self.x
        dz = player_position[1] - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance > self.shooting_range:
            return False
            
        # Calculate angle to player
        target_angle = math.degrees(math.atan2(dx, dz)) + 90  # Add 90 degrees to match model orientation
        angle_diff = abs((target_angle - self.rotation) % 360)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        return angle_diff <= 15  # Allow shooting if within 15 degrees of facing player

    def shoot(self, current_time):
        """Shoot a bullet if cooldown has passed"""
        if not self.alive:
            return
            
        if current_time - self.last_shot_time >= self.shot_cooldown:
            # Calculate direction vector based on rotation (adjusted for model orientation)
            rads = math.radians(self.rotation - 90)  # Subtract 90 degrees to get correct direction
            dir_x = math.sin(rads)
            dir_z = math.cos(rads)
            
            # Create new bullet
            new_bullet = Bala(
                [self.x + 5, 5.0, self.z],
                [dir_x, 0.0, dir_z],
                speed=7.0,
                side=2.0  # Tamanio
            )
            self.bullets.append(new_bullet)
            self.last_shot_time = current_time

    def check_collision(self, next_x, next_z, obstacles):
        """Check if next position would cause collision with obstacles"""
        if not self.alive:
            return True
            
        for obstacle in obstacles:
            d_x = next_x - obstacle.Position[0]
            d_z = next_z - obstacle.Position[2]
            distance = math.sqrt(d_x * d_x + d_z * d_z)
            
            if distance + 2.5 < (self.radio + obstacle.radio):
                return True
        return False

    def update(self, player_position, obstacles, current_time):
        """Update bot's position and behavior"""
        if not self.alive:
            return

        # Calculate distance to player
        dx = player_position[0] - self.x
        dz = player_position[1] - self.z
        distance_to_player = math.sqrt(dx*dx + dz*dz)

        # Update path more frequently if far from player
        if distance_to_player > self.min_distance:
            self.path_update_cooldown = 500  # Update more frequently when far
        else:
            self.path_update_cooldown = 1000  # Normal update rate when close

        # Update path periodically
        if current_time - self.path_update_time > self.path_update_cooldown:
            self.current_path = self.find_path(
                (self.x, 0, self.z),
                (player_position[0], 0, player_position[1]),
                obstacles
            )
            self.path_update_time = current_time

        # Follow path if available
        if self.current_path:
            target_pos = self.current_path[0]
            dx = target_pos[0] - self.x
            dz = target_pos[1] - self.z
            distance = math.sqrt(dx*dx + dz*dz)
            
            if distance < 12:  # Adjusted waypoint distance
                self.current_path.pop(0)
            else:
                # Calculate target rotation
                target_rotation = math.degrees(math.atan2(dx, dz)) + 90
                
                # Update rotation
                rotation_diff = (target_rotation - self.rotation) % 360
                if rotation_diff > 180:
                    rotation_diff = 360 - rotation_diff
                    self.rotation -= self.rotation_speed
                else:
                    self.rotation += self.rotation_speed
                
                # Normalize rotation
                self.rotation = self.rotation % 360
                
                # Move towards waypoint
                if distance > 0:
                    dx = dx / distance
                    dz = dz / distance
                    next_x = self.x + dx * self.movement_speed
                    next_z = self.z + dz * self.movement_speed
                    
                    if not self.check_collision(next_x, next_z, obstacles):
                        self.x = next_x
                        self.z = next_z

        # Check if can shoot at player
        if self.can_shoot_at_player(player_position):
            self.shoot(current_time)
        
        # Update bullets and handle collisions
        update_and_collide_bullets(self.bullets, obstacles, 200) 