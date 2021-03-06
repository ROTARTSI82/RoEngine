# -*- coding: UTF-8 -*-

"""
Defines [Dummy] and [Game]
"""

import pygame
import logging

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

__all__ = ["Dummy", "Game", "Obstacle"]

"""
Usage:
>>> isAdmin = newflag(3)  # isAdmin: 8 (int)
>>> isModerator = newflag(2)  # isModerator: 4 (int)
>>> Bob = isAdmin | isModerator
>>> Alice = isModerator
>>> if isModerator in get_flags(Alice):  # get_flags(Alice) == [4, ]
...     -- INSERT CODE HERE --
>>> get_flags(Bob)
[4, 8]

"""

logger = logging.getLogger("util.base")

_flaglist = []


def newflag(num):
    _flaglist.append(1 << num)
    return 1 << num


def get_flags(num):
    ret = []
    for i in _flaglist:
        if num & i:
            ret.append(i)
    return ret


def are_flags_set(num, flags, mode='all'):
    return globals()['__builtins__'][mode]([num & i for i in flags])


class Dummy(object):

    def __getitem__(self, item):
        return self

    def __getattr__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self


class Game(object):
    def __init__(self, fps=60, state='main'):
        self.fps = fps
        self._state = state
        self.running = False

    def terminate(self, stop_args=()):
        self.running = False
        self.stop(*stop_args)
        reactor.stop()

    def tick_arbitrary(self, state):
        """
        Handle arbitrary states

        :param args:
        :param kwargs:
        :return:
        """
        print ("WARNING: Arbitrary state")

    def stop(self, *args, **kwargs):
        self.running = False

    def update_state(self, new):
        assert type(new) == str
        old_state = self._state[:]
        if new == old_state: return
        self._state = new
        if hasattr(self, 'exit_%s' %(old_state)):
            getattr(self, 'exit_%s' % old_state)(new)
        if hasattr(self, 'enter_%s' % (new)):
            getattr(self, 'enter_%s' % new)(old_state)
        if hasattr(self, "%s_to_%s"%(old_state, new)):
            getattr(self, "%s_to_%s"%(old_state, new))()
        else:
            self.unhandled_update_state(old_state, new)

    def unhandled_update_state(self, old, new):
        """
        Handle the event of an arbitrary parameter passed to [self.update_state]

        :param old:
        :param new:
        :return:
        """
        print ("WARNING: ARBITRARY UPDATE_STATE")

    def start(self, *args, **kwargs):
        self.running = True

    def global_tick(self):
        pass

    def _call_tick(self, *args, **kwargs):
        if self.running:
            self.global_tick()
            if hasattr(self, "tick_"+self._state):
                getattr(self, "tick_"+self._state)(*args, **kwargs)
            else:
                self.tick_arbitrary(self._state)

    def load(self, start_args=(), tick_args=()):
        reactor.callWhenRunning(self.start, *start_args)
        _tick = LoopingCall(self._call_tick, *tick_args)
        _tick.start(1.0/self.fps)
        return _tick


class Obstacle(pygame.sprite.Sprite):
    refract_blume = [2.0, 2.0]

    def __init__(self, size, pos, lvl=1, color=(0, 0, 0)):
        pygame.sprite.Sprite.__init__(self)

        self.climb_difficulty = lvl

        self.size = size
        self.color = color
        self.image = pygame.Surface(size).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def copy(self):
        return Obstacle(self.size, self.rect.center, self.climb_difficulty, self.color)

    def update_size(self):
        oldPos = self.rect.center
        try:
            self.image = pygame.Surface(self.size).convert()
        except pygame.error:  # Invalid size. just don't do anything.
            pass
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = oldPos

    def on_collide(self, face, player):
        pass

    def bullet_on_collide(self, col_list):
        logger.critical("bullet_on_collide of an Obstacle was called!")

    def damage(self, damage, parent):
        parent.req_kill()
