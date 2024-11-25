import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math
"""
1)10, 10, 10
2)50, 50, 50
3)70, 70, 70
"""

class Package:
    def __init__(self, dim, vel, textures, txtIndex):
        # Se inicializa las coordenadas de los vertices del cubo
        self.possibleSizes = [
                      [10, 10, 10],
                      [50, 50, 50],
                      [70, 70, 70]
                      ]
        self.size = self.possibleSizes[random.randint(0, len(self.possibleSizes) - 1)]
        self.vertexCoords = [
                    (0, 1, self.size[2]),
                    (self.size[0], 1, self.size[2]),
                    (self.size[0], 1, 0),
                    (0, 0, 0),
                    (0, self.size[1], self.size[2]),
                    (self.size[0], self.size[1], self.size[2]),
                    (self.size[0], self.size[1], 0),
                    (0, self.size[1], 0)
                ]

        self.elementArray = [0,1,2,3,0,3,7,4,0,4,5,1,6,2,1,5,6,5,4,7,6,7,3,2,]

        self.vertexColors = [1,1,1,1,0,0,1,1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,1,1,]

        self.dim = dim
        # Se inicializa una posicion aleatoria en el tablero
        self.position = [
            random.randint(-dim, -75),  # Posición en X
            3,                          # Posición en Y
            random.randint(-dim, -dim+(dim-75))   # Posición en Z
        ]
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenandolas en el vector position
        # ...
        # Se inicializa un vector de direccion aleatorio
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-1, 1) or 1
        magnitude = math.sqrt(dirX * dirX + dirZ * dirZ) * vel
        self.Direction = [dirX / magnitude, 0, dirZ / magnitude]
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de direccion
        # ...
        # Se cambia la maginitud del vector direccion con la variable vel
        # ...
        
        #Arreglo de texturas
        self.textures = textures

        #Index de la textura a utilizar
        self.txtIndex = txtIndex

        #Control variable for drawing
        self.alive = True
        #Control variable for Trailer
        self.in_cube = False

    def update(self):
        # Se debe de calcular la posible nueva posicion del cubo a partir de su
        # posicion acutual (position) y el vector de direccion (Direction)
        # ...
        newX = self.position[0] + self.Direction[0]
        newZ = self.position[2] + self.Direction[2]
        if newX < -self.dim or newX > self.dim:
            self.Direction[0] *= -1
        else:
            self.position[0] = newX
        if newZ < -self.dim or newZ > self.dim:
            self.Direction[2] *= -1
        else:
            self.position[2] = newZ

        # Se debe verificar que el objeto cubo, con su nueva posible direccion
        # no se salga del plano actual (DimBoard)
        # ...

    def draw(self):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.position[0], self.position[1], self.position[2])
            glScaled(0.25, 0.25, 0.25)
            glColor3f(1.0, 1.0, 1.0)

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])

            tex_coords = [
            (0.0, 0.0),
            (1.0, 0.0), 
            (1.0, 1.0), 
            (0.0, 1.0),  
            ]
            
            faces = [
                [0, 1, 2, 3],  # Cara inferior
                [4, 5, 6, 7],  # Cara superior
                [0, 1, 5, 4],  # Cara frontal
                [2, 3, 7, 6],  # Cara trasera
                [1, 2, 6, 5],  # Cara derecha
                [0, 3, 7, 4],  # Cara izquierda
            ]

            glBegin(GL_QUADS)
            for face in faces:
                for i, vertex in enumerate(face):
                    glTexCoord2f(*tex_coords[i]) 
                    glVertex3f(*self.vertexCoords[vertex])
            glEnd()

            glDisable(GL_TEXTURE_2D)

            glPopMatrix()