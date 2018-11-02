# -*- coding: UTF-8 -*-

import pygame

from roengine.util import DummySprite
from roengine.gui import Text
from pygame.locals import *

__all__ = ['Button', 'buttons', 'CheckBox', 'CheckButton']


class _ButtonRegistry(object):
    def __init__(self):
        self.group = pygame.sprite.Group()
        self.visible_bts = pygame.sprite.Group()

    def register(self, button):
        self.group.add(button)
        self.set_visible(button, button.visible)

    def unregister(self, button):
        self.group.remove(button)
        self.visible_bts.remove(button)

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


class CheckButton(Button):
    def __init__(self, clicked=False, down=(0, 0, 255), up=(255, 255, 255), size=15, thickness=1):
        self.image = pygame.Surface([size, size]).convert()
        self.image.fill([0, 0, 0])

        self.inner = pygame.Surface([size-thickness*2, size-thickness*2]).convert()
        self.down, self.up = down, up
        self.inner.fill(down if clicked else up)

        self.clicked = clicked
        self.thickness = thickness

        self.image.blit(self.inner, [self.thickness, self.thickness])

        Button.__init__(self, self.image)

    def on_click_start(self, event):
        self.clicked ^= True
        self.inner.fill(self.down if self.clicked else self.up)
        self.image.blit(self.inner, [self.thickness, self.thickness])


class CheckBox(Button):
    def __init__(self, text):
        self.check_box = CheckButton(size=15, thickness=2)
        self.clicked = self.check_box.clicked
        buttons.unregister(self.check_box)
        self.text = Text(text)
        self.dim = [self.check_box.image.get_width()+self.text.image.get_width()+20,
                    max(self.check_box.image.get_height(), self.text.image.get_height())+10]
        self.image = pygame.Surface(self.dim, SRCALPHA, 32).convert_alpha()

        self.check_box.rect.centery = self.dim[1]/2
        self.check_box.rect.left = 5
        self.text.rect.centery = self.dim[1] / 2
        self.text.rect.left = self.check_box.rect.right + 5

        self.image.blit(self.text.image, self.text.rect)
        self.image.blit(self.check_box.image, self.check_box.rect)
        Button.__init__(self, self.image)

    def on_click_start(self, event):
        self.check_box.on_click_start(event)
        self.clicked = self.check_box.clicked
        self.image = pygame.Surface(self.dim, SRCALPHA, 32).convert_alpha()
        self.check_box.rect.centery = self.dim[1] / 2
        self.check_box.rect.left = 5
        self.text.rect.centery = self.dim[1] / 2
        self.text.rect.left = self.check_box.rect.right + 5

        self.image.blit(self.text.image, self.text.rect)
        self.image.blit(self.check_box.image, self.check_box.rect)
