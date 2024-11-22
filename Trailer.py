import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math

class Trailer:
    def __init__(self, textures):
        self.radius = 100
        self.points = [
            (0, 1, 26),   
            (146, 1, 26), 
            (146, 1, 0),  
            (0, 0, 0),    
            (0, 40, 26),  
            (146, 40, 26),
            (146, 40, 0),
            (0, 40, 0),  
        ]
        self.faces = [
            # Cara inferior
            [self.points[3], self.points[2], self.points[1], self.points[0]],
            # Cara superior
            [self.points[4], self.points[5], self.points[6], self.points[7]],
            # Cara frontal
            [self.points[7], self.points[6], self.points[2], self.points[3]],
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
        glColor3f(1.0, 0.5, 0.0)
        glBegin(GL_QUADS) 
        for face in self.faces:
            for vertex in face:
                glTexCoord2f(0.0, 0.0) 
                glVertex3d(*vertex) 
        glEnd()
