# -*- coding: UTF-8 -*-

"""
Defines [Dummy] and [Game]
"""

import pygame
import random

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

__all__ = ["Dummy", "Game", "Obstacle"]


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

        self.image = pygame.Surface(size).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def on_collide(self, face, player):
        pass

    def damage(self, damage, parent):
        parent.req_kill()
