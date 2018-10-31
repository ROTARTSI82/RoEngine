# -*- coding: UTF-8 -*-

import pygame
import pygame.freetype

from pygame.locals import *


font_file = None
text = pygame.compat.as_unicode(r"Hello world! \u2665!")
pos = (250, 250)

pygame.init()
screen = pygame.display.set_mode([640, 480], RESIZABLE)

font = pygame.freetype.Font(font_file, size=10, font_index=0, resolution=0, ucs4=False)
font.antialiased = True
font.vertical = True
text = font.render(text, fgcolor=(0, 255, 0), bgcolor=(255, 0, 0), style=0, rotation=0, size=(48, 24))

text = list(text)

text[0] = text[0].convert()
text[1].center = pos

alpha = 0
mode = "+"

running = True
while running:
    if mode == "+":
        alpha += 1
    else:
        alpha -= 1
    if alpha > 255 and mode == "+":
        mode = "-"
    if alpha < 0 and mode == "-":
        mode = "+"
    text[0].set_alpha(alpha)
    screen.fill([255, 255, 255])
    screen.blit(text[0], text[1])
    # pygame.draw.rect(screen, (0, 0, 0), text[1], 1)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
pygame.quit()
