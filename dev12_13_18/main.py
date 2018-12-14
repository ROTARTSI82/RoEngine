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
##

__appName__ = "_UntitledApp"  # Placeholder
__version__ = 'dev12.13.18'
__author__ = "Grant Yang <rotartsi0482@gmail.com>"
__date__ = '13 December 2018'


class D12_11_18(Game):
    enter_test_mode, exit_test_mode, tick_test_mode = enter_test_mode, exit_test_mode, tick_test_mode
    def start(self):
        pygame.init()
        # Add vars from global
        self.logger = logger
        self.initiated = []

        self.screen = pygame.display.set_mode(SCREEN_RES, SCREEN_FLAGS)

        self.hud_layer = Map(HUD_RES)
        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32)

        self.mouse_sprite = DummySprite([10, 10], [0, 0])
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

        self.main_menu_bts = pygame.sprite.Group(self.quit_bt, self.test_mode_bt)

        self._state = 'main_menu'
        buttons.set_buttons(self.main_menu_bts.sprites())
        self.running = True

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

    def tick_arbitrary(self, state):
        logger.fatal("Arbitrary _state: '%s'", state)
        logger.fatal("Setting _state to 'main_menu'")
        self.update_state('main_menu')

    def unhandled_update_state(self, old, new):
        logger.fatal("Arbitrary update_state: '%s' -> '%s'", old, new)

    def tick_main_menu(self):
        self.hud_layer._map = self.clear_surf.copy()
        self.mouse_sprite.rect.center = self.hud_layer.translate_pos(self.mouse_pos)
        self.hud_layer.draw_group(buttons.visible_bts)
        self.hud_layer.scale_to(self.screen, [1, 1])

        self.screen.fill([255, 255, 255])
        self.hud_layer.blit_to(self.screen)
        pygame.display.flip()

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
    warningLog = logging.getLogger('py.warnings')

    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    for handler in generic_logging.handlers:
        warningLog.addHandler(handler)
        logger.addHandler(handler)
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
        warnings.warn(Warning("Got pygame==%s (expected pygame==1.9.4)" % pygame.ver))

    if sys.version[:3] != '2.7':
        warnings.warn(Warning("Got python==%s (expected python==2.7)" % sys.version[:3]))

    if twisted.__version__ != '18.9.0':
        warnings.warn(Warning("Got twisted==%s (expected twisted==18.9.0)" % twisted.__version__))

    game = D12_11_18()
    game.load()
    reactor.run()
    logger.info("Runtime finished completely. Stopped.")
