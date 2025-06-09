import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

from Cubo import Cubo
from objloader import OBJ
from Bala import Bala, update_and_collide_bullets  # Importamos la clase y la función

# Import BotTank
from BotTank import BotTank

screen_width = 1200
screen_height = 800
#vc para el obser.
FOVY=103.0
ZNEAR=1.0
ZFAR=900.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 0.0 
EYE_Y = 15.6 #Variable para ajuste de camara
EYE_Z = 0.0
CENTER_X=1.0
CENTER_Y=15.0
CENTER_Z=0.0
UP_X=0
UP_Y=1
UP_Z=0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 200

dir = [1.0, 0.0, 0.0]
theta = 0.0
total_theta = -90.0  # Tank total rotation
col = 0

# Bot tank Variables

BOT_X = DimBoard - 10
BOT_Y = 5.0
BOT_Z = DimBoard - 10
BOT_ROTATION = 120.0  # Facing towards the player (diagonally)

pygame.init()

cubos = []
ncubos = 50

# Player tank Variables
PLAYER_X = -DimBoard + 10
PLAYER_Y = 5.0
PLAYER_Z = -DimBoard + 10
PLAYER_HEALTH = 3  # Player starts with 3 health points
PLAYER_ALIVE = True  # Flag to track if player is alive

EYE_X = PLAYER_X
EYE_Y = PLAYER_Y + 10.6  # Camera height above player
EYE_Z = PLAYER_Z
CENTER_X = EYE_X + 1.0
CENTER_Y = EYE_Y - 0.6
CENTER_Z = EYE_Z

player = Cubo(DimBoard, 1.0, PLAYER_Y)
player.Position = [PLAYER_X, PLAYER_Y, PLAYER_Z]

objetos = []

bullets = []

def shoot_bullet(bullets_list):
    spawn_x = EYE_X + dir[0] * 2.0

    spawn_y = player.Position[1] + player.scale

    spawn_z = EYE_Z + dir[2] * 2.0
    start_pos = [spawn_x, spawn_y, spawn_z]

    new_bullet = Bala(start_pos, [dir[0], 0.0, dir[2]], speed=6.0, side=2.0)
    bullets_list.append(new_bullet)


# Create bot tank instance
bot = BotTank(BOT_X, BOT_Z, BOT_ROTATION)

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(-DimBoard, 0.0, 0.0)
    glVertex3f( DimBoard, 0.0, 0.0)
    glEnd()
    
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, -DimBoard, 0.0)
    glVertex3f(0.0,  DimBoard, 0.0)
    glEnd()
    
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, -DimBoard)
    glVertex3f(0.0, 0.0,  DimBoard)
    glEnd()
    glLineWidth(1.0)


def Init():
    pygame.init()
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: tanques con OBJ y disparos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        EYE_X, EYE_Y, EYE_Z,
        CENTER_X, CENTER_Y, CENTER_Z,
        UP_X, UP_Y, UP_Z
    )

    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    for i in range(ncubos):
        c = Cubo(DimBoard, 1.0, 5.0)
        cubos.append(c)

    for obj in cubos:
        obj.getCubos(cubos)

    glLightfv(GL_LIGHT0, GL_POSITION,  (0, 200, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,   (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,   (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

     # Cargar la textura del suelo
    glEnable(GL_TEXTURE_2D)
    global suelo_texture
    suelo_texture = load_texture("Juego Tanques/patterned_concrete_wall_4k.blend/textures/patterned_concrete_wall_diff_4k.jpg")
    
    # Cargar el modelo del tanque
    objetos.append(OBJ("Juego Tanques/Tank.obj", swapyz=True))
    objetos.append(OBJ("Juego Tanques/swat_tank.obj", swapyz=True))#tanque de bot
    objetos[0].generate()
    objetos[1].generate()
   

def lookat():
    global EYE_X, EYE_Z, CENTER_X, CENTER_Z, dir, theta
    rads = math.radians(theta)
    dir_x = math.cos(rads) * dir[0] + math.sin(rads) * dir[2]
    dir_z = -math.sin(rads) * dir[0] + math.cos(rads) * dir[2]
    dir[0], dir[2] = dir_x, dir_z

    CENTER_X = EYE_X + dir[0]
    CENTER_Z = EYE_Z + dir[2]
    glLoadIdentity()
    gluLookAt(
        EYE_X, EYE_Y, EYE_Z,
        CENTER_X, CENTER_Y, CENTER_Z,
        UP_X, UP_Y, UP_Z
    )


def check_tank_collision(bullet_pos, tank_pos, tank_radius):
    """Check if a bullet hits a tank"""
    dx = bullet_pos[0] - tank_pos[0]
    dz = bullet_pos[2] - tank_pos[2]
    distance = math.sqrt(dx*dx + dz*dz)
    return distance < tank_radius

def display():
    global PLAYER_ALIVE, PLAYER_HEALTH
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()

    # --- Draw the textured floor ---
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, suelo_texture)
    glColor3f(1.0, 1.0, 1.0)  # No tint
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 10.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(10.0, 10.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(10.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    # --- End floor ---

    # Draw cubes
    for obj in cubos:
        obj.draw()
        obj.update()
    
    # Draw player tank if alive
    if PLAYER_ALIVE:
        glPushMatrix()
        glTranslatef(EYE_X, 0.0, EYE_Z)
        glRotatef(total_theta, 0.0, 1.0, 0.0)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glScale(0.6, 0.6, 0.6)
        objetos[0].render()
        glPopMatrix()

    # Draw bot tank if alive
    if bot.alive:
        glPushMatrix()
        glTranslatef(bot.x, BOT_Y, bot.z + 5)
        glRotatef(bot.rotation, 0.0, 1.0, 0.0)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        glScale(3.5, 3.5, 3.5)
        objetos[1].render()
        glPopMatrix()

    # Draw bullets
    for b in bullets:
        b.draw()

    # Update bot tank
    bot.update((EYE_X, EYE_Z), cubos, pygame.time.get_ticks())
    
    # Draw bot's bullets
    for bullet in bot.bullets:
        bullet.draw()

    # Check for tank collisions with bullets
    if PLAYER_ALIVE:
        for bullet in bot.bullets[:]:  # Use slice to create a copy of the list
            if bullet.alive and check_tank_collision(bullet.pos, [EYE_X, EYE_Y, EYE_Z], 14):
                bullet.alive = False
                PLAYER_HEALTH -= 1
                if PLAYER_HEALTH <= 0:
                    PLAYER_ALIVE = False
                    print("Game Over - You Lost!")

    if bot.alive:
        for bullet in bullets[:]:  # Use slice to create a copy of the list
            if bullet.alive and check_tank_collision(bullet.pos, [bot.x, BOT_Y, bot.z], 14):
                bullet.alive = False
                if bot.take_damage():
                    print("You Win!")

def load_texture(path):
    texture_surface = pygame.image.load(path)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id


#Bucle principal
Init()
done = False

while not done:
    keys = pygame.key.get_pressed()

    if PLAYER_ALIVE:  # Only allow player movement if alive
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
                    gluLookAt(
                        EYE_X, EYE_Y, EYE_Z,
                        CENTER_X, CENTER_Y, CENTER_Z,
                        UP_X, UP_Y, UP_Z
                    )

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
                    gluLookAt(
                        EYE_X, EYE_Y, EYE_Z,
                        CENTER_X, CENTER_Y, CENTER_Z,
                        UP_X, UP_Y, UP_Z
                    )

        if keys[pygame.K_LEFT]:
            theta = 1
            total_theta += 1
            lookat()

        if keys[pygame.K_RIGHT]:
            theta = -1
            total_theta -= 1
            lookat()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and PLAYER_ALIVE:  # Only allow shooting if alive
                shoot_bullet(bullets)

    update_and_collide_bullets(bullets, cubos, DimBoard)

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()

