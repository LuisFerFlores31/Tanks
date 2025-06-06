# ---------- Bala.py ----------

import math
from OpenGL.GL import *

class Bala:
    """
    Cada Bala:
    - tiene posición (x, y, z)
    - tiene dirección (dx, 0, dz) normalizada y multiplicada por velocidad
    - un tamaño (side) para dibujo y para cálculo de colisión
    - un flag alive para saber si está activa o ya debe eliminarse
    """
    def __init__(self, start_pos, direction, speed=6.0, side=2.0):
        # start_pos: lista [x, y, z] (coordenadas iniciales)
        # direction: lista [dx, 0, dz] (antes de normalizar)
        self.pos = [start_pos[0], start_pos[1], start_pos[2]]
        # Normalizamos el vector (dx, dz) en XZ y luego lo escalamos por speed
        mag = math.sqrt(direction[0]**2 + direction[2]**2)
        if mag != 0:
            self.dir = [
                (direction[0] / mag) * speed,
                0.0,
                (direction[2] / mag) * speed
            ]
        else:
            self.dir = [0.0, 0.0, 0.0]

        # Tamaño de la bala (lado del cubo que la representa)
        self.side = side
        # Calculamos el radio de colisión como la mitad de la diagonal del cubo
        self.radio = math.sqrt(self.side*self.side + self.side*self.side) / 2.0

        # Flag que indica si la bala sigue en escena (True) o ya debe eliminarse (False)
        self.alive = True

    def update(self):
        """Mueve la bala según su vector self.dir."""
        if not self.alive:
            return
        self.pos[0] += self.dir[0]
        self.pos[2] += self.dir[2]

    def draw(self):
        """Dibuja la bala como un cubo rojo."""
        if not self.alive:
            return

        half = self.side / 2.0
        x, y, z = self.pos

        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(self.side, self.side, self.side)
        glColor3f(1.0, 0.0, 0.0)  # rojo

        # Dibujamos un cubo de lado 1 centrado en (0,0,0); el escalado lo deja con tamaño “side”
        glBegin(GL_QUADS)
        # Frente
        glVertex3f(-half, -half,  half)
        glVertex3f( half, -half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f(-half,  half,  half)
        # Atrás
        glVertex3f(-half, -half, -half)
        glVertex3f(-half,  half, -half)
        glVertex3f( half,  half, -half)
        glVertex3f( half, -half, -half)
        # Izquierda
        glVertex3f(-half, -half, -half)
        glVertex3f(-half, -half,  half)
        glVertex3f(-half,  half,  half)
        glVertex3f(-half,  half, -half)
        # Derecha
        glVertex3f( half, -half, -half)
        glVertex3f( half,  half, -half)
        glVertex3f( half,  half,  half)
        glVertex3f( half, -half,  half)
        # Arriba
        glVertex3f(-half,  half, -half)
        glVertex3f(-half,  half,  half)
        glVertex3f( half,  half,  half)
        glVertex3f( half,  half, -half)
        # Abajo
        glVertex3f(-half, -half, -half)
        glVertex3f( half, -half, -half)
        glVertex3f( half, -half,  half)
        glVertex3f(-half, -half,  half)
        glEnd()

        glPopMatrix()

    def check_wall_collision(self, board_limit):
        """
        Si la bala sale de los límites [-board_limit, board_limit] en X o Z,
        la marcamos como “muerta” (alive=False).
        """
        x, _, z = self.pos
        if abs(x) > board_limit or abs(z) > board_limit:
            self.alive = False

    def check_cube_collision(self, cubos_list):
        """
        Recorre todos los cubos en cubos_list. Si la distancia entre el centro
        de la bala y el centro de algún cubo es menor que (radio_bala + radio_cubo),
        marcamos alive=False y devolvemos el índice del cubo colisionado.

        Retorna:
            -1 si no hubo colisión con ningún cubo
            índice i del cubo colisionado en cubos_list en caso contrario
        """
        for i, cube in enumerate(cubos_list):
            dx = self.pos[0] - cube.Position[0]
            dz = self.pos[2] - cube.Position[2]
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < (self.radio + cube.radio):
                self.alive = False  # la bala muere
                return i
        return -1


def update_and_collide_bullets(bullets_list, cubos_list, board_limit):
    """
    Recorre todas las balas en bullets_list:
      1) Las mueve (update)
      2) Checa colisión contra paredes (límites del tablero) y las marca muertas si salen
      3) Checa colisión contra cada cubo vivo en cubos_list. Si colisiona,
         elimina la bala y el cubo (se remueve el cubo de la lista).
      4) Finalmente, descarta todas las balas con alive=False del arreglo.
    """
    cubos_to_remove = set()

    # 1) Mover y checar colisión pared/cubo
    for b in bullets_list:
        if not b.alive:
            continue

        # a) Mover
        b.update()

        # b) Paredes
        b.check_wall_collision(board_limit)

        # c) Checar colisiones con cubos
        if b.alive:
            idx = b.check_cube_collision(cubos_list)
            if idx >= 0:
                cubos_to_remove.add(idx)

    # 2) Remover cubos colisionados
    if cubos_to_remove:
        nuevos_cubos = []
        for i, cube in enumerate(cubos_list):
            if i not in cubos_to_remove:
                nuevos_cubos.append(cube)
        cubos_list[:] = nuevos_cubos  # actualizamos in‐place

    # 3) Filtrar balas muertas
    bullets_list[:] = [b for b in bullets_list if b.alive]
