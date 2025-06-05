import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import sys

sys.path.append('..')
from Cubo import Cubo
from Bala import Bala


screen_width  = 1200
screen_height =  800

FOVY   = 60.0
ZNEAR  =  1.0
ZFAR   = 900.0


EYE_X, EYE_Y, EYE_Z = 0.0, 5.0, 0.0
CENTER_X, CENTER_Y, CENTER_Z = 1.0, 5.0, 0.0
UP_X, UP_Y, UP_Z = 0, 1, 0

DimBoard = 200

dir = [1.0, 0.0, 0.0] 
theta = 0.0

cubos = []
ncubos = 50

player = Cubo(DimBoard, 1.0, 5.0)

bullets = []

#de bala.py
def shoot_bullet(bullets_list):
    spawn_x = EYE_X + dir[0] * 2.0
    spawn_y = EYE_Y
    spawn_z = EYE_Z + dir[2] * 2.0
    start_pos = [spawn_x, spawn_y, spawn_z]

    new_bala = Bala(start_pos, [dir[0], 0.0, dir[2]], speed=3.0, size=1.0)
    bullets_list.append(new_bala)

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
        new_cubos = []
        for i, cube in enumerate(cubos_list):
            if i not in cubos_to_remove:
                new_cubos.append(cube)
        cubos_list[:] = new_cubos  

    bullets_list[:] = [b for b in bullets_list if b.alive]


def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    # Eje X
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(-DimBoard, 0.0, 0.0)
    glVertex3f( DimBoard, 0.0, 0.0)
    glEnd()
    # Eje Y
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, -DimBoard, 0.0)
    glVertex3f(0.0,  DimBoard, 0.0)
    glEnd()
    # Eje Z
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, -DimBoard)
    glVertex3f(0.0, 0.0,  DimBoard)
    glEnd()
    glLineWidth(1.0)

def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Juego de Tanques")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z,
              CENTER_X, CENTER_Y, CENTER_Z,
              UP_X,    UP_Y,    UP_Z)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    for i in range(ncubos):
        c = Cubo(DimBoard, 1.0, 5.0)
        cubos.append(c)

    for obj in cubos:
        obj.getCubos(cubos)

def lookat():
    global EYE_X, EYE_Z, CENTER_X, CENTER_Z, dir, theta
    rads = math.radians(theta)
    dir_x = math.cos(rads) * dir[0] + math.sin(rads) * dir[2]
    dir_z = -math.sin(rads) * dir[0] + math.cos(rads) * dir[2]
    dir[0], dir[2] = dir_x, dir_z

    CENTER_X = EYE_X + dir[0]
    CENTER_Z = EYE_Z + dir[2]
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z,
              CENTER_X, CENTER_Y, CENTER_Z,
              UP_X,    UP_Y,    UP_Z)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    # Piso
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0,  DimBoard)
    glVertex3d( DimBoard, 0,  DimBoard)
    glVertex3d( DimBoard, 0, -DimBoard)
    glEnd()

    for obj in cubos:
        obj.draw()
        obj.update()

    for b in bullets:
        b.draw()


#Bucle principal
pygame.init()
Init()
done = False

while not done:
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        next_x = EYE_X + dir[0]
        next_z = EYE_Z + dir[2]

        player.Position[0] = EYE_X
        player.Position[2] = EYE_Z
        player.Direction[0] = dir[0]
        player.Direction[2] = dir[2]

        if not player.Detcol():
            collision = False
            for cube in cubos:
                if cube.checkPlayerCollision([next_x, EYE_Y, next_z]):
                    collision = True
                    break

            if not collision:
                EYE_X = next_x
                EYE_Z = next_z
                CENTER_X = EYE_X + dir[0]
                CENTER_Z = EYE_Z + dir[2]
                glLoadIdentity()
                gluLookAt(EYE_X, EYE_Y, EYE_Z,
                          CENTER_X, CENTER_Y, CENTER_Z,
                          UP_X,    UP_Y,    UP_Z)

    if keys[pygame.K_DOWN]:
        next_x = EYE_X - dir[0]
        next_z = EYE_Z - dir[2]

        player.Position[0] = EYE_X
        player.Position[2] = EYE_Z
        player.Direction[0] = dir[0]
        player.Direction[2] = dir[2]

        if not player.Detcol():
            collision = False
            for cube in cubos:
                if cube.checkPlayerCollision([next_x, EYE_Y, next_z]):
                    collision = True
                    break
            if not collision:
                EYE_X = next_x
                EYE_Z = next_z
                CENTER_X = EYE_X + dir[0]
                CENTER_Z = EYE_Z + dir[2]
                glLoadIdentity()
                gluLookAt(EYE_X, EYE_Y, EYE_Z,
                          CENTER_X, CENTER_Y, CENTER_Z,
                          UP_X,    UP_Y,    UP_Z)

    if keys[pygame.K_LEFT]:
        theta =  1
        lookat()
    if keys[pygame.K_RIGHT]:
        theta = -1
        lookat()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot_bullet(bullets)

    update_and_collide_bullets(bullets, cubos, DimBoard)


    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
