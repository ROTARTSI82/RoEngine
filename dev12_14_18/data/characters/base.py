import pygame
import time
import random
pygame.init()

from pygame.locals import *
from roengine.game.animation import *
from roengine import *
from dev12_14_18.CONFIG import *
from dev12_14_18.data.weapons.weapons import *

WEAPON_KEYS = WEAPON_KEYBINDS.keys()
ABILITY_KEYS = ABILITY_KEYBINDS.keys()
_weapon_switch = Action('weapon_switch', 0, 0)

#spritesheet = pygame.image.load("./data/sprites/player.png")
fps = 1.0/5
death = []
birth = []
init = False
# cannot use convert_alpha yet.


class Dash(Action):
    def __init__(self, player, game):
        self.id = 1
        self.player = player
        self.game = game
        Action.__init__(self, 'ability.dash', 129, 0, 5)

    def __str__(self): return "Dash"

    def start(self):
        self.player.position = pygame.math.Vector2(self.player.aiming_at)
        self.player.update_rect()


class Flight(Action):
    def __init__(self, player, game):
        self.id = 2
        self.player = player
        self.game = game
        Action.__init__(self, 'ability.flight', 128, 5, 30)

    def __str__(self): return "Flight"

    def tick(self):
        self.player.position = pygame.math.Vector2(self.player.aiming_at)
        self.player.update_rect()


class BasicCharacter(PlatformerPlayer):
    keybinds = BASIC_KEYBINDS
    respawn_cool = 5
    streak_multiplier = 0.25

    def __init__(self, game):
        global death, birth, spritesheet, init
        if not init:
            spritesheet = pygame.image.load("./data/sprites/Player.png")
            death = [(from_spritesheet([0, 0, 32, 32], spritesheet), fps),
                     (from_spritesheet([32, 0, 32, 32], spritesheet), fps),
                     (from_spritesheet([0, 32, 32, 32], spritesheet), fps),
                     (from_spritesheet([32, 32, 32, 32], spritesheet), fps),
                     (from_spritesheet([0, 64, 32, 32], spritesheet), fps),
                     (from_spritesheet([64, 64, 32, 32], spritesheet), fps)]
            birth = list(reversed(death))
            init = True
        PlatformerPlayer.__init__(self, pygame.Surface([16, 16]).convert_alpha())
        self.image.fill([0, 0, 255])
        self.health = 100
        self.max_hp = 100
        self.defense = 1
        self.name = 'Player'

        self.kills = 0
        self.score = 0
        self.streak = 0

        self.game = game
        self.respawn_start = 0
        self.alive = True
        self.animations = Animation(mode='sec', idle=death[0][0], loop=False)
        prev_center = self.rect.center
        self.rect = self.animations.idle_frame.get_rect()
        self.rect.center = prev_center
        self.spawn_locations = [[0, 0], ]

        self.speed = 5
        self.firing = False
        self.aiming_at = [0, 0]
        self.mouse_at = [0, 0]
        self.action_manager = ActionManager()
        WArgs = (self, self.action_manager)
        self.inv = {'weapon_1': SMG(*WArgs), 'weapon_2': AssaultRifle(*WArgs), 'weapon_3': AutomaticShotgun(*WArgs),
                    'weapon_4': Sniper(*WArgs)}
        self.abilities = {'ability_1': Dash(self, self.game), 'ability_2': Flight(self, self.game)}
        self.ability = self.abilities['ability_1']
        self.mode = 'weapon'
        self.weapon = self.inv['weapon_1']

    def onDamageDealt(self, amount):
        self.score += (1+self.streak*self.streak_multiplier) * amount

    def onDeath(self):
        self.animations.play_anim(death, death[-1][0])

    def onRespawn(self):
        """
        Reset all our attributes.
        :return: None
        """
        self.animations.play_anim(birth, death[0][0])
        self.position = pygame.math.Vector2(random.choice(self.spawn_locations))
        self.velocity = pygame.math.Vector2(0, 0)
        self.rotation = 0
        self.update_rect()

        self.is_climbing = False
        self.grounded = False
        self.firing = False

        self.input_state = {"forward": False, "backward": False, "jump": False}
        self.alive = True
        self.health = self.max_hp
        self.streak = 0

        self.aiming_at = [0, 0]
        self.action_manager = ActionManager()
        WArgs = (self, self.action_manager)
        self.inv = {'weapon_1': SMG(*WArgs), 'weapon_2': AssaultRifle(*WArgs), 'weapon_3': AutomaticShotgun(*WArgs),
                    'weapon_4': Sniper(*WArgs)}
        self.abilities = {'ability_1': Dash(self, self.game), 'ability_2': Flight(self, self.game)}
        self.ability = self.abilities['ability_1']
        self.mode = 'weapon'
        self.weapon = self.inv['weapon_1']

    def update_event(self, event):
        PlatformerPlayer.update_event(self, event)
        if event.type == KEYDOWN:
            if event.key == K_r and self.mode == 'weapon':
                self.weapon.force_reload()
            if event.key in ABILITY_KEYS:
                self.action_manager.do_action(_weapon_switch, True)
                self.ability = self.abilities[ABILITY_KEYBINDS[event.key]]
                self.mode = 'ability'
                if hasattr(self.game, 'weapon_txt'):
                    self.game.weapon_txt.update_text("Ability: " + str(self.ability))
            if event.key in WEAPON_KEYS:
                self.action_manager.do_action(_weapon_switch, True)
                self.weapon = self.inv[WEAPON_KEYBINDS[event.key]]
                self.mode = 'weapon'
                if hasattr(self.game, 'weapon_txt'):
                    self.game.weapon_txt.update_text("Item: " + str(self.weapon))
        if event.type == MOUSEMOTION:
            self.mouse_at = event.dict['pos']
        if event.type == MOUSEBUTTONDOWN:
            self.firing = True
        if event.type == MOUSEBUTTONUP:
            self.firing = False

    def damage(self, damage, bullet):
        bullet.req_kill()
        bullet.parent.onDamageDealt(damage)
        self.health -= damage * self.defense
        if self.health <= 0 and self.alive:
            bullet.parent.kills += 1
            bullet.parent.streak += 1
            #self.rect.center = [0, 0]
            #self.update_pos()
            self.streak = 0
            self.alive = False
            self.respawn_start = time.time()
            self.onDeath()

    def update(self, upd_pos=True, is_server=False):
        self.animations.update()
        self.master_image = self.animations.get_frame()
        self.update_rot(self.aiming_at)
        self.action_manager.tick()
        self.weapon.tick()
        if self.health <= 0 and self.alive:
            #self.rect.center = [0, 0]
            #self.update_pos()
            self.streak = 0
            self.alive = False
            self.respawn_start = time.time()
            self.onDeath()

        if self.alive:
            if not is_server:
                self.aiming_at = self.game.map.translate_pos(self.mouse_at)
            if self.firing and self.mode == 'weapon' and upd_pos:
                self.weapon.tick_fire(self.aiming_at)
            if self.firing and self.mode == 'ability' and upd_pos:
                self.action_manager.do_action(self.ability)
            if upd_pos:
                PlatformerPlayer.update(self)
        elif not self.alive:
            if time.time()-self.respawn_start > self.respawn_cool:
                self.onRespawn()


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
