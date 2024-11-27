import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import *

import math
import random
# Se carga el archivo de la clase Cubo
import sys
import requests
sys.path.append('..')
from Lifter import Lifter
from Package import Package
from Trailer import Trailer

screen_width = 500
screen_height = 500
#vc para el obser.
FOVY=60.0
ZNEAR=0.1
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
#Dimension del plano
DimBoard = 300

# Variables para el control del observador
theta = 0.0
radius = 300

trailer = []

# Arreglo para el manejo de texturas
textures = []
filenames = ["Plataformas/bars.jpg","Plataformas/wheel.jpeg", "Plataformas/machine.jpg","Plataformas/Cardboard.svg", "Plataformas/Wall.jpg", "Plataformas/TrailerWall.svg", "Plataformas/Ceiling.jpg", "Plataformas/piso_bodega.jpg", "Plataformas/zona_carga2.jpeg"]

#Llamada a Julia
URL_BASE = "http://localhost:8000"
r = requests.post(URL_BASE+ "/simulations", allow_redirects=False)
datos = r.json()
#print(datos)
LOCATION = datos["Location"]
liftersX = []
liftersZ = []
for lifter in datos["robots"]:
    liftersX.append(lifter["pos"][0])
    liftersZ.append(lifter["pos"][1])

packagesX = []
packagesZ = []
packagesHeight = []
packagesWidth = []
packagesDepth = []
#packageStatus = []
for box in datos["boxes"]:
    packagesX.append(box["pos"][0])
    packagesZ.append(box["pos"][1])
    packagesWidth.append(box["width"])
    packagesHeight.append(box["height"])
    packagesDepth.append(box["depth"])
    #packageStatus.append(box["BoxStatus"])


trailerX = []
trailerZ = []
for trail in datos["storages"]:
    trailerX.append(trail["pos"][0])
    trailerZ.append(trail["pos"][1])

lifters = {f"l{i}": Lifter(DimBoard, 0.7, textures) for i, _ in enumerate(datos["robots"])}
packages = {f"p{i}": Package(DimBoard,1,textures,3, packagesWidth[i], packagesHeight[i], packagesDepth[i]) for i, _ in enumerate(datos["boxes"])}

pygame.init()

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
    image = pygame.image.load(filepath).convert_alpha()  # Ensure image has an alpha channel
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

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    response = requests.get(URL_BASE + LOCATION)
    datos = response.json()
    
    # Se dibujan los Montacargas
    for i, lifter_data in enumerate(datos["robots"]):
        lifter = lifters[f"l{i}"]
        
        glPushMatrix()
        glTranslatef(-lifter_data["pos"][0], 0, -lifter_data["pos"][1])
        x = lifter_data["pos"][0]
        z = lifter_data["pos"][1]
        lifter.draw()
        glPopMatrix()
        print(f"Se dibujó Lifter{i} en la posición [{x},{z}]")

    # Se dibujan los Paquetes
    for i, package_data in enumerate(datos["boxes"]):
        package = packages[f"p{i}"]
        
        glPushMatrix()
        glTranslatef(package_data["pos"][0]*4, 0, package_data["pos"][1]*4)
        x = package_data["pos"][0]*4
        z = package_data["pos"][1]*4
        package.draw()
        glPopMatrix()
        print(f"Se dibujó Package{i} en la posición [{x},{z}]")
        
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
    
def lookAt():
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = EYE_X * math.cos(rad) + EYE_Z * math.sin(rad)
    newZ = -EYE_X * math.sin(rad) + EYE_Z * math.cos(rad)
    gluLookAt(newX,EYE_Y,newZ,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    
done = False
Init()
while not done:
    keys = pygame.key.get_pressed()  # Checking pressed keys
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 10.0
        lookAt()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta -= 10.0
        lookAt()
    if keys[pygame.K_UP]:
        EYE_Y += 10.0
        lookAt()
    
    if keys[pygame.K_DOWN]:
        EYE_Y -= 10.0
        lookAt()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        if event.type == pygame.QUIT:
            done = True
    display()

    display()
    pygame.display.flip()
    pygame.time.wait(100)
pygame.quit()