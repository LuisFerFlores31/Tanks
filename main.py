# ---------- main.py ----------

import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

# Asumimos que Cubo.py, objloader.py y Bala.py están en la misma carpeta que main.py:
from Cubo import Cubo
from objloader import OBJ
from Bala import Bala, update_and_collide_bullets  # Importamos la clase y la función


# ---------------- Configuración inicial ----------------

screen_width  = 1200
screen_height =  800

# Parámetros de cámara
FOVY  = 103.0
ZNEAR =   1.0
ZFAR  = 900.0

# Posición inicial del jugador (cámara)
EYE_X, EYE_Y, EYE_Z = 0.0, 15.6, 0.0
CENTER_X, CENTER_Y, CENTER_Z = 1.0, 15.0, 0.0
UP_X, UP_Y, UP_Z = 0, 1, 0

# Dimensiones del “mundo” (límite del tablero)
DimBoard = 200

# Vector direccional “hacia dónde mira” el jugador
dir = [1.0, 0.0, 0.0]
theta = 0.0
total_theta = -90.0  # Ángulo total para rotar el modelo 3D del tanque

# Lista de cubos (tanques “simplificados” para colisiones)
cubos = []
ncubos = 50

# Un “jugador” (instancia de Cubo) que usamos para chequear colisiones con los cubos
player = Cubo(DimBoard, 1.0, 5.0)

# Lista para almacenar los modelos 3D cargados con OBJ
objetos = []

# Lista global de balas activas
bullets = []


# -------------------------------------------------------
#  Función para crear / disparar una bala nueva (ajustada en altura)
# -------------------------------------------------------
def shoot_bullet(bullets_list):
    """
    Crea una nueva Bala partiendo de la posición actual del tanque (jugador),
    pero coloca su altura (spawn_y) de modo que parezca salir del cañón del tanque,
    es decir, justo encima del cubo del jugador, no a la altura de la cámara.
    """
    # La cámara está en EYE_Y = 15.6, pero el tanque “jugador” (player) alcanza
    # hasta y = player.Position[1] + player.scale (por cómo se define el cubo).
    spawn_x = EYE_X + dir[0] * 2.0

    # Se ajusta spawn_y para que quede sobre la parte superior del cubo “player”
    spawn_y = player.Position[1] + player.scale

    spawn_z = EYE_Z + dir[2] * 2.0
    start_pos = [spawn_x, spawn_y, spawn_z]

    # Dirección = mismo vector dir, normalizado y escalado dentro de Bala.__init__
    # Usamos speed=6.0 y side=2.0 (bala más grande y más lenta).
    new_bullet = Bala(start_pos, [dir[0], 0.0, dir[2]], speed=6.0, side=2.0)
    bullets_list.append(new_bullet)


# -------------------------------------------------------
#  Funciones auxiliares (Axis, lookat, Init, display)
# -------------------------------------------------------

def Axis():
    """
    Dibuja los ejes X (rojo), Y (verde) y Z (azul).
    """
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
    """
    Inicializa Pygame, OpenGL y carga la escena:
     - Configura la cámara
     - Crea los cubos “tanques de colisión”
     - Carga el modelo 3D del tanque (Tank.obj + Tank.mtl)
     - Configura iluminación básica
    """
    pygame.init()
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: tanques con OBJ y disparos")

    # Proyección perspectiva
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    # Vista de la cámara
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

    # Crear cubos de colisión
    for i in range(ncubos):
        c = Cubo(DimBoard, 1.0, 5.0)
        cubos.append(c)

    # Cada cubo recibe la lista completa para detección mutua de colisiones
    for obj in cubos:
        obj.getCubos(cubos)

    # Configuración de iluminación simple
    glLightfv(GL_LIGHT0, GL_POSITION,  (0, 200, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,   (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,   (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

    # ----------------------------
    # Carga del modelo OBJ del tanque
    # ----------------------------
    try:
        tank_model = OBJ("Tank.obj", swapyz=True)
        tank_model.generate()
        objetos.append(tank_model)
    except FileNotFoundError as e:
        print("No se pudo cargar el OBJ del tanque:", e)
        # Si falla, el programa continúa pero no se renderizará el tanque 3D


def lookat():
    """
    Actualiza la matriz de vista de la cámara según la nueva dirección `dir`.
    """
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


def display():
    """
    Limpia pantalla, dibuja ejes, piso, cubos de colisión, tanque 3D y balas.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()

    # Piso gris
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0,  DimBoard)
    glVertex3d( DimBoard, 0,  DimBoard)
    glVertex3d( DimBoard, 0, -DimBoard)
    glEnd()

    # Dibujar y actualizar cubos de colisión
    for obj in cubos:
        obj.draw()
        obj.update()

    # Dibujar el tanque OBJ en la posición del jugador
    if objetos:
        glPushMatrix()
        glTranslatef(EYE_X, 0.0, EYE_Z)          # Posicionar en la cámara/jugador
        glRotatef(total_theta, 0.0, 1.0, 0.0)    # Rotación sobre Y según total_theta
        glRotatef(-90.0, 1.0, 0.0, 0.0)          # Alineación inicial (depende del modelo)
        glScale(0.6, 0.6, 0.6)                   # Escalar el tamaño para que sea visible
        objetos[0].render()
        glPopMatrix()

    # Dibujar cada bala viva
    for b in bullets:
        b.draw()


# ----------------------
#   Bucle principal
# ----------------------

Init()
done = False

while not done:
    keys = pygame.key.get_pressed()

    # --------------------------------------------------
    # A) Movimiento del jugador con flechas
    # --------------------------------------------------

    # Avanzar
    if keys[pygame.K_UP]:
        next_x = EYE_X + dir[0]
        next_z = EYE_Z + dir[2]

        # Actualizamos el “player” (Cubo) para colisiones
        player.Position[0] = EYE_X
        player.Position[2] = EYE_Z
        player.Direction[0] = dir[0]
        player.Direction[2] = dir[2]

        if not player.Detcol():
            # Revisamos colisión con los cubos
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

    # Retroceder
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

    # Rotar jugador a la izquierda
    if keys[pygame.K_LEFT]:
        theta =  1
        total_theta += 1
        lookat()

    # Rotar jugador a la derecha
    if keys[pygame.K_RIGHT]:
        theta = -1
        total_theta -= 1
        lookat()

    # --------------------------------------------------
    # B) Captura de eventos: cerrar ventana y disparo
    # --------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        # Al pulsar SPACE, disparamos una bala (más grande y más lenta)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot_bullet(bullets)

    # --------------------------------------------------
    # C) Actualizar estado de todas las balas (movimiento + colisiones)
    # --------------------------------------------------
    update_and_collide_bullets(bullets, cubos, DimBoard)

    # --------------------------------------------------
    # D) Render de toda la escena (cubos, tanque y balas)
    # --------------------------------------------------
    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
