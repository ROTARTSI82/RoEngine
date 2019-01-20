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

fps = 1.0/5
death = []
birth = []
init = False
# cannot use convert_alpha yet.

SHIELD_PER_SECOND = 7.5
HEALTH_PER_SECOND = 2
FRAMES_PER_SECOND = 60
STUN_DURATION = 5  # How long to wait without taking damage before shields start regenerating
SHIELD_PLUS = SHIELD_PER_SECOND / float(FRAMES_PER_SECOND)  # Remember python 2 floor division
HEALTH_PLUS = HEALTH_PER_SECOND / float(FRAMES_PER_SECOND)


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
    ability_keybinds = ABILITY_KEYBINDS
    weapon_keybinds = WEAPON_KEYBINDS
    weapon_keys = weapon_keybinds.keys()
    ability_keys = ability_keybinds.keys()

    respawn_cool = 5
    streak_multiplier = 0.25
    ZOOM = 0.75

    def __init__(self, game, img_path="./data/sprites/Player.png"):
        global death, birth, spritesheet, init
        if not init:
            spritesheet = pygame.image.load(img_path).convert_alpha()
            death = [(from_spritesheet([0, 0, 32, 32], spritesheet), fps),
                     (from_spritesheet([32, 0, 32, 32], spritesheet), fps),
                     (from_spritesheet([0, 32, 32, 32], spritesheet), fps),
                     (from_spritesheet([32, 32, 32, 32], spritesheet), fps),
                     (from_spritesheet([0, 64, 32, 32], spritesheet), fps),
                     (from_spritesheet([64, 64, 32, 32], spritesheet), fps)]
            birth = list(reversed(death))
            init = True
        PlatformerPlayer.__init__(self, death[0][0].convert_alpha())
        self.image.fill([0, 0, 255])
        self.health = 100
        self.max_hp = 100
        self.shield = 100
        self.shield_cooldown = {"start": 0, "duration": 0}
        self.max_shield = 100, 100  # First item is the max shield points, shield is divided by second to get percent
        self.name = 'Player'

        self.kills = 0
        self.score = 0
        self.streak = 0

        self.game = game
        self.respawn_start = 0
        self.alive = True
        self.animations = Animation(mode='sec', idle=death[0][0], loop=False)
        prev_center = self.rect.center
        self.rect = pygame.transform.rotozoom(self.animations.idle_frame, 0, self.ZOOM).get_rect()
        self.rect.center = prev_center
        self.spawn_locations = [[0, 0], ]

        self.speed = 5
        self.firing = False
        self.aiming_at = [0, 0]
        self.mouse_at = [0, 0]
        self.action_manager = ActionManager()
        WArgs = (self, self.action_manager)
        self.inv = {'1': SMG(*WArgs), '2': AssaultRifle(*WArgs), '3': AutomaticShotgun(*WArgs),
                    '4': Sniper(*WArgs)}
        self.abilities = {'1': Dash(self, self.game), '2': Flight(self, self.game)}
        self.ability = self.abilities['1']
        self.mode = 'weapon'
        self.weapon = self.inv['1']

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
        self.shield = self.max_shield[0]
        self.shield_cooldown = {"start": 0, "duration": 0}
        self.streak = 0

        self.aiming_at = [0, 0]
        self.action_manager = ActionManager()
        WArgs = (self, self.action_manager)
        self.inv = {'1': SMG(*WArgs), '2': AssaultRifle(*WArgs), '3': AutomaticShotgun(*WArgs),
                    '4': Sniper(*WArgs)}
        self.abilities = {'1': Dash(self, self.game), '2': Flight(self, self.game)}
        self.ability = self.abilities['1']
        self.mode = 'weapon'
        self.weapon = self.inv['1']

    def update_event(self, event, upd_txt=True):
        PlatformerPlayer.update_event(self, event)
        if event.type == KEYDOWN:
            if event.key == K_r and self.mode == 'weapon' and upd_txt:
                self.weapon.force_reload()
            if event.key in self.ability_keys and upd_txt:
                self.action_manager.do_action(_weapon_switch, True)
                self.ability = self.abilities[self.ability_keybinds[event.key]]
                self.mode = 'ability'
                if hasattr(self.game, 'weapon_txt'):
                    self.game.weapon_txt.update_text("Ability: " + str(self.ability))
            if event.key in self.weapon_keys and upd_txt:
                self.action_manager.do_action(_weapon_switch, True)
                self.weapon = self.inv[self.weapon_keybinds[event.key]]
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
        if not self.alive:
            return
        bullet.req_kill()
        bullet.parent.onDamageDealt(damage)
        if self.shield > 0:
            shield_percent = self.shield / float(self.max_shield[1])
            self.health -= damage * (1 - shield_percent)
            self.shield -= damage * shield_percent
            if self.shield < 0:
                self.health += self.shield  # Deduct abs(shield) since the shield failed to reflect that damage
        else:
            self.health -= damage
        self.shield_cooldown['start'] = time.time()
        self.shield_cooldown['duration'] = STUN_DURATION
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
        if time.time() - self.shield_cooldown['start'] > self.shield_cooldown['duration'] and upd_pos:
            self.shield = min(self.max_shield[0], self.shield + SHIELD_PLUS)  # Could we do this another way?
            self.health = min(self.max_hp, self.health + HEALTH_PLUS)
        self.action_manager.tick()
        self.weapon.tick()
        self.animations.update()
        self.master_image = self.animations.get_frame()
        self.update_rot(self.aiming_at, self.ZOOM)
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
