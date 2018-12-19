# -*- coding: UTF-8 -*-

import pygame

from roengine.util import Obstacle
from roengine.gui import Text
from pygame.locals import *

__all__ = ['Button', 'buttons', 'CheckBox', 'CheckButton', 'TextBt']


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
            mouse_sprite = Obstacle([0, 0], pygame.mouse.get_pos())
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


class TextBt(Button):
    def __init__(self, image, hover='txtAuto', pos=(0, 0), is_clickable=True, visible=True):
        Button.__init__(self, image.image, pos, is_clickable, visible)
        self.normal = image
        self.hover_state = 'normal'
        self.hover_img = hover
        if hover == 'txtAuto':
            self.hover_img = Text(image.text, image.pos, None, (image.size[0]*1.25, image.size[1]*1.25),
                                  image.fg, (0, 0, 255))  # set bg to blue and make it bigger

    def event_update(self, hovering):
        if hovering and self.hover_state == 'normal':
            self.hover_state = 'hovering'
            old_pos = self.rect.center
            self.image = self.hover_img.image.copy()
            self.rect = self.image.get_rect()
            self.rect.center = old_pos
        if (not hovering) and self.hover_state == 'hovering':
            self.hover_state = 'normal'
            old_pos = self.rect.center
            self.image = self.normal.image.copy()
            self.rect = self.image.get_rect()
            self.rect.center = old_pos
