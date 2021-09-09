import socket
import time

import pygame
import math


ip = ''
with open('config.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'client' in line:
            ip = line[line.index(':')+1:].replace('\n', '').strip()
        if 'port' in line:
            port = int(line[line.index(':')+1:].replace('\n','').strip())
# networking ---------------------------------------------------------------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = ('192.168.1.5', 56789)

s.connect(serverAddr)
startingData = s.recv(2048).decode().split(',')
clientId = startingData[0]

# contains info about THIS client
sentData = {'clientId': 0, 'x': 0, 'y': 0, 'lookingDirection': 0, 'fired': 0, 'health': 0, 'otherhealth': 0}

# contains info about the OTHER client
receivedData = {'clientId': 0, 'x': 0, 'y': 0, 'lookingDirection': 0, 'fired': 0, 'health': 0, 'otherhealth': 0}
# --------------------------------------------------------------------------------------------------------------

width = 800
height = 800
disp = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

red = (255, 0, 0)
blue = (0, 0, 255)
movementspeed = 2
bulletVelocity = 0.4

thisColor = ()
otherColor = ()
if clientId == '0':
    thisColor = blue
    otherColor = red
else:
    thisColor = red
    otherColor = blue


class Player:
    def __init__(self, x, y, pointingAtAngle, color, health):
        self.x = x
        self.y = y
        self.pointingAtAngle = pointingAtAngle
        self.color = color
        self.health = health

    def __add__(self, other):
        return Player(self.x + other.x, self.y + other.y, self.angle, self.color, self.health)

    def __sub__(self, other):
        return Player(self.x - other.x, self.y - other.y, self.angle, self.color, self.health)

    def __str__(self):
        return f'x:{self.x}, y:{self.y}, color:{self.color}'


class Bullet:
    def __init__(self, x, y, initAngle, color):
        self.x = x
        self.y = y
        self.initAngle = initAngle
        self.color = color
        self.toRender = True

    def updatePos(self):
        dt = clock.get_time()
        self.x += bulletVelocity * math.cos(self.initAngle) * dt
        self.y -= bulletVelocity * math.sin(self.initAngle) * dt

    def checkCollide(self):
        for p in players:
            if p.color != self.color and self.toRender:
                if p.health - math.sqrt((p.x - self.x) ** 2 + (p.y - self.y) ** 2) > 0:
                    p.health -= 1
                    self.toRender = False


def drawPlayer(p: Player):
    # print(type(p.x))
    pygame.draw.circle(disp, p.color, (p.x, p.y), p.health)
    angle = p.pointingAtAngle
    # finding the four corner points of the turret
    # gets coords of the point at the edge of the circle where the centre vector intersects
    intersectX = p.health * 0.9 * math.cos(angle) + p.x
    intersectY = p.health * 0.9 * math.sin(angle) - p.y
    perpendicularAngle = math.radians(90) + angle
    # print(f'Angle: {math.degrees(angle)}, Perp angle: {math.degrees(perpendicularAngle)}')
    # points in clockwise order
    rectWdith = p.health * 0.5
    rectLength = p.health * 1.5
    p1 = (rectWdith * math.cos(perpendicularAngle) + intersectX, rectWdith * math.sin(perpendicularAngle) + intersectY)
    p4 = (
        rectWdith * math.cos(math.pi + perpendicularAngle) + intersectX,
        rectWdith * math.sin(math.pi + perpendicularAngle) + intersectY)
    p2 = (rectLength * math.cos(angle) + p1[0], rectLength * math.sin(angle) + p1[1])
    p3 = (rectLength * math.cos(angle) + p4[0], rectLength * math.sin(angle) + p4[1])

    # print(f'Perp angle: {math.degrees(perpendicularAngle)}')
    # print(f'Intersect X: {intersectX}, Intersect Y: {intersectY}')
    # print(f'{p1}, {p2}, {p3}, {p4}')
    points = [p1, p2, p3, p4]
    for i in range(len(points)):
        points[i] = (points[i][0], abs(points[i][1]))
    pygame.draw.polygon(disp, p.color, points)


def moveForward(p: Player, steps):
    p.x += steps * math.cos(p.pointingAtAngle)
    p.y -= steps * math.sin(p.pointingAtAngle)


def strafeLeft(p: Player, steps):
    angle = math.pi / 2 + p.pointingAtAngle
    p.x += steps * math.cos(angle)
    p.y -= steps * math.sin(angle)


def strafeRight(p: Player, steps):
    angle = math.pi / 2 + p.pointingAtAngle + math.pi
    p.x += steps * math.cos(angle)
    p.y -= steps * math.sin(angle)


thisPLayer = Player(float(startingData[1]), float(startingData[2]), float(startingData[3]), thisColor, int(startingData[5]))
otherPlayer = Player(0, 0, 0, otherColor, 0)
players = [thisPLayer, otherPlayer]
bullets = []

pygame.init()
fired = '0'
run = True
elapsedTime = 1000
elapsedTime2 = 1000
while run:
    dt = clock.get_time()
    elapsedTime += dt
    elapsedTime2 += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    # sending current info
    s.send(str.encode(
        f'{clientId},{thisPLayer.x},{thisPLayer.y},{thisPLayer.pointingAtAngle},{fired},{thisPLayer.health},{otherPlayer.health}'))
    r_data = s.recv(2048).decode().split(',')
    if fired == '1':
        fired = '0'
    # changing the 'server' player to match values
    receivedData = {'clientId': r_data[0], 'x': float(r_data[1]), 'y': float(r_data[2]), 'lookingDirection': float(r_data[3]),
                    'fired': r_data[4], 'health': int(r_data[5]), 'otherhealth': int(r_data[6])}
    # print(receivedData)
    otherPlayer.x = receivedData['x']
    otherPlayer.y = receivedData['y']
    otherPlayer.pointingAtAngle = receivedData['lookingDirection']
    otherPlayer.health = receivedData['health']
    thisPLayer.health = receivedData['otherhealth']

    # checking to see if other player has fired a bullet
    if receivedData['fired'] == '1':
        if elapsedTime2 > 1000:
            bullets.append(Bullet(otherPlayer.x, otherPlayer.y, otherPlayer.pointingAtAngle, otherPlayer.color))
            elapsedTime2 = 0

    # done syncing
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        thisPLayer.pointingAtAngle -= 0.05
    if keys[pygame.K_LEFT]:
        thisPLayer.pointingAtAngle += 0.05
    if keys[pygame.K_w]:
        moveForward(thisPLayer, movementspeed)
    if keys[pygame.K_a]:
        strafeLeft(thisPLayer, movementspeed)
    if keys[pygame.K_d]:
        strafeRight(thisPLayer, movementspeed)
    if keys[pygame.K_s]:
        moveForward(thisPLayer, -movementspeed)
    if keys[pygame.K_SPACE]:
        if elapsedTime > 1000:
            bullets.append(Bullet(thisPLayer.x, thisPLayer.y, thisPLayer.pointingAtAngle, thisPLayer.color))
            fired = "1"
            elapsedTime = 0

    disp.fill((0, 0, 0))
    for player in players:
        drawPlayer(player)

    for bullet in bullets:
        bullet.updatePos()
        bullet.checkCollide()
        if bullet.toRender:
            pygame.draw.circle(disp, bullet.color, (bullet.x, bullet.y), 7)
    pygame.display.update()
    clock.tick(60)
