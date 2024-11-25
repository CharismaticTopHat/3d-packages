import pygame
from pygame.locals import *
from Cubo import Cubo

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Lifter:
    def __init__(self, dim, vel, textures):
        self.dim = dim
        # Se inicializa una posicion aleatoria en el tablero
        self.position = [
            random.randint(-dim, -75),  # Posición en X
            10,                         # Posición en Y
            dim-10                      # Posición en Z
        ]
        #self.position = [0, 6, 0]
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenandolas en el vector position

        # Se inicializa un vector de direccion aleatorio
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-1, 1) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.angle = 0
        self.vel = vel
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de direccion

        # Arreglo de texturas
        self.textures = textures

        # Control variables for platform movement
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False

        #Control variable for collisions
        self.radiusCol = 5

        #Control variables for animations
        self.status = 0
        self.trashID = -1
        #0 = searching
        #1 = lifting
        #2 = delivering
        #3 = dropping
        #4 = returning

    def search(self):
        # Change direction to random
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-1, 1) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]

    def targetTrailer(self):
        # Set direction to center
        dirX = -self.position[0]
        dirZ = -self.position[2]
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]

    def updatePos(self, posX, posZ):
        self.position[0] = posX
        self.position[2] = posZ
    
    def update(self):
        if self.status == 1:
            delta = 0.01
            if self.platformHeight >= 0:
                self.targetTrailer()
                self.status = 2
            else:
                self.platformHeight += delta
        elif self.status == 2:
            if (self.position[0] <= 10 and self.position[0] >= -10) and (self.position[2] <= 10 and self.position[2] >= -10):
                self.status = 3
            else:
                newX = self.position[0] + self.Direction[0] * self.vel
                newZ = self.position[2] + self.Direction[2] * self.vel
                
                # Límite en X
                if newX - 10 < -self.dim or newX + 10 > -75:
                    self.Direction[0] *= -1
                else:
                    self.position[0] = newX
                
                # Límite en Z
                if newZ - 10 < -self.dim or newZ + 10 > self.dim:
                    self.Direction[2] *= -1
                # Área Roja
                elif newZ + 10 > 26 and self.position[0] <= -75 and self.position[0] >= -75:
                    self.Direction[2] *= -1
                else:
                    self.position[2] = newZ

                self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                if self.Direction[2] > 0:
                    self.angle = 360 - self.angle
        elif self.status == 3:
            delta = 0.01
            if self.platformHeight <= -1.5:
                self.status = 4
            else:
                self.platformHeight -= delta
        elif self.status == 4:
            if (self.position[0] <= 20 and self.position[0] >= -20) and (self.position[2] <= 20 and self.position[2] >= -20):
                self.position[0] -= (self.Direction[0] * (self.vel / 4))
                self.position[2] -= (self.Direction[2] * (self.vel / 4))
            else:
                self.search()
                self.status = 0
        else:
            # Update position
            if random.randint(1, 1000) == 69:
                self.search()
            
            newX = self.position[0] + self.Direction[0] * self.vel
            newZ = self.position[2] + self.Direction[2] * self.vel
            
            # Límite en X
            if newX - 10 < -self.dim or newX + 10 > -75:
                self.Direction[0] *= -1
            else:
                self.position[0] = newX
            
            # Límite en Z
            if newZ - 10 < -self.dim or newZ + 10 > self.dim:
                self.Direction[2] *= -1
            # Área roja
            elif newZ + 10 > 26 and self.position[0] <= -75 and self.position[0] >= -75:
                self.Direction[2] *= -1
            else:
                self.position[2] = newZ
            
            self.angle = math.acos(self.Direction[0]) * 180 / math.pi
            if self.Direction[2] > 0:
                self.angle = 360 - self.angle

            # Move platform
            delta = 0.01
            if self.platformUp:
                if self.platformHeight >= 0:
                    self.platformUp = False
                else:
                    self.platformHeight += delta
            elif self.platformDown:
                if self.platformHeight <= -1.5:
                    self.platformUp = True
                else:
                    self.platformHeight -= delta



    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.angle, 0, 1, 0)
        glScaled(5, 8, 6)
        glColor3f(1.0, 1.0, 1.0)
        # front face
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, 1)

        # 2nd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -1, 1)

        # 3rd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -1, -1)

        # 4th face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, -1)

        # top
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)
        glEnd()

        # Head

        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)
        head = Cubo(self.textures, 0)
        head.draw()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Wheels
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        glPushMatrix()
        glTranslatef(-1.2, -1, 1)
        glScaled(0.6, 0.6, 0.6)
        glColor3f(1.0, 1.0, 1.0)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, 1)
        glScaled(0.6, 0.6, 0.6)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, -1)
        glScaled(0.6, 0.6, 0.6)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-1.2, -1, -1)
        glScaled(0.6, 0.6, 0.6)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Lifter
        glPushMatrix()
        if self.status == 1 or self.status == 2 or self.status == 3:
            self.drawTrash()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, self.platformHeight, 0)  # Up and down
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(3, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(3, 1, 1)
        glEnd()
        glPopMatrix()
        glPopMatrix()

    def drawTrash(self):
        glPushMatrix()
        glTranslatef(2, (self.platformHeight + 1.5), 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[3])

        glBegin(GL_QUADS)

        # Front face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, 1)

        # Back face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, -1)

        # Left face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, 1)

        # Right face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, -1, -1)

        # Top face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, -1)

        # Bottom face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, -1, -1)

        glEnd()
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()