# -*- coding: UTF-8 -*-

"""
Module for custom cursors
"""

import pygame

__all__ = ['text_marker', 'slider_x', 'slider_xy', 'slider_y', 'tri_left', 'thick_arrow', 'tri_right',
           'clickable', 'broken_x', 'ball', 'diamond', 'arrow']

_CURSOR_STRING_ARRAY = (
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
text_marker = [(8, 16), (4, 6)] + list(pygame.cursors.compile(pygame.cursors.textmarker_strings))
slider_x = [(24, 16), (9, 6)] + list(pygame.cursors.compile(pygame.cursors.sizer_x_strings))
slider_y = [(16, 24), (6, 10)] + list(pygame.cursors.compile(pygame.cursors.sizer_y_strings))
slider_xy = [(24, 16), (8, 8)] + list(pygame.cursors.compile(pygame.cursors.sizer_xy_strings))
thick_arrow = [(24, 24), (2, 2)] + list(pygame.cursors.compile(pygame.cursors.thickarrow_strings))

clickable = [(24, 24), (6, 2)] + list(pygame.cursors.compile(_CURSOR_STRING_ARRAY))

broken_x = pygame.cursors.broken_x
arrow = pygame.cursors.arrow
diamond = pygame.cursors.diamond
ball = pygame.cursors.ball
tri_left = pygame.cursors.tri_left
tri_right = pygame.cursors.tri_right
