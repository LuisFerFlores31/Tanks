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
# Import obj loader
from objloader import *

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
#Vector de direcc. del observador
dir = [1.0, 0.0, 0.0]
theta = 0.0
total_theta = -90.0  # Track total rotation
col = 0

# Bot tank Variables
BOT_X = 20
BOT_Y = 5
BOT_Z = 20
BOT_ROTATION = 45.0  # Initial rotation in degrees

pygame.init()

#cubo = Cubo(DimBoard, 1.0)
cubos = []
ncubos = 50
# Guardo un cubo como el jugador para las colisiones
player = Cubo(DimBoard, 1.0, 5.0)
# Lista para almacenar los objetos 3D
objetos = []

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

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
    
    for i in range(ncubos):
        cubos.append(Cubo(DimBoard, 1.0, 5.0))
        
    #se le pasan a los objetos el arreglo de cubos
    for obj in cubos:
        obj.getCubos(cubos)
    
    # Configuración de iluminación
    glLightfv(GL_LIGHT0, GL_POSITION,  (0, 200, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)
    
    # Cargar el modelo del tanque
    objetos.append(OBJ("Juego Tanques/Tank.obj", swapyz=True))
    objetos.append(OBJ("Juego Tanques/swat_tank.obj", swapyz=True))#tanque de bot
    objetos[0].generate()
    objetos[1].generate()

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
    Axis()
    #Se dibuja el plano gris
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    #Se dibuja cubos
    for obj in cubos:
        obj.draw()
        obj.update()
    
    # Dibujar el tanque del jugador
    glPushMatrix()
    # Posicionar el tanque en la posición del jugador (camara del jugador)
    glTranslatef(EYE_X, 0.0, EYE_Z)
    # Rotar el tanque según la dirección total (Direccion de la camara)
    glRotatef(total_theta, 0.0, 1.0, 0.0)
    # Rotación inicial para orientar el modelo
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    # Ajustar la escala del modelo
    glScale(0.6, 0.6, 0.6)
    objetos[0].render() #Render del jugador
    glPopMatrix()

    # Dibujar el tanque bot
    glPushMatrix()
    # Posicionar el tanque bot en su posición
    glTranslatef(BOT_X, BOT_Y, BOT_Z)
    # Rotar el tanque bot
    glRotatef(BOT_ROTATION, 0.0, 1.0, 0.0)
    # Rotación inicial para orientar el modelo
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    # Ajustar la escala del modelo
    glScale(3.5, 3.5, 3.5)
    objetos[1].render() #Render del tanque bot
    glPopMatrix()

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
        total_theta += 1  # Increment total rotation
        lookat()
    if keys[pygame.K_RIGHT]:
        theta = -1
        total_theta -= 1  # Decrement total rotation
        lookat()                     
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    display()

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()