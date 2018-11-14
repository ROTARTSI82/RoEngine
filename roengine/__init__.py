#!venv/bin python
# -*- coding: UTF-8 -*-

"""
RoEngine_temp is a library for making mundane parts easy and fast.
"""

from .gameplay import *
from .networking import *
from .util import *
from .gui import *

# NOTE: The following imports are unused
from .maths import *

__all__ = ["Map", "DummySprite", "PlatformerPlayer", "Projectile", "GenericUDPClient", "GenericTCPClient", "Game",
           "GenericClientFactory", "reactor", "GenericUDPServer", "GenericTCPServer", "GenericServerFactory",
           "Dummy", "Button", "Text", "buttons", "CheckBox", "CheckButton", "Weapon", "bullets", "Bullet"]

__extras__ = ['factorize', 'gen_primes', 'is_prime', 'is_perfect', 'gen_perfect', 'prime_factorize',
              'lcm', 'gcf', 'reduce_frac', 'Fraction', 'MixedNumber']

# Uncomment to include extra functions
# __all__.extend(__extras__)
