import pygame
import os
import random
import marshal

pygame.init()

DOT_SIZE = 1
GENERATE = False
LOAD = 'triangle.dat'
SAVE = 'current_save.dat'

def update_points():
    global points, shape, current_point
    target = random.choice(shape)
    current_point = current_point[0] + rate*(target[0] - current_point[0]), \
                    current_point[1] + rate*(target[1] - current_point[1])
    r = pygame.Rect(current_point[0], current_point[0], DOT_SIZE, DOT_SIZE)
    r.center = current_point
    pygame.draw.rect(screen, [255, 0, 0], r)
    points.append(current_point)


screen = pygame.display.set_mode([650, 490])
screen.fill([255, 255, 255])

rate = 0.5
triangle = [[0, 480], [640, 480], [320, 0]]
# shape = [[0, 0], [0, 480], [640, 480], [640, 0]]
shape = triangle
pygame.draw.lines(screen, [0, 0, 0], True, shape, 1)
random.shuffle(shape)
if os.path.exists(LOAD):
    with open(LOAD, 'r') as fp:
        current_point, points = marshal.load(fp)
else:
    current_point = random.choice(shape)
    points = [current_point, ]
for point in points:
    r = pygame.Rect(point[0], point[0], DOT_SIZE, DOT_SIZE)
    r.center = point
    pygame.draw.rect(screen, [255, 0, 0], r)

pygame.time.set_timer(pygame.USEREVENT+1, 10000)
update_points()

running = True
while running:
    if GENERATE:
        update_points()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT+1:
            print ("Saving...")
            with open(SAVE, 'w') as fp:
                marshal.dump((current_point, points), fp)
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
with open(SAVE, 'w') as fp:
    marshal.dump((current_point, points), fp)
