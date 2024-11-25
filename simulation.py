import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import *

import math
import random
import requests
# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Lifter import Lifter
from Package import Package
from Trailer import Trailer

URL_BASE = "http://localhost:8000"
r = requests.post(URL_BASE+ "/simulations", allow_redirects=False)
datos = r.json()
LOCATION = datos["Location"]
robotsX = datos["robots"][0]["pos"][0]
robotsZ = datos["robots"][0]["pos"][1]
boxesX = datos["boxes"][0]["pos"][0]
boxesZ = datos["boxes"][0]["pos"][1]

screen_width = 500
screen_height = 500
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=1800.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X=200.0
EYE_Y=150.0
EYE_Z=200.0
CENTER_X=0
CENTER_Y=0
CENTER_Z=0
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
#Pantalla de Ejecución
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
#Dimension del plano
DimBoard = 300
#Procesado en Webapi
URL_BASE = "http://localhost:8000"

# Variables para el control del observador
theta = 0.0
radius = 300

trailer = []
lifters = {}
packages = {}

# Arreglo para el manejo de texturas
textures = []
filenames = ["Plataformas/bars.jpg","Plataformas/wheel.jpeg", "Plataformas/machine.jpg","Plataformas/Cardboard.svg", "Plataformas/Wall.jpg", "Plataformas/TrailerWall.svg", "Plataformas/Ceiling.jpg", "Plataformas/piso_bodega.jpg", "Plataformas/zona_carga2.jpeg"]

pygame.init()

def fetch_data():
    """Fetch data from server and handle errors."""
    try:
        response = requests.post(URL_BASE + "/simulations", allow_redirects=False)
        response.raise_for_status()
        datos = response.json()
        lifters_data = datos["robots"]
        boxes_data = datos["boxes"]
        location = datos["Location"]
        return lifters_data, boxes_data, location
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None, None

def update_data(location):
    """Update data from server using the specified location."""
    try:
        response = requests.get(URL_BASE + location)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error updating data: {e}")
        return None

def initialize_objects(lifters_data, boxes_data):
    """Initialize robot, box, and storage objects based on the server data."""
    for i, rob in enumerate(lifters_data):
        lifters[f"l{i}"] = Lifter(DimBoard, 0.7, textures)
    for i, _ in enumerate(boxes_data):
        packages[f"p{i}"] = Package(DimBoard,1,textures,3)

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

def Texturas(filepath):
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Packages")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    for i in filenames:
        Texturas(i)
        
    trailer.append(OBJ("truck.obj", swapyz=True))
    trailer[0].generate()
        
def planoText():
    # activate textures
    glColor(1.0, 1.0, 1.0)
    #glEnable(GL_TEXTURE_2D)
    # front face
    #glBindTexture(GL_TEXTURE_2D, textures[0])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    
    glEnd()
    # glDisable(GL_TEXTURE_2D)
                

def display(lifters_data, boxes_data):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Se los Montacargas
    for i, _ in enumerate(lifters_data):
        lifter = lifters[f"l{i}"]
        lifter.draw()
    
    for i, _ in enumerate(boxes_data):
        package = packages[f"p{i}"]
        package.draw()

    #trailer = Trailer(textures)
    #trailer.draw()

    # Área de Montacargas
    '''
    glEnable(GL_TEXTURE_2D)  # Activar las texturas
    glBindTexture(GL_TEXTURE_2D, textures[7])
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 2, 75) 
    glTexCoord2f(1.0, 0.0) 
    glVertex3d(-75, 2, 75)   
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-75, 2, DimBoard)  
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 2, DimBoard)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    '''
    # Área de Cajas
    glEnable(GL_TEXTURE_2D)  # Activar las texturas
    glBindTexture(GL_TEXTURE_2D, textures[8])
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 2, -DimBoard)
    glTexCoord2f(1.0, 0.0) 
    glVertex3d(-75, 2, -DimBoard)
    glTexCoord2f(1.0, 1.0) 
    glVertex3d(-75, 2, -DimBoard + (DimBoard - 75))
    glTexCoord2f(0.0, 1.0) 
    glVertex3d(-DimBoard, 2, -DimBoard + (DimBoard - 75))
    glEnd()

    #Área de Ruta
    glEnable(GL_TEXTURE_2D)  # Activar las texturas
    glBindTexture(GL_TEXTURE_2D, textures[7])
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 1, DimBoard)    
    glTexCoord2f(1.0, 0.0)       
    glVertex3d(-75, 1, DimBoard) 
    glTexCoord2f(1.0, 1.0)                 
    glVertex3d(-75, 1, -DimBoard)
    glTexCoord2f(0.0, 1.0)           
    glVertex3d(-DimBoard, 1, -DimBoard)    
    glEnd()
    glBegin(GL_QUADS)
    glVertex3d(0, 1, 26)          
    glVertex3d(-75, 1, 26)                 
    glVertex3d(-75, 1, 0)          
    glVertex3d(0, 1, 0)    
    glEnd()
    glDisable(GL_TEXTURE_2D)


    # Dibujar Plano Inferior
    planoText()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, -1, -DimBoard)
    glVertex3d(-DimBoard, -1, DimBoard)
    glVertex3d(DimBoard, -1, DimBoard)
    glVertex3d(DimBoard, -1, -DimBoard)
    glEnd()
    
    wall_height = 200.0  # Altura de Paredes
    
    #Dibujar Plano Superior
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[6])
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, wall_height, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, wall_height, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, wall_height, -DimBoard)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glColor3f(0.8, 0.8, 0.8)  # Light gray color for walls
    
    # Paredes Exteriores
    # Pared Izquierda
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[4])
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-DimBoard, wall_height, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, wall_height, -DimBoard)
    glEnd()
    
    # Pared Derecha
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, wall_height, -DimBoard)
    glEnd()
    
    # Pared Frontal
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, wall_height, DimBoard)
    glEnd()
    
    # Pared Trasera
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, -DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, wall_height, -DimBoard)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glPushMatrix()  
    #correcciones para dibujar el objeto en plano XZ
    #esto depende de cada objeto
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    glTranslatef(0.0, 200.0, 25.0)
    glScalef(50.0,50.0,50.0)
    trailer[0].render()  
    glPopMatrix()
    
    pygame.display.flip()
    
def lookAt():
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = EYE_X * math.cos(rad) + EYE_Z * math.sin(rad)
    newZ = -EYE_X * math.sin(rad) + EYE_Z * math.cos(rad)
    gluLookAt(newX,EYE_Y,newZ,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)

def handleInput():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 1.0
        lookAt()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta -= 1.0
        lookAt()
    if keys[pygame.K_UP]:
        EYE_Y += 1.0
        lookAt()
    
    if keys[pygame.K_DOWN]:
        EYE_Y -= 1.0
        lookAt()


def init_opengl():
    """Initialize OpenGL settings."""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Packages")
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-100, 1000, -100, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0, 0, 0, 0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glShadeModel(GL_FLAT)
    
    lifters_data, boxes_data, location = fetch_data()
    if lifters_data:
        initialize_objects(lifters_data, boxes_data)
        init_opengl()

        # Set your desired update interval and frame delay here
        UPDATE_INTERVAL = 1  # Update data every 500 milliseconds
        FRAME_DELAY = 1       # Frame delay set to 30 milliseconds

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            handleInput()
            Axis()
            display(lifters_data, boxes_data, storages_data)

            # Update data every UPDATE_INTERVAL milliseconds
            if pygame.time.get_ticks() % UPDATE_INTERVAL == 0:
                new_data = update_data(location)
                if new_data:
                    robots_data = new_data["robots"]
                    boxes_data = new_data["boxes"]
                    storages_data = new_data["storages"]
            # Reduce delay to FRAME_DELAY for a faster frame rate
            pygame.time.wait(FRAME_DELAY)

    pygame.quit()