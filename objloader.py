import os
import pygame
from OpenGL.GL import *


class OBJ:
    generate_on_init = True

    @classmethod
    def loadTexture(cls, imagefile):
        surf = pygame.image.load(imagefile)
        image = pygame.image.tostring(surf, 'RGBA', True)
        ix, iy = surf.get_rect().size

        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        return texid

    @classmethod
    def loadMaterial(cls, filename):
        contents = {}
        mtl = None
        dirname = os.path.dirname(filename)

        with open(filename, "r") as f:
            for line in f:
                if line.startswith('#'):
                    continue
                values = line.split()
                if not values:
                    continue
                if values[0] == 'newmtl':
                    mtl = contents[values[1]] = {}
                elif mtl is None:
                    raise ValueError("El archivo .mtl no comienza con 'newmtl': " + filename)
                elif values[0] == 'map_Kd':
                    mtl['map_Kd'] = values[1]
                    imagefile = os.path.join(dirname, mtl['map_Kd'])
                    mtl['texture_Kd'] = cls.loadTexture(imagefile)
                else:
                    mtl[values[0]] = list(map(float, values[1:]))

        return contents

    def __init__(self, filename, swapyz=False):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []      
        self.gl_list = 0

        dirname = os.path.dirname(filename)
        material = None

        try:
            with open(filename, "r") as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    values = line.split()
                    if not values:
                        continue
                    if values[0] == 'v':
                        v = list(map(float, values[1:4]))
                        if swapyz:
                            v = (v[0], v[2], v[1])
                        self.vertices.append(v)
                    elif values[0] == 'vn':
                        v = list(map(float, values[1:4]))
                        if swapyz:
                            v = (v[0], v[2], v[1])
                        self.normals.append(v)
                    elif values[0] == 'vt':
                        self.texcoords.append(list(map(float, values[1:3])))
                    elif values[0] in ('usemtl', 'usemat'):
                        material = values[1]
                    elif values[0] == 'mtllib':
                        mtl_path = os.path.join(dirname, values[1])
                        self.mtl = self.loadMaterial(mtl_path)
                    elif values[0] == 'f':
                        face_verts = []
                        face_norms = []
                        face_texs  = []
                        for v in values[1:]:
                            w = v.split('/')
                            face_verts.append(int(w[0]))
                            if len(w) >= 2 and w[1]:
                                face_texs.append(int(w[1]))
                            else:
                                face_texs.append(0)
                            if len(w) >= 3 and w[2]:
                                face_norms.append(int(w[2]))
                            else:
                                face_norms.append(0)
                        self.faces.append((face_verts, face_norms, face_texs, material))
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo OBJ: '{filename}'")

        if self.generate_on_init:
            self.generate()

    def generate(self):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        for face in self.faces:
            vertices, normals, texture_coords, material = face

            mtl = self.mtl.get(material, {})

            if 'texture_Kd' in mtl:
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                kd = mtl.get('Kd', [1.0, 1.0, 1.0])
                glColor3f(*kd)

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()

        glDisable(GL_TEXTURE_2D)
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def free(self):
        glDeleteLists(self.gl_list, 1)