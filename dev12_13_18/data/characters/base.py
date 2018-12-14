import pygame
from roengine import *
from dev12_13_18.data.weapons.weapons import *


class BasicCharacter(PlatformerPlayer):
    def __init__(self):
        PlatformerPlayer.__init__(self, pygame.Surface([16, 16]).convert_alpha())
        self.image.fill([0, 0, 255])
        self.health = 100
        self.defense = 1
        self.speed = 5
        self.firing = False
        self.aiming_at = [0, 0]
        self.action_manager = ActionManager()
        self.inv = {'1': SMG, '2': AssaultRifle, '3': AutomaticShotgun, '4': Sniper}
        for k in self.inv.keys():
            self.inv[k].parent = self
            self.inv[k].actionManager = self.action_manager
        self.weapon = self.inv['1']

    def damage(self, damage, bullet):
        bullet.req_kill()
        self.health -= damage * self.defense

    def update(self):
        if self.weapon.parent != self:
            self.weapon.parent = self
            self.weapon.actionManager = self.action_manager
        self.weapon.tick()
        if self.firing:
            self.weapon.tick_fire(self.aiming_at)
        PlatformerPlayer.update(self)


class TargetDummy(PlatformerPlayer):
    def __init__(self):
        PlatformerPlayer.__init__(self, pygame.Surface([16, 16]).convert_alpha())
        self.image.fill([255, 0, 0])
        self.health = 75
        self.defense = 1
        self.speed = 3

    def damage(self, damage, bullet):
        bullet.req_kill()
        self.health -= damage * self.defense

    def req_kill(self):
        self.kill()

    def update(self, player):
        PlatformerPlayer.update(self)

        self.input_state = {"forward": False, "backward": False, "jump": True}
        if player.rect.x > self.rect.x:
            self.input_state['forward'] = True
        elif player.rect.x < self.rect.x:
            self.input_state['backward'] = True

        if self.health <= 0:
            self.req_kill()
