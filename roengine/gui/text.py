# -*- coding: UTF-8 -*-

import pygame
import pygame.freetype

from pygame.locals import *


class Text(pygame.sprite.Sprite):
    def __init__(self, text, pos=(0, 0), font=None, size=0, fg=(0, 0, 0), bg=None):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.freetype.Font(font, size=size, font_index=0, resolution=0, ucs4=False)
        self.pos = pos
        self.image, self.rect = self.render(text, fgcolor=fg, bgcolor=bg, style=0, rotation=0, size=(48, 24))
        self.text, self.fg, self.bg = text, fg, bg

    def render(self, *args, **kwargs):
        self.image = self.font.render(*args, **kwargs)[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        return self.image, self.rect

    def set_font(self, *args, **kwargs):
        self.font = pygame.freetype.Font(*args, **kwargs)
        self.render(self.text, fgcolor=self.fg, bgcolor=self.bg, style=0, rotation=0, size=(24, 24))
