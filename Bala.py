import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Bala:
    def __init__(self, start_pos, direction, speed=5.0, size=1.0):
        #donde start_pos es la lista [x, y, z] (coordenadas iniciales)
        #donde direction es la lista [dx, 0, dz] (dirección antes de normalizar)
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

        self.size = size

        self.radio = math.sqrt(self.size * self.size + self.size * self.size) / 2.0

        self.alive = True

    def update(self):
        if not self.alive:
            return

        self.pos[0] += self.dir[0]
        self.pos[2] += self.dir[2]

    def draw(self):
        if not self.alive:
            return

        half = self.size / 2.0
        x, y, z = self.pos

        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(self.size, self.size, self.size)
        glColor3f(1.0, 0.0, 0.0)  

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
                self.alive = False
                return i
        return -1
