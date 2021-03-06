# -*- coding: UTF-8 -*-

from roengine import Weapon, Shotgun
from .bullets import *


def _pdw(weapon, str_repr, identifier, type='Weapon'):
    def _predef_weapon_instance(parent, action_manager):
        ret = (Weapon if type == 'Weapon' else Shotgun)(*weapon)
        ret.parent = parent
        ret.actionManager = action_manager
        ret.str_repr = str_repr
        ret.reload_action.name = 'reload.%s' % str_repr
        ret.id = identifier  # why? this is never used...
        return ret
    return _predef_weapon_instance


AutomaticShotgun = _pdw((65.5, 1.5, ShotgunBullet, None, 5, 12, float('inf'), 4.75, (1.5, 1.5)),
                        'Automatic Shotgun', 3, 'Shotgun')
Sniper = _pdw((72, 0.8, RifleBullet, None, 6, float('inf'), 1.8, (0, 0)), 'Sniper Rifle', 4)
SMG = _pdw((105, 9, RifleBullet, None, 40, float('inf'), 3, (1.6, 1.6)), 'SubMachineGun', 1)
AssaultRifle = _pdw((96.25, 5.5, RifleBullet, None, 30, float('inf'), 2.3, (1, 1)), 'Assault Rifle', 2)
