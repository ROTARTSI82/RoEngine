# -*- coding: UTF-8 -*-

import pygame

from roengine.util import DummySprite
from pygame.locals import *

__all__ = ['Button', 'buttons']


class _ButtonRegistry(object):
    def __init__(self):
        self.group = pygame.sprite.Group()
        self.visible_bts = pygame.sprite.Group()

    def register(self, button):
        self.group.add(button)
        self.set_visible(button, button.visible)

    def set_visible(self, button, visible):
        if visible and button not in self.visible_bts:
            self.visible_bts.add(button)
        elif not visible and (button in self.visible_bts):
            self.visible_bts.remove(button)

    def set_buttons(self, bts):
        self.visible_bts = pygame.sprite.Group()
        for bt in self.group:
            bt.clickable = False
            if bt in bts:
                self.set_visible(bt, True)
                bt.clickable = True


buttons = _ButtonRegistry()


class Button(pygame.sprite.Sprite):
    def __init__(self, image, pos=(0, 0), clickable=True, visible=True):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.clickable = clickable
        self.visible = visible
        self.self_group = pygame.sprite.GroupSingle(self)

        buttons.register(self)

    def update_event(self, event, mouse_sprite=None):
        if not self.clickable:
            return
        if mouse_sprite is None:
            mouse_sprite = DummySprite([0, 0], pygame.mouse.get_pos())
        hovering = pygame.sprite.spritecollide(mouse_sprite, self.self_group, False)
        if hovering:
            if event.type == MOUSEBUTTONDOWN:
                self.on_click_start(event)
            if event.type == MOUSEBUTTONUP:
                self.on_click_end(event)
        self.event_update(hovering)

    def event_update(self, hovering):
        pass

    def on_click_start(self, event):
        """
        Event handler

        :param event: pygame.event.Event
        :return:
        """
        pass

    def on_click_end(self, event):
        pass
