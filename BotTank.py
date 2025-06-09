import math
from Bala import Bala, update_and_collide_bullets

class BotTank:
    def __init__(self, x, z, rotation):
        self.x = x
        self.z = z
        self.rotation = rotation
        self.bullets = []
        self.last_shot_time = 0
        self.shot_cooldown = 2000  # 2 seconds between shots
        self.shooting_range = 100
        self.movement_speed = 0.7
        self.rotation_speed = 2.0
        self.radio = 14  # Same as player's collision radius
        self.health = 3  # Bot starts with 3 health points
        self.alive = True  # Flag to track if bot is alive

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
            
        # Calculate direction to player
        dx = player_position[0] - self.x
        dz = player_position[1] - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Calculate target rotation
        target_rotation = math.degrees(math.atan2(dx, dz)) + 90  # Add 90 degrees to align with model
        
        # Update rotation
        rotation_diff = (target_rotation - self.rotation) % 360
        if rotation_diff > 180:
            rotation_diff = 360 - rotation_diff
            self.rotation -= self.rotation_speed
        else:
            self.rotation += self.rotation_speed
            
        # Normalize rotation
        self.rotation = self.rotation % 360
        
        # Move towards player if not too close
        if distance > 30:  # Minimum distance to maintain
            # Normalize movement vector
            if distance > 0:
                dx = dx / distance
                dz = dz / distance
                # Calculate next position
                next_x = self.x + dx * self.movement_speed
                next_z = self.z + dz * self.movement_speed
                
                # Check for collisions before moving
                if not self.check_collision(next_x, next_z, obstacles):
                    self.x = next_x
                    self.z = next_z
                    self.shoot(current_time)
        
        # Check if can shoot at player
        if self.can_shoot_at_player(player_position):
            self.shoot(current_time)
        
        # Update bullets and handle collisions
        update_and_collide_bullets(self.bullets, obstacles, 200)  # 200 is the DimBoard value 