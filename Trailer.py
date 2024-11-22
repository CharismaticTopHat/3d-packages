import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Cubo import Cubo

import random
import math

class Trailer:
    def __init__(self, textures):
        self.radius = 100
        self.length = 146
        self.height = 41
        self.width = 26
        self.points = [
            (0, 1, self.width),   
            (self.length, 1, self.width), 
            (self.length, 1, 0),  
            (0, 0, 0),    
            (0, self.height, self.width),  
            (self.length, self.height, self.width),
            (self.length, self.height, 0),
            (0, self.height, 0),  
        ]
        self.faces = [
            # Cara inferior
            [self.points[3], self.points[2], self.points[1], self.points[0]],
            # Cara superior
            [self.points[4], self.points[5], self.points[6], self.points[7]],
            # Cara frontal
            #[self.points[7], self.points[6], self.points[2], self.points[3]],
            # Cara trasera
            #[self.points[4], self.points[5], self.points[1], self.points[0]],
            # Cara izquierda
            #[self.points[4], self.points[7], self.points[3], self.points[0]],
            # Cara derecha
            [self.points[5], self.points[6], self.points[2], self.points[1]],
        ]
        self.textures = textures
        self.min_x = 0
        self.max_x = 100
        self.min_y = 0
        self.max_y = 30
        self.min_z = 0
        self.max_z = 100

    def trailerCollision(self, agent_position, agent_radius):
        agent_x, agent_y, agent_z = agent_position

        closest_x = max(self.min_x, min(agent_x, self.max_x))
        closest_y = max(self.min_y, min(agent_y, self.max_y))
        closest_z = max(self.min_z, min(agent_z, self.max_z))

        distance = math.sqrt(
            (closest_x - agent_x) ** 2 +
            (closest_y - agent_y) ** 2 +
            (closest_z - agent_z) ** 2
        )

        return distance < agent_radius
    
    def draw(self):
        # Contenedor
        glEnable(GL_TEXTURE_2D)  # Activar las texturas
        glBindTexture(GL_TEXTURE_2D, self.textures[5])  # Vincular la textura deseada

        glBegin(GL_QUADS)

        # Cara inferior
        glTexCoord2f(0.0, 0.0)
        glVertex3d(*self.points[3])
        glTexCoord2f(1.0, 0.0)
        glVertex3d(*self.points[2])
        glTexCoord2f(1.0, 1.0)
        glVertex3d(*self.points[1])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(*self.points[0])

        # Cara superior
        glTexCoord2f(0.0, 0.0)
        glVertex3d(*self.points[4])
        glTexCoord2f(1.0, 0.0)
        glVertex3d(*self.points[5])
        glTexCoord2f(1.0, 1.0)
        glVertex3d(*self.points[6])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(*self.points[7])

        # Cara derecha
        glTexCoord2f(0.0, 0.0)
        glVertex3d(*self.points[5])
        glTexCoord2f(1.0, 0.0)
        glVertex3d(*self.points[6])
        glTexCoord2f(1.0, 1.0)
        glVertex3d(*self.points[2])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(*self.points[1])

        glEnd()

        glDisable(GL_TEXTURE_2D)

        # Cabina
        glEnable(GL_TEXTURE_2D)  # Activar las texturas
        glBindTexture(GL_TEXTURE_2D, self.textures[5])
        glPushMatrix()
        glTranslatef(self.length+16, 25, 13.5)
        glScaled(15.5, 15.5, 15.5)
        glColor3f(1.0, 0.1, 0.0) 
        head = Cubo(self.textures, 0)
        head.draw()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Llantas
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        wheel_positions = [
            (0, 0, self.width+3),            
            (self.length+3, 0, self.width+3),   
            (self.length+3, 0, 0),           
            (0, 0, 0),                   
        ]
        for pos in wheel_positions:
            glPushMatrix()
            glTranslatef(*pos)
            glScaled(4.6, 4.6, 4.6)
            glColor3f(1.0, 1.0, 1.0)
            wheel = Cubo(self.textures, 0)
            wheel.draw()
            glPopMatrix()
        glDisable(GL_TEXTURE_2D)

