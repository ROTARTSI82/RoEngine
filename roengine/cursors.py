# -*- coding: UTF-8 -*-

"""
Module for custom cursors
"""

import pygame

__all__ = ['text_marker', 'slider_x', 'slider_xy', 'slider_y', 'tri_left', 'thick_arrow', 'tri_right',
           'clickable', 'reticule', 'ball', 'diamond', 'arrow', 'default']

_CLICKABLE_CURSOR = (
    "     XX                 ",  # 24x24
    "    X..X                ",
    "    X..X                ",
    "    X..X                ",
    "    X..X                ",
    "    X..XXX              ",
    "    X..X..XXX           ",
    "    X..X..X..XX         ",
    "    X..X..X..X.X        ",
    "XXX.X..X..X..X..X       ",
    "X..XX........X..X       ",
    "X...X...........X       ",
    " X..............X       ",
    "  X.............X       ",
    "  X.............X       ",
    "   X............X       ",
    "   X...........X        ",
    "    X..........X        ",
    "    X..........X        ",
    "     X........X         ",
    "     X........X         ",
    "     XXXXXXXXXX         ",
    "                        ",
    "                        ",
)
_DEFAULT_CURSOR = (
    "X                       ",
    "XX                      ",
    "X.X                     ",
    "X..X                    ",
    "X...X                   ",
    "X....X                  ",
    "X.....X                 ",
    "X......X                ",
    "X.......X               ",
    "X........X              ",
    "X.........X             ",
    "X..........X            ",
    "X......XXXXX            ",
    "X...X..X                ",
    "X..X X..X               ",
    "X.X  X..X               ",
    "XX    X..X              ",
    "      X..X              ",
    "       XX               ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
)

text_marker = [(8, 16), (4, 6)] + list(pygame.cursors.compile(pygame.cursors.textmarker_strings))
slider_x = [(24, 16), (9, 6)] + list(pygame.cursors.compile(pygame.cursors.sizer_x_strings))
slider_y = [(16, 24), (6, 10)] + list(pygame.cursors.compile(pygame.cursors.sizer_y_strings))
slider_xy = [(24, 16), (8, 8)] + list(pygame.cursors.compile(pygame.cursors.sizer_xy_strings))
thick_arrow = [(24, 24), (2, 2)] + list(pygame.cursors.compile(pygame.cursors.thickarrow_strings))

clickable = [(24, 24), (6, 2)] + list(pygame.cursors.compile(_CLICKABLE_CURSOR))
default = [(24, 24), (1, 1)] + list(pygame.cursors.compile(_DEFAULT_CURSOR))

reticule = list(pygame.cursors.broken_x)
reticule[1] = (8, 8)  # The hotspot on the original is slightly off-center.

arrow = pygame.cursors.arrow
diamond = pygame.cursors.diamond
ball = pygame.cursors.ball
tri_left = pygame.cursors.tri_left
tri_right = pygame.cursors.tri_right
