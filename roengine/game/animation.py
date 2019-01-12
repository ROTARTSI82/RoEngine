# -*- coding: UTF-8 -*-
import time
import pygame


def from_spritesheet(rectangle, surf):
    rect = pygame.Rect(rectangle)
    image = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
    image.blit(surf, (0, 0), rect)
    #image.set_colorkey((255, 255, 255), pygame.RLEACCEL)
    return image.convert_alpha()


class Animation(object):
    def __init__(self, frames=(), mode='num', loop=True, idle=None):
        self.master_num = 0
        self.frame_num = 0
        self.mode = mode
        self.idle_frame = idle
        self.lastFlip = time.time()
        self.doLoop = loop
        self.alive = False
        self.frames = frames

    def reset(self):
        self.frame_num = 0

    def update(self):
        if self.alive:
            if self.mode == 'num':
                self.master_num += 1
                if self.master_num % self.frames[self.frame_num][1] == 0:
                    self.master_num = 0
                    self.progress_frame()
            else:
                now = time.time()
                if now-self.lastFlip >= self.frames[self.frame_num][1]:
                    self.lastFlip = now
                    self.progress_frame()

    def play_anim(self, anim=None, idle=None):
        self.master_num = 0
        self.frame_num = 0
        self.lastFlip = time.time()
        if idle is not None:
            self.idle_frame = idle
        if anim is None:
            self.alive = True
            return
        self.frames = anim
        self.alive = True

    def stop_anim(self):
        self.alive = False

    def progress_frame(self):
        self.frame_num += 1
        if self.frame_num >= len(self.frames):
            self.frame_num = 0
            if not self.doLoop:
                self.alive = False
        self.onFrameUpdate()

    def onFrameUpdate(self):
        pass

    def get_frame(self):
        if self.frames and self.alive:
            return self.frames[self.frame_num][0]
        else:
            return self.idle_frame
