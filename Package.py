import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math
"""
1)3.9370, 1.9685, 1.9685
2)7.8740, 3.9370, 1.9685
3)6.2992, 3.9370, 1.5748
4)7.8740, 5.9055, 2.9528
5)5.5118, 2.7559, 2.7559
6)4.9213, 3.9370, 1.9685
7)7.4803, 3.9370, 2.5434
8)6.6929, 5.9055, 1.9685
9)8.0000, 4.0000, 2.0000
10)7.2835, 3.6418, 3.2087
"""

class Package:
    def __init__(self, dim, vel, textures, txtIndex):
        # Se inicializa las coordenadas de los vertices del cubo
        self.possibleSizes = [[3.9370, 1.9685, 1.9685],
                      [7.8740, 3.9370, 1.9685],
                      [6.2992, 3.9370, 1.5748],
                      [7.8740, 5.9055, 2.9528],
                      [5.5118, 2.7559, 2.7559],
                      [4.9213, 3.9370, 1.9685],
                      [7.4803, 3.9370, 2.5434],
                      [6.6929, 5.9055, 1.9685],
                      [8.0000, 4.0000, 2.0000],
                      [7.2835, 3.6418, 3.2087],
                      [5.0, 5.0, 5.0]]
        self.size = self.possibleSizes[random.randint(0, len(self.possibleSizes) - 1)]
        self.vertexCoords = [
                    self.size[0], self.size[1], self.size[2],    # Vertex 1
                    self.size[0], self.size[1], -self.size[2],   # Vertex 2
                    self.size[0], -self.size[1], -self.size[2],  # Vertex 3
                    self.size[0], -self.size[1], self.size[2],   # Vertex 4
                    -self.size[0], self.size[1], self.size[2],   # Vertex 5
                    -self.size[0], self.size[1], -self.size[2],  # Vertex 6
                    -self.size[0], -self.size[1], -self.size[2], # Vertex 7
                    -self.size[0], -self.size[1], self.size[2],  # Vertex 8
                ]

        self.elementArray = [0,1,2,3,0,3,7,4,0,4,5,1,6,2,1,5,6,5,4,7,6,7,3,2,]

        self.vertexColors = [1,1,1,1,0,0,1,1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,1,1,]

        self.dim = dim
        # Se inicializa una posicion aleatoria en el tablero
        self.Position = [
            random.randint(-dim, -75),  # Posición en X
            2,                          # Posición en Y
            random.randint(-dim, -75)   # Posición en Z
        ]
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenandolas en el vector Position
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
        # posicion acutual (Position) y el vector de direccion (Direction)
        # ...
        newX = self.Position[0] + self.Direction[0]
        newZ = self.Position[2] + self.Direction[2]
        if newX < -self.dim or newX > self.dim:
            self.Direction[0] *= -1
        else:
            self.Position[0] = newX
        if newZ < -self.dim or newZ > self.dim:
            self.Direction[2] *= -1
        else:
            self.Position[2] = newZ

        # Se debe verificar que el objeto cubo, con su nueva posible direccion
        # no se salga del plano actual (DimBoard)
        # ...

    def draw(self):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.Position[0], self.Position[1], self.Position[2])
            glColor3f(1.0, 1.0, 1.0)

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])

            glBegin(GL_QUADS)
            
            # Front face
            glTexCoord2f(0.0, 0.0); glVertex3f(*self.vertexCoords[0:3])
            glTexCoord2f(1.0, 0.0); glVertex3f(*self.vertexCoords[3:6])
            glTexCoord2f(1.0, 1.0); glVertex3f(*self.vertexCoords[6:9])
            glTexCoord2f(0.0, 1.0); glVertex3f(*self.vertexCoords[9:12])
            
            # Repeat similar logic for other faces using self.vertexCoords
            # Use appropriate indices to match the faces (back, left, right, top, bottom)

            glEnd()
            glDisable(GL_TEXTURE_2D)

            glPopMatrix()