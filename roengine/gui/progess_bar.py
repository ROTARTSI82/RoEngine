# -*- coding: UTF-8 -*-

import pygame

__all__ = ["ProgessBar"]


class ProgessBar(pygame.sprite.Sprite):
    def __init__(self, maxval, val, size, width, colors=((255, 0, 0), (0, 0, 0))):
        pygame.sprite.Sprite.__init__(self)
        self.max = maxval
        self.val = val
        self.size = size
        self.width = width
        self.cols = colors

        self.image = pygame.Surface([self.size[0] + self.width[0] * 2, self.size[1] + self.width[1] * 2])
        self.rate = size[0] / float(maxval)
        self.bar_width = val * self.rate
        self.bar = pygame.Surface([self.bar_width, size[1]])
        self.image.fill(colors[1])
        self.bar.fill(colors[0])
        self.image.blit(self.bar, self.width)
        self.rect = self.image.get_rect()

    def update(self):
        self.val = min(self.max, max(0, self.val))
        self.image = pygame.Surface([self.size[0] + self.width[0] * 2, self.size[1] + self.width[1] * 2])
        oldcenter = self.rect.center
        self.rate = self.size[0] / float(self.max)
        self.bar_width = self.val * self.rate
        self.bar = pygame.Surface([self.bar_width, self.size[1]])
        self.image.fill(self.cols[1])
        self.bar.fill(self.cols[0])
        self.image.blit(self.bar, self.width)
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
