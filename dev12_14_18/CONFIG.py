# -*- coding: UTF-8 -*-

from pygame.locals import *

__all__ = ['SCREEN_RES', 'SCREEN_FLAGS', 'HUD_RES', 'RECORD_LOGS', 'LOG_CONSOLE', 'WRITE_LATEST', 'LATEST_LEVEL',
           'OUTPUT_LEVEL', 'CONSOLE_LEVEL', 'MAP_ZOOM', 'ABILITY_KEYBINDS', 'WEAPON_KEYBINDS']

# CRITICAL/FATAL = 50
# ERROR = 40
# WARNING/WARN = 30
# INFO = 20
# DEBUG = 10
# NOTSET = 0

RECORD_LOGS = False  # Write logs to file
LOG_CONSOLE = True  # Write logs to console
WRITE_LATEST = True  # Write to latest.log

LATEST_LEVEL = 10  # for latest.log. (DEBUG)
OUTPUT_LEVEL = 10  # for normal files. (DEBUG)
CONSOLE_LEVEL = 20  # for console output (INFO)

SCREEN_RES = (960, 720)  # 4:3; Note: objects are not scaled to res.
HUD_RES = (960, 720)  # 960, 720
MAP_ZOOM = (3, 1)  # It's stretched on any other res...
SCREEN_FLAGS = RESIZABLE

ABILITY_KEYBINDS = {K_v: 'ability_1', K_c: 'ability_2'}
WEAPON_KEYBINDS = {K_1: 'weapon_1', K_2: 'weapon_2', K_3: 'weapon_3', K_4: 'weapon_4'}
