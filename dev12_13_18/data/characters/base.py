import pygame

from pygame.locals import *
from roengine import *
from dev12_13_18.data.weapons.weapons import *


class Dash(Action):
    def __init__(self, player, game):
        self.player = player
        self.game = game
        Action.__init__(self, 'ability', 5, 2, 10)

    def __str__(self): return "Dash"

    def start(self):
        self.player.position = pygame.math.Vector2(self.game.map.translate_pos(pygame.mouse.get_pos()))
        self.player.update_rect()


class BasicCharacter(PlatformerPlayer):
    def __init__(self, game):
        PlatformerPlayer.__init__(self, pygame.Surface([16, 16]).convert_alpha())
        self.image.fill([0, 0, 255])
        self.health = 100
        self.defense = 1

        self.game = game

        self.speed = 5
        self.firing = False
        self.aiming_at = [0, 0]
        self.action_manager = ActionManager()

        self.inv = {'1': SMG, '2': AssaultRifle, '3': AutomaticShotgun, '4': Sniper}
        self.abilities = {'b': Dash(self, self.game)}
        self.ability = ['b']
        self.mode = 'weapon'
        for k in self.inv.keys():
            self.inv[k].parent = self
            self.inv[k].actionManager = self.action_manager
        self.weapon = self.inv['1']

    def damage(self, damage, bullet):
        bullet.req_kill()
        self.health -= damage * self.defense

    def update(self):
        self.action_manager.tick()
        if self.weapon.parent != self:
            self.weapon.parent = self
            self.weapon.actionManager = self.action_manager
        self.weapon.tick()
        if self.firing and self.mode == 'weapon':
            self.weapon.tick_fire(self.aiming_at)
        if self.firing and self.mode == 'ability':
            self.action_manager.do_action(self.ability)
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
