# -*- coding: UTF-8 -*-

"""
pygame.cursor and pygame.mouse test
"""

import pygame

from pygame.locals import *
from roengine import *

from roengine.cursors import clickable


class CursorsTest(Game):
    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode([640, 480])
        self.CURSOR_STRING_ARRAY = (
            "........................",
            "........................",
            "........................",
            "........................",
            "........................",
            "........................",
            "..........XXX...........",
            "..........XXX...........",
            "..........XXX...........",
            "........................",
            "........................",
            "........................",
            "........................",
            "........................",
            "........................",
            "........................",
        )
        self.COMPILED_CURSOR = list(pygame.cursors.compile(self.CURSOR_STRING_ARRAY))
        self.COMPILED_CURSOR = [(24, 16), (12, 8)] + self.COMPILED_CURSOR

        self.text_marker = [(8, 16), (4, 6)] + list(pygame.cursors.compile(pygame.cursors.textmarker_strings))
        self.slider_x = [(24, 16), (9, 6)] + list(pygame.cursors.compile(pygame.cursors.sizer_x_strings))
        self.slider_y = [(16, 24), (6, 10)] + list(pygame.cursors.compile(pygame.cursors.sizer_y_strings))
        self.slider_xy = [(24, 16), (8, 8)] + list(pygame.cursors.compile(pygame.cursors.sizer_xy_strings))
        self.thick_arrow = [(24, 24), (2, 2)] + list(pygame.cursors.compile(pygame.cursors.thickarrow_strings))

        pygame.mouse.set_cursor(*clickable)
        self.running = True
        self.markers = pygame.sprite.Group()
        self.mdown = False

    def tick_main(self):
        self.screen.fill([255, 255, 255])
        self.markers.draw(self.screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
            if event.type == MOUSEBUTTONDOWN:
                self.mdown = True
            elif event.type == MOUSEBUTTONUP:
                self.mdown = False
        if self.mdown:
            self.markers.add(DummySprite([2, 2], pygame.mouse.get_pos()))


    def stop(self):
        pygame.quit()
        self.running = False


if __name__ == "__main__":
    game = CursorsTest()
    game.load()
    reactor.run()
