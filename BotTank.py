import math
from Bala import Bala

class BotTank:
    def __init__(self, x, z, rotation):
        self.x = x
        self.z = z
        self.rotation = rotation
        self.bullets = []
        self.last_shot_time = 0
        self.shot_cooldown = 2000  # 2 seconds between shots
        self.shooting_range = 100
        self.movement_speed = 1.0
        self.rotation_speed = 3.0

    def can_shoot_at_player(self, player_position):
        """Check if bot can shoot at player"""
        # Calculate distance to player
        dx = player_position[0] - self.x
        dz = player_position[1] - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance > self.shooting_range:
            return False
            
        # Calculate angle to player
        target_angle = math.degrees(math.atan2(dx, dz))
        angle_diff = abs((target_angle - self.rotation) % 360)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        return angle_diff <= 15

    def shoot(self, current_time):
        """Shoot a bullet if cooldown has passed"""
        if current_time - self.last_shot_time >= self.shot_cooldown:
            # Calculate direction vector based on rotation
            rads = math.radians(self.rotation)
            dir_x = math.sin(rads)
            dir_z = math.cos(rads)
            
            # Create new bullet
            new_bullet = Bala(
                [self.x, 5.0, self.z],
                [dir_x, 0.0, dir_z],
                speed=8.0,
                side=2.0
            )
            self.bullets.append(new_bullet)
            self.last_shot_time = current_time

    def update(self, player_position, obstacles, current_time):
        """Update bot's position and behavior"""
        # Calculate direction to player
        dx = player_position[0] - self.x
        dz = player_position[1] - self.z
        distance = math.sqrt(dx*dx + dz*dz)
        
        # Calculate target rotation (adjusted for model orientation)
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
        if distance > 20:  # Minimum distance to maintain
            # Normalize movement vector
            if distance > 0:
                dx = dx / distance
                dz = dz / distance
                # Apply movement
                self.x += dx * self.movement_speed
                self.z += dz * self.movement_speed
        
        # Check if can shoot at player
        if self.can_shoot_at_player(player_position):
            self.shoot(current_time)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullets that are too far
            if (abs(bullet.pos[0]) > 200 or 
                abs(bullet.pos[2]) > 200):
                self.bullets.remove(bullet) 