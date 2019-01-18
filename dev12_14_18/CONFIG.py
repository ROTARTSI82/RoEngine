# -*- coding: UTF-8 -*-

from pygame.locals import *

__all__ = ['SCREEN_RES', 'SCREEN_FLAGS', 'HUD_RES', 'RECORD_LOGS', 'LOG_CONSOLE', 'WRITE_LATEST', 'LATEST_LEVEL',
           'OUTPUT_LEVEL', 'CONSOLE_LEVEL', 'MAP_ZOOM', 'ABILITY_KEYBINDS', 'WEAPON_KEYBINDS', 'RECT_MODE',
           'BASIC_KEYBINDS', 'ZOOM_VALS']

# CRITICAL/FATAL = 50
# ERROR = 40
# WARNING/WARN = 30
# INFO = 20
# DEBUG = 10
# NOTSET = 0

RECORD_LOGS = False  # Write logs to file
LOG_CONSOLE = True  # Write logs to console
WRITE_LATEST = True  # Write to latest.log

ZOOM_VALS = {"player": 0.75, 'bullets': {0: 0.75, 1: 0.5}}

LATEST_LEVEL = 10  # for latest.log. (DEBUG)
OUTPUT_LEVEL = 10  # for normal files. (DEBUG)
CONSOLE_LEVEL = 10  # for console output (INFO) 20

SCREEN_RES = (960, 720)  # 4:3; Note: objects are not scaled to res.
HUD_RES = (960, 720)  # 960, 720
MAP_ZOOM = (3, 1)  # It's stretched on any other res...
SCREEN_FLAGS = RESIZABLE
RECT_MODE = 'whole_rect'

ABILITY_KEYBINDS = {K_v: '1', K_c: '2'}
WEAPON_KEYBINDS = {K_1: '1', K_2: '2', K_3: '3', K_4: '4'}
BASIC_KEYBINDS = {'jump': (K_SPACE, K_w), 'forward': (K_d, ), 'backward': (K_a, )}
