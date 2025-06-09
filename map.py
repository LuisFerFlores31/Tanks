import math
from Cubo import Cubo

class Map:
    def __init__(self, layout, dimBoard, scale):
        self.walls = []
        rows = len(layout)
        cols = len(layout[0]) if rows else 0
        width  = cols * scale * 2
        height = rows * scale * 2
        x_off = width  / 2 - scale
        z_off = height / 2 - scale

        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                if cell == 1:
                    w = Cubo(dimBoard, 0.0, scale)
                    x = j * scale * 2 - x_off
                    z = i * scale * 2 - z_off
                    w.Position = [x, scale, z]
                    w.Cubos = []
                    self.walls.append(w)

    def draw(self):
        for w in self.walls:
            w.draw()