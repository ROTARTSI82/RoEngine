# -*- coding: UTF-8 -*-
import pygame
from roengine import Text
import datetime
pygame.init()
screen = pygame.display.set_mode([800, 600])


def pad(x, num):
    return "0" * abs(num-len(x)) + x


class Light(pygame.sprite.Sprite):
    def __init__(self, off=(128, 128, 128), on=(255, 0, 0), pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([25, 25]).convert()
        self.image.fill(off)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.colors = on, off
        self.is_on = False

    def set_on(self, is_on):
        self.is_on = is_on
        if is_on:
            self.image.fill(self.colors[0])
        else:
            self.image.fill(self.colors[1])

    def toggle(self):
        self.set_on(self.is_on ^ True)


seconds = [Light(on=(0, 0, 255), pos=(700, i)) for i in range(100, 400, 50)]
minutes = [Light(on=(0, 255, 0), pos=(400, i)) for i in range(100, 400, 50)]
hours = [Light(on=(255, 0, 0), pos=(100, i)) for i in range(100, 400, 50)]
sec = Text("0sec", pos=(700, 550))
min = Text("0min", pos=(400, 550))
hrs = Text("0hrs", pos=(100, 550))

running = True
while running:
    n = datetime.datetime.now()
    pygame.display.set_icon(screen)
    hour = n.hour if n.hour <= 12 else n.hour - 12
    # hour = n.hour  # Military time.
    pygame.display.set_caption("%shrs %smin %ssec" % (hour, n.minute, n.second))
    min.update_text("%smin" % n.minute)
    hrs.update_text("%shrs" % hour)
    sec.update_text("%ssec" % n.second)
    values = [[i == '1' for i in pad(bin(hour)[2:], 6)], [i == '1' for i in pad(bin(n.minute)[2:], 6)],
              [i == '1' for i in pad(bin(n.second)[2:], 6)]]
    for light, val in zip(hours, values[0]):
        light.set_on(val)
    for light, val in zip(minutes, values[1]):
        light.set_on(val)
    for light, val in zip(seconds, values[2]):
        light.set_on(val)

    screen.fill([255, 255, 255])
    for light in seconds:
        screen.blit(light.image, light.rect)
    for light in hours:
        screen.blit(light.image, light.rect)
    for light in minutes:
        screen.blit(light.image, light.rect)
    screen.blit(hrs.image, hrs.rect)
    screen.blit(sec.image, sec.rect)
    screen.blit(min.image, min.rect)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
