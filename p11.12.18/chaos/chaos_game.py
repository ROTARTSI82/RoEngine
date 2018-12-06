import pygame
import os
import random
import marshal

pygame.init()

DOT_SIZE = 1
GENERATE = False
LOAD = 'triangle.dat'
SAVE = None


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

rate = 2.0/3
triangle = [[0, 480], [640, 480], [320, 0]]
carpet = [[0, 0], [0, 240], [0, 480], [320, 480], [640, 480], [640, 240], [640, 0], [320, 0]]
# shape = [[0, 0], [0, 480], [640, 480], [640, 0]]
shape = carpet
pygame.draw.lines(screen, [0, 0, 0], True, shape, 1)
random.shuffle(shape)
if os.path.exists(LOAD):
    with open(LOAD, 'r') as fp:
        current_point, points = marshal.load(fp)
else:
    current_point = random.choice(shape)
    points = [current_point, ]
    update_points()
for point in points:
    r = pygame.Rect(point[0], point[0], DOT_SIZE, DOT_SIZE)
    r.center = point
    pygame.draw.rect(screen, [255, 0, 0], r)

for point in shape:
    r = pygame.Rect(point[0], point[0], DOT_SIZE+2, DOT_SIZE+2)
    r.center = point
    pygame.draw.rect(screen, [0, 255, 0], r)

pygame.time.set_timer(pygame.USEREVENT+1, 10000)

running = True
while running:
    if GENERATE:
        update_points()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT+1:
            print ("Saving...")
            try:
                with open(SAVE, 'w') as fp:
                    marshal.dump((current_point, points), fp)
            except:
                print ("FAILED")
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
try:
    with open(SAVE, 'w') as fp:
        marshal.dump((current_point, points), fp)
except:
    print ("SAVE FAILED")
