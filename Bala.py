import math
from OpenGL.GL import *

class Bala:
    def __init__(self, start_pos, direction, speed=6.0, side=2.0):
        #start_pos es la lista [x, y, z] (coordenadas iniciales)
        #direction es la lista [dx, 0, dz] (antes de normalizar)
        self.pos = [start_pos[0], start_pos[1], start_pos[2]]
        
        mag = math.sqrt(direction[0]**2 + direction[2]**2)
        if mag != 0:
            self.dir = [
                (direction[0] / mag) * speed,
                0.0,
                (direction[2] / mag) * speed
            ]
        else:
            self.dir = [0.0, 0.0, 0.0]

        
        self.side = side
        self.radio = math.sqrt(self.side*self.side + self.side*self.side) / 2.0
        self.alive = True

    def update(self):
        if not self.alive:
            return
        self.pos[0] += self.dir[0]
        self.pos[2] += self.dir[2]

    def draw(self):
        if not self.alive:
            return

        half = self.side / 2.0
        x, y, z = self.pos

        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(self.side, self.side, self.side)
        glColor3f(1.0, 0.0, 0.0)  # rojo

        glBegin(GL_QUADS)
        
        glVertex3f(-half, -half,  half)
        glVertex3f( half, -half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f(-half,  half,  half)
       
        glVertex3f(-half, -half, -half)
        glVertex3f(-half,  half, -half)
        glVertex3f( half,  half, -half)
        glVertex3f( half, -half, -half)
        
        glVertex3f(-half, -half, -half)
        glVertex3f(-half, -half,  half)
        glVertex3f(-half,  half,  half)
        glVertex3f(-half,  half, -half)
       
        glVertex3f( half, -half, -half)
        glVertex3f( half,  half, -half)
        glVertex3f( half,  half,  half)
        glVertex3f( half, -half,  half)
       
        glVertex3f(-half,  half, -half)
        glVertex3f(-half,  half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f( half,  half, -half)
       
        glVertex3f(-half, -half, -half)
        glVertex3f( half, -half, -half)
        glVertex3f( half, -half,  half)
        glVertex3f(-half, -half,  half)
        glEnd()

        glPopMatrix()

    def check_wall_collision(self, board_limit):
        x, _, z = self.pos
        if abs(x) > board_limit or abs(z) > board_limit:
            self.alive = False

    def check_cube_collision(self, cubos_list):
        for i, cube in enumerate(cubos_list):
            dx = self.pos[0] - cube.Position[0]
            dz = self.pos[2] - cube.Position[2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < (self.radio + cube.radio):
                self.alive = False  # la bala muere
                return i
        return -1


def update_and_collide_bullets(bullets_list, cubos_list, board_limit):
    cubos_to_remove = set()

    for b in bullets_list:
        if not b.alive:
            continue

        b.update()

        b.check_wall_collision(board_limit)

        if b.alive:
            idx = b.check_cube_collision(cubos_list)
            if idx >= 0:
                cubos_to_remove.add(idx)

    if cubos_to_remove:
        nuevos_cubos = []
        for i, cube in enumerate(cubos_list):
            if i not in cubos_to_remove:
                nuevos_cubos.append(cube)
        cubos_list[:] = nuevos_cubos  
    
    bullets_list[:] = [b for b in bullets_list if b.alive]
