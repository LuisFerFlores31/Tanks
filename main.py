import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Cubo import Cubo

screen_width = 1200
screen_height = 800
#vc para el obser.
FOVY=60.0
ZNEAR=1.0
ZFAR=900.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 0.0
EYE_Y = 5.0
EYE_Z = 0.0
CENTER_X=1.0
CENTER_Y=5.0
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
#Vector de direcc. del observador
dir = [1.0, 0.0, 0.0]
theta = 0.0
col = 0

pygame.init()

#cubo = Cubo(DimBoard, 1.0)
cubos = []
ncubos = 50
# Guardo un cubo como el jugador para las colisiones
player = Cubo(DimBoard, 1.0, 5.0)



# def Axis():
#     glShadeModel(GL_FLAT)
#     glLineWidth(3.0)
#     #X axis in red
#     glColor3f(1.0,0.0,0.0)
#     glBegin(GL_LINES)
#     glVertex3f(X_MIN,0.0,0.0)
#     glVertex3f(X_MAX,0.0,0.0)
#     glEnd()
#     #Y axis in green
#     glColor3f(0.0,1.0,0.0)
#     glBegin(GL_LINES)
#     glVertex3f(0.0,Y_MIN,0.0)
#     glVertex3f(0.0,Y_MAX,0.0)
#     glEnd()
#     #Z axis in blue
#     glColor3f(0.0,0.0,1.0)
#     glBegin(GL_LINES)
#     glVertex3f(0.0,0.0,Z_MIN)
#     glVertex3f(0.0,0.0,Z_MAX)
#     glEnd()
#     glLineWidth(1.0)



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



def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_TEXTURE_2D)
    global suelo_texture
    suelo_texture = load_texture("Juego Tanques/patterned_concrete_wall_4k.blend/textures/patterned_concrete_wall_diff_4k.jpg")
    
    
    for i in range(ncubos):
        cubos.append(Cubo(DimBoard, 1.0, 5.0))
        
    #se le pasan a los objetos el arreglo de cubos
    for obj in cubos:
        obj.getCubos(cubos)
        
def lookat():
    global EYE_X
    global EYE_Z
    global CENTER_X
    global CENTER_Z
    global dir
    global theta
    dir_x = 0.0
    dir_z = 0.0
    rads = math.radians(theta)
    dir_x = math.cos(rads)*dir[0] + math.sin(rads)*dir[2]
    dir_z = -math.sin(rads)*dir[0] + math.cos(rads)*dir[2]
    dir[0] = dir_x
    dir[2] = dir_z
    CENTER_X = EYE_X + dir[0]
    CENTER_Z = EYE_Z + dir[2]
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
    

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #Axis()
    #Se dibuja el plano gris
    # glColor3f(0.3, 0.3, 0.3)
    # glBegin(GL_QUADS)
    # glVertex3d(-DimBoard, 0, -DimBoard)
    # glVertex3d(-DimBoard, 0, DimBoard)
    # glVertex3d(DimBoard, 0, DimBoard)
    # glVertex3d(DimBoard, 0, -DimBoard)
    # glEnd()
    glBindTexture(GL_TEXTURE_2D, suelo_texture)
    glColor3f(1.0, 1.0, 1.0)  # Sin tintado
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

    #Se dibuja cubos
    for obj in cubos:
        obj.draw()
        obj.update()
    
done = False
Init()
while not done:
    keys = pygame.key.get_pressed()
    #avanzar observador
    if keys[pygame.K_UP]: #Cambiar Colisiones
        # Calculo la nueva posicion y la guardo
        next_x = EYE_X + dir[0]
        next_z = EYE_Z + dir[2]

         # Actualizo tanto la posicion como la direccion del jugador
        player.Position[0] = EYE_X
        player.Position[2] = EYE_Z
        player.Direction[0] = dir[0]
        player.Direction[2] = dir[2]
        
        # se checa colision con el mapa
        if not player.Detcol():
            #Se checa la colision con todos los cubos y el jugador
            collision = False
            for cube in cubos:
                if cube.checkPlayerCollision([next_x, EYE_Y, next_z]):
                    collision = True
                    break
            
            # Se mueve si no hay colision
            if not collision:
                EYE_X = next_x
                EYE_Z = next_z
                CENTER_X = EYE_X + dir[0]
                CENTER_Z = EYE_Z + dir[2]
                glLoadIdentity()
                gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)

    #retroceder observador    
    if keys[pygame.K_DOWN]: #Cambiar colisiones
        #nueva pos
        next_x = EYE_X - dir[0]
        next_z = EYE_Z - dir[2]

        player.Position[0] = EYE_X
        player.Position[2] = EYE_Z
        player.Direction[0] = dir[0]
        player.Direction[2] = dir[2]
        
        # Detecta la colision con el mapa
        if not player.Detcol():
            # Checa colision con los cubos y el jugador
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
                gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)

    if keys[pygame.K_LEFT]:
        theta = 1
        lookat()
    if keys[pygame.K_RIGHT]:
        theta = -1
        lookat()                     
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True


    display()
    


    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()