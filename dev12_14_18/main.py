# -*- coding: UTF-8 -*-

import logging
import warnings
import traceback

import platform
import os
import sys

import twisted

import pygame
from pygame.locals import *

import generic_logging

from CONFIG import *
from roengine import *
from data.states import *


## TODO
# Come up with a actual name...
# Optimize test_mode.py:53-62 (Do we need to update these every frame?)
# Client doesn't quit after backing out.
# Is the shield regen rate too fast?
##

__appName__ = "_UntitledApp"  # Placeholder
__version__ = 'dev01.19.19'
__author__ = "Grant Yang <rotartsi0482@gmail.com>"
__date__ = '19 January 2019'


class D12_11_18(Game):
    enter_test_mode, exit_test_mode, tick_test_mode = enter_test_mode, exit_test_mode, tick_test_mode
    enter_mult_test, exit_mult_test, tick_mult_test = enter_mult_test, exit_mult_test, tick_mult_test
    def start(self):
        pygame.init()
        self.initiated = []

        self.screen = pygame.display.set_mode(SCREEN_RES, SCREEN_FLAGS)
        self.update_rects(SCREEN_RES)

        self.hud_layer = Map(HUD_RES)
        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32)

        self.clock = pygame.time.Clock()
        self.mouse_sprite = Obstacle([10, 10], [0, 0])
        self.mouse_pos = [0, 0]

        self.quit_bt = TextBt(Text("QUIT", size=(32, 32), bg=(255, 0, 0)))
        self.quit_bt.rect.bottomright = HUD_RES[0]-12, HUD_RES[1]-12
        def quit_click(event):
            self.terminate()
        self.quit_bt.on_click_end = quit_click

        self.test_mode_bt = TextBt(Text("Test Mode", size=(32, 32), bg=(0, 255, 0)))
        self.test_mode_bt.rect.center = HUD_RES[0]/2, HUD_RES[1]/2
        def set_test_mode(event):
            self.update_state("test_mode")
        self.test_mode_bt.on_click_end = set_test_mode

        self.mult_bt = TextBt(Text("Multiplayer Test", size=(32, 32), bg=(255, 0, 255)))
        self.mult_bt.rect.center = HUD_RES[0] / 2, HUD_RES[1]/2+50
        def set_mult_test(event):
            self.update_state("mult_test")
        self.mult_bt.on_click_end = set_mult_test

        self.main_menu_bts = pygame.sprite.Group(self.quit_bt, self.test_mode_bt, self.mult_bt)

        self._state = 'main_menu'
        buttons.set_buttons(self.main_menu_bts.sprites())
        self.running = True

    def update_rects(self, size):
        middle = size[0] / 2, size[1] / 2
        self.quad_rects = [pygame.rect.Rect((0, 0), middle), pygame.rect.Rect((middle[0], 0), middle),
                           pygame.rect.Rect(middle, middle), pygame.rect.Rect((0, middle[1]), middle)]
        self.half_y_rects = [pygame.rect.Rect((0, 0), (size[0], middle[1])),
                             pygame.rect.Rect((0, middle[1]), (size[0], middle[1]))]
        self.half_x_rects = [pygame.rect.Rect((0, 0), (middle[0], size[1])),
                             pygame.rect.Rect((middle[0], 0), (middle[0], size[1]))]
        self.whole_rect = [pygame.rect.Rect((0, 0), size)]
        if RECT_MODE in ['quad_rects', 'half_y_rects', 'half_x_rects', 'whole_rect']:
            self.rects = getattr(self, RECT_MODE)
        else:
            logger.critical("Invalid option RECT_MODE: %s", RECT_MODE)
            self.rects = self.whole_rect
        self.rect_len = len(self.rects) - 1
        self.current_rect = self.rects[0]
        self.rect_index = 0

    def tick_rect(self):
        if self.rect_index == self.rect_len:
            self.rect_index = 0
        else:
            self.rect_index += 1
        self.current_rect = self.rects[self.rect_index]

    def global_tick(self):
        self.tick_rect()

    def universal_events(self, event):
        [bt.update_event(event, self.mouse_sprite) for bt in buttons.visible_bts]
        if event.type == MOUSEMOTION:
            self.mouse_pos = event.pos
            self.mouse_sprite.rect.center = self.hud_layer.translate_pos(self.mouse_pos)
        if event.type == QUIT:
            self.terminate()
        if event.type == VIDEORESIZE:
            logger.info("VIDEORESIZE: %s", event.dict['size'])
            self.screen = pygame.display.set_mode(event.dict['size'], SCREEN_FLAGS)
            self.update_rects(event.dict['size'])

    def tick_arbitrary(self, state):
        logger.fatal("Arbitrary _state: '%s'", state)
        logger.fatal("Setting _state to 'main_menu'")
        self.update_state('main_menu')

    def unhandled_update_state(self, old, new):
        logger.warn("Arbitrary update_state: '%s' -> '%s'", old, new)

    def tick_main_menu(self):
        self.clock.tick()
        pygame.display.set_caption(str(self.clock.get_fps()))
        self.hud_layer._map = self.clear_surf.copy()
        self.mouse_sprite.rect.center = self.hud_layer.translate_pos(self.mouse_pos)
        self.hud_layer.draw_group(buttons.visible_bts)
        self.hud_layer.scale_to(self.screen, [1, 1])

        self.screen.fill([255, 255, 255])
        self.hud_layer.blit_to(self.screen)
        pygame.display.update(self.current_rect)

        for event in pygame.event.get():
            self.universal_events(event)

    def stop(self):
        pygame.quit()
        logger.info("Terminating...")


def exception_handler(type, value, tb):
    strtb = traceback.format_exception(type, value, tb)
    logger.critical("Unhandled Exception: \n%s", "".join(strtb))


if __name__ == '__main__':
    logging.captureWarnings(True)
    root = logging.getLogger()
    logger = logging.getLogger('main')
    root.setLevel(logging.DEBUG)
    for handler in generic_logging.handlers:
        root.addHandler(handler)
    sys.excepthook = exception_handler

    logger.info("Starting...")
    logger.info("%s by %s", __appName__, __author__)
    logger.info("Version %s (latest as of %s)", __version__, __date__)

    # Some info about the system.
    logger.info("platform: %s", platform.platform())
    logger.info("ENVIRON: %s", os.environ)
    logger.info("python: %s", sys.version.replace('\n', "- "))
    # Check versions!
    logger.info("pygame==%s (Expected pygame==1.9.4)", pygame.ver)
    logger.info("twisted==%s (Expected twisted==18.9.0)", twisted.__version__)
    logger.info("python==%s (Expected python==2.7)" % sys.version[:3])

    if pygame.ver != '1.9.4':
        warnings.warn("Got pygame==%s (expected pygame==1.9.4)" % pygame.ver, Warning)

    if sys.version[:3] != '2.7':
        warnings.warn("Got python==%s (expected python==2.7)" % sys.version[:3], Warning)

    if twisted.__version__ != '18.9.0':
        warnings.warn("Got twisted==%s (expected twisted==18.9.0)" % twisted.__version__, Warning)

    game = D12_11_18(60)
    game.load()
    reactor.run()
    logger.info("Runtime finished completely. Stopped.")
