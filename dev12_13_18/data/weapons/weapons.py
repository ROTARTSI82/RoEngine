# -*- coding: UTF-8 -*-

from roengine import Weapon, Shotgun
from .bullets import *


AutomaticShotgun = Shotgun(65.5, 1.5, Bullet, None, 5, 12, float('inf'), 4.75, (1.5, 1.5))  # Modeled after Tac
Sniper = Weapon(72, 0.8, Bullet, None, 6, float('inf'), 1.8, (0, 0))  # Modeled after Hunting Rifle
SMG = Weapon(105, 9, Bullet, None, 40, float('inf'), 3, (1.6, 1.6))  # Based off of the p90 (duh)
AssaultRifle = Weapon(96.25, 5.5, Bullet, None, 30, float('inf'), 2.3, (1, 1))  # Based off of grey AR

#AutomaticShotgun.str_repr = "Automatic Shotgun"
Sniper.str_repr = 'Sniper Rifle'
SMG.str_repr = 'SubMachineGun'
AssaultRifle.str_repr = 'Assault Rifle'
