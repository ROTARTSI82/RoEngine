# -*- coding: UTF-8 -*-

import pygame

__all__ = ["ProgressBar"]


class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, val_range, val, size, width, colors=((255, 0, 0), (0, 0, 0))):
        pygame.sprite.Sprite.__init__(self)
        self.range = val_range
        self.val = val
        self.size = size
        self.width = width
        self.cols = colors

        self.image = pygame.Surface([self.size[0] + self.width[0] * 2, self.size[1] + self.width[1] * 2])
        self.rate = size[0] / float(val_range[1])
        self.bar_width = val * self.rate
        self.bar = pygame.Surface([self.bar_width, size[1]])
        self.image.fill(colors[1])
        self.bar.fill(colors[0])
        self.image.blit(self.bar, self.width)
        self.rect = self.image.get_rect()

    def update(self):
        self.val = min(self.range[1], max(self.range[0], self.val))
        self.image = pygame.Surface([self.size[0] + self.width[0] * 2, self.size[1] + self.width[1] * 2])
        oldcenter = self.rect.center
        self.rate = self.size[0] / float(self.range[1])
        self.bar_width = self.val * self.rate
        self.bar = pygame.Surface([self.bar_width, self.size[1]])
        self.image.fill(self.cols[1])
        self.bar.fill(self.cols[0])
        self.image.blit(self.bar, self.width)
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
