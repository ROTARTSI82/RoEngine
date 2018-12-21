import pygame

from pygame.locals import *
from roengine import *
from dev12_14_18.data.weapons.weapons import *


class Dash(Action):
    def __init__(self, player, game):
        self.id = 1
        self.player = player
        self.game = game
        Action.__init__(self, 'ability', 5, 0, 5)

    def __str__(self): return "Dash"

    def start(self):
        self.player.position = pygame.math.Vector2(self.player.aiming_at)
        self.player.update_rect()


class Flight(Action):
    def __init__(self, player, game):
        self.id = 2
        self.player = player
        self.game = game
        Action.__init__(self, 'ability', 4, 5, 30)

    def __str__(self): return "Flight"

    def tick(self):
        self.player.position = pygame.math.Vector2(self.player.aiming_at)
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
        WArgs = (self, self.action_manager)
        self.inv = {'weapon_1': SMG(*WArgs), 'weapon_2': AssaultRifle(*WArgs), 'weapon_3': AutomaticShotgun(*WArgs),
                    'weapon_4': Sniper(*WArgs)}
        self.abilities = {'ability_1': Dash(self, self.game), 'ability_2': Flight(self, self.game)}
        self.ability = self.abilities['ability_1']
        self.mode = 'weapon'
        self.weapon = self.inv['weapon_1']

    def damage(self, damage, bullet):
        bullet.req_kill()
        self.health -= damage * self.defense

    def update(self):
        self.action_manager.tick()
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
        self.health = 100
        self.defense = 1
        self.speed = 3

    def damage(self, damage, bullet):
        bullet.req_kill()
        self.health -= damage * self.defense
        if self.health <= 0:
            self.req_kill()

    def req_kill(self):
        self.kill()

    def update(self, player):
        PlatformerPlayer.update(self)

        self.input_state = {"forward": False, "backward": False, "jump": True}
        if player.rect.x > self.rect.x:
            self.input_state['forward'] = True
        elif player.rect.x < self.rect.x:
            self.input_state['backward'] = True
