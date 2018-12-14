# -*- coding: UTF-8 -*-

import pygame
import pygame.freetype

from pygame.locals import *


class Text(pygame.sprite.Sprite):
    def __init__(self, text, pos=(0, 0), font=None, size=(24, 24), fg=(0, 0, 0), bg=None):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.freetype.Font(font, size=size, font_index=0, resolution=0, ucs4=False)
        self.image, self.rect = None, None
        self.text, self.fg, self.bg, self.size, self.pos = text, fg, bg, size, pos
        self.render(text, fgcolor=fg, bgcolor=bg, style=0, rotation=0, size=size)

    def render(self, *args, **kwargs):
        if self.rect is not None:
            old_pos = self.rect.center
        else:
            old_pos = self.pos
        self.image = self.font.render(*args, **kwargs)[0]
        self.rect = self.image.get_rect()
        self.rect.center = old_pos
        return self.image, self.rect

    def update_text(self, text):
        self.text = text
        self.render(text, fgcolor=self.fg, bgcolor=self.bg, style=0, rotation=0, size=self.size)

    def set_font(self, *args, **kwargs):
        self.font = pygame.freetype.Font(*args, **kwargs)
        self.render(self.text, fgcolor=self.fg, bgcolor=self.bg, style=0, rotation=0, size=self.size)
