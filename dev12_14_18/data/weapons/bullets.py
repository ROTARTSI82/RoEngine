# -*- coding: UTF-8 -*-

from roengine.game.animation import from_spritesheet
from roengine import Bullet
from dev12_14_18.CONFIG import ZOOM_VALS
import pygame

bullet_img = None
shotgun_img = None


class RifleBullet(Bullet):
    def __init__(self, damage, target, parent, blume):
        global bullet_img
        Bullet.__init__(self, damage, target, parent, blume)
        if bullet_img is None:
            bullet_img = from_spritesheet([32, 96, 32, 32], pygame.image.load("./data/sprites/Player.png"))
        self.master_image = bullet_img
        self.type = 0
        self.rot_to_target(self.target, ZOOM_VALS['bullets'][self.type], False)  # Doesn't account for blume...


class ShotgunBullet(Bullet):
    def __init__(self, damage, target, parent, blume):
        global shotgun_img
        Bullet.__init__(self, damage, target, parent, blume)
        if shotgun_img is None:
            shotgun_img = from_spritesheet([0, 96, 32, 32], pygame.image.load("./data/sprites/Player.png"))
        self.master_image = shotgun_img
        self.type = 1
        self.rot_to_target(self.target, ZOOM_VALS['bullets'][self.type], False)  # Doesn't account for blume...

# Radic

# Traceless

# Techno

# Sergeant

# Brawl

# Inferno

# Enchanter
