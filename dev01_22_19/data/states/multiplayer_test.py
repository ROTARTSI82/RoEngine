# -*- coding: UTF-8 -*-

import json
import logging
from math import ceil

from pygame.locals import *

from dev01_22_19.CONFIG import *
from dev01_22_19.data.characters.base import *
from roengine import *
from roengine.game.animation import from_spritesheet
from roengine.game.recording import GameRecorder
from roengine.net.cUDP import *
from roengine.net.rencode import dumps

test_modeLogger = logging.getLogger('multiplayer_test')

VALID_SERV_VER = ['dev01.19.19', ]
DEBUG = True
PREDICTION = False
NAME = raw_input("Enter your nickname: ")


class RespawnPopup(PopUp):
    def __init__(self, game):
        PopUp.__init__(self)
        self.game = game
        self.text = Text("Oh noes! You died!", (HUD_RES[0] / 2, HUD_RES[1] / 2), fg=(255, 255, 255))
        self.filter = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA, 32).convert()
        self.filter.set_alpha(200)

    def open(self):
        self.update_filter()
        self.is_open = True

    def update_filter(self):
        self.filter = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA, 32).convert()
        self.filter.set_alpha(200)

    def tick_main(self):
        if self.game.player.alive:
            # print ("CLOSING POPUP")
            popups.close()
        self.game.screen.blit(self.filter, [0, 0])
        self.game.hud_layer._map = self.game.clear_surf.copy()
        self.game.hud_layer.draw_sprite(self.text)
        for event in pygame.event.get():
            self.game.universal_events(event)
            if event.type == VIDEORESIZE:
                self.update_filter()

    def close(self, reason):
        self.is_open = False


class LeaderboardPopup(PopUp):
    def __init__(self, game):
        PopUp.__init__(self)
        self.game = game
        self.text = Text("Leader Board", (HUD_RES[0]/2, 50), fg=(255, 255, 255))
        self.board = [Text("", (HUD_RES[0] / 2, 50 + 50 * i), fg=(255, 255, 255)) for i in range(1, 11)]
        self.filter = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA, 32).convert()
        self.filter.set_alpha(200)

    def open(self):
        self.update_filter()
        self.is_open = True

    def update_filter(self):
        self.filter = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA, 32).convert()
        self.filter.set_alpha(200)

    def tick_main(self):
        self.game.screen.blit(self.filter, [0, 0])
        self.game.hud_layer._map = self.game.clear_surf.copy()
        self.game.hud_layer.draw_sprite(self.text)
        for i, v in enumerate(self.game.leaders):
            # stats.append([i.score, i.name, i.kills])
            self.board[i].update_text("%s: %s | %i points | %i kills" % (i + 1, v[1], ceil(v[0]), v[2]))
        for i in self.board:
            self.game.hud_layer.draw_sprite(i)
        for event in pygame.event.get():
            self.game.universal_events(event)
            if event.type == KEYDOWN:
                if event.key == K_l:
                    popups.close()
            if event.type == VIDEORESIZE:
                self.update_filter()

    def close(self, reason):
        self.is_open = False


class DummyPlayer(pygame.sprite.Sprite):
    def __init__(self, args, image):
        self.pos, self.rot = args
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.image = pygame.transform.rotozoom(self.image, self.rot, ZOOM_VALS['player'])


class DummyBullet(pygame.sprite.Sprite):
    def __init__(self, args, image):
        self.pos, self.rot, self.type = args
        pygame.sprite.Sprite.__init__(self)
        self.image = image[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.image = pygame.transform.rotozoom(self.image, self.rot, ZOOM_VALS['bullets'][self.type])


class Client(EnqueUDPClient):
    def __init__(self, host, port, game):
        EnqueUDPClient.__init__(self, host, port)
        self.send_bytes = 0
        self.recv_bytes = 0
        self.start = time.time()
        self.game = game
        self.verify_send({"action": "cli_settings", "name": NAME, "ability_keys": ABILITY_KEYBINDS,
                          "basic_keys": BASIC_KEYBINDS, "weapon_keys": WEAPON_KEYBINDS})

    def tick(self):
        if DEBUG and self.send_que:
            self.send_bytes += len(dumps(self.send_que))
        self.empty_que()

    def datagramReceived(self, message, address):
        if DEBUG:
            self.recv_bytes += len(message)
        EnqueUDPClient.datagramReceived(self, message, address)

    def network_update(self, msg, addr):
        self.game.recording.record_get(msg, addr)
        self.game.leaders = msg['stat']
        bullets._bullets = pygame.sprite.Group(*[DummyBullet(i, self.game.bul_pics) for i in msg['bullets']])
        self.game.players = pygame.sprite.Group(*[DummyPlayer(i, self.game.pic) for i in msg['players']])

        self.game.player.score = msg['score']
        self.game.player.rect.center = msg['pos']
        self.game.player.shield = msg['sh']
        self.game.player.health = msg['hp']
        self.game.player.update_pos()
        self.game.player.rotation = msg['rot']
        self.game.player.mode = 'weapon' if msg['item'][0] == 'w' else 'ability'
        if self.game.player.mode == 'weapon':
            self.game.player.weapon = self.game.player.inv[msg['item'][1:]]
            self.game.weapon_txt.update_text("Item: " + str(self.game.player.weapon))
            self.game.player.weapon.ammo = msg['ammo']
            self.game.reload_txt.update_text("%.1f" % msg["reload_prog"])
        if self.game.player.mode == 'ability':
            self.game.reload_txt.update_text("%.1f" % msg["action_cool"])
            # action_dur = "%.1f" %
            self.game.ammo_txt.update_text("%.1f" % msg['action_dur'])
            self.game.player.ability = self.game.player.abilities[msg['item'][1:]]
            self.game.weapon_txt.update_text("Ability: " + str(self.game.player.ability))

    def network_settings(self, msg, addr):
        self.game.recording.record_get(msg, addr)
        if not msg['ver'] in VALID_SERV_VER:
            test_modeLogger.critical("Invalid server version: %s", msg['ver'])
        try:
            with open("./data/maps/%s.json" % msg['map'], 'r') as fp:
                map_json = json.load(fp)
            self.game.TEST_MAP = pygame.sprite.Group()
            for i in map_json['blocks']:
                self.game.TEST_MAP.add(Obstacle(i['size'], i['pos'], 1, i['color']))
            self.game.background_col = map_json['background']['color']
            self.game.spawn_locs = map_json['spawns']
            self.game.player.spawn_locations = self.game.spawn_locs
            self.game.player.onRespawn()
        except (ValueError, IOError, KeyError):
            # TODO: Add individual try/except cluases for each element (map, background color, spawn locations)
            test_modeLogger.exception("Failed to load map: ")


def event_logger(self, event, exclude_events=(), include_events=()):
    if event.type in exclude_events:
        return
    if event.type in include_events:
        test_modeLogger.debug("Event%s: %s", event.type, event.dict)


def enter_mult_test(self, old):
    self.leaders = []
    self.recording = GameRecorder()
    self.recording.start()
    self.client = Client('127.0.0.1', 3000, self)
    self.client.load()
    sheet = pygame.image.load("./data/sprites/Player.png")
    self.pic = from_spritesheet([0, 0, 32, 32], sheet)
    self.bul_pics = [from_spritesheet([32, 96, 32, 32], sheet), from_spritesheet([0, 96, 32, 32], sheet)]
    self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                        Obstacle([100, 10], [150, 428]),
                                        Obstacle([10, 400], [250, 28]),
                                        Obstacle([1920, 50], [320, 480]),
                                        Obstacle([100, 100], [320, 405]),
                                        Obstacle([50, 400], [500, 400]))
    self.spawn_locs = [[0, 0]]
    self.background_col = [255, 255, 255]
    # REMEMBER: Update the server, too.

    buttons.set_buttons([])
    self.players = pygame.sprite.Group()
    self.player = BasicCharacter(self)
    self.map = Map([1500, 500])
    self.player.bounds = self.map.get_map()
    self.player.spawn_locations = self.spawn_locs  # REMEMBER: Update the server, too.

    self.hp_bar = ProgressBar((0, self.player.max_hp), 100,
                              (HUD_RES[0]-200, 20), (2, 2), ((255, 0, 0), (128, 128, 128)))
    self.hp_bar.rect.center = HUD_RES[0]/2, 15
    self.sh_bar = ProgressBar((0, self.player.max_shield[0]), 100,
                              (HUD_RES[0]-200, 20), (2, 2), ((0, 0, 255), (128, 128, 128)))
    self.sh_bar.rect.center = HUD_RES[0] / 2, 40

    bullets.set_bounds(self.map.get_map())
    self.player.collidables = self.TEST_MAP.copy()
    bullets.set_shootables(self.TEST_MAP.copy())

    self.reload_progress = self.player.action_manager.action_duration - self.player.action_manager.progress
    self.reload_txt = Text(str(self.reload_progress)[:3], bg=(255, 255, 255))
    self.reload_txt.rect.right = HUD_RES[0] - 100
    self.reload_txt.rect.centery = 65

    self.weapon_txt = Text("Item: " + str(self.player.weapon), bg=(255, 255, 255))
    self.weapon_txt.rect.center = HUD_RES[0] / 2, 65

    self.debug_txt = Text("Recv: 0 | Send: 0", bg=(255, 255, 255))
    self.debug_txt.rect.centerx = HUD_RES[0] / 2
    self.debug_txt.rect.bottom = HUD_RES[1] - 5

    self.hp_txt = Text("Health: 100")
    self.hp_txt.rect.center = self.hp_bar.rect.center

    self.sh_txt = Text("Shield: 100")
    self.sh_txt.rect.center = self.sh_bar.rect.center

    self.kill_txt = Text("Score: 0", bg=(255, 255, 255))
    self.kill_txt.rect.center = HUD_RES[0]/2, 87

    self.ammo_txt = Text(str(self.player.weapon.ammo) + '/inf', bg=(255, 255, 255))
    self.ammo_txt.rect.left = 100
    self.ammo_txt.rect.centery = 65

    self.respawn = RespawnPopup(self)
    self.leaderboard = LeaderboardPopup(self)

    self.initiated.append('multiplayer_test')
    self.player.onRespawn()  # Apply the changes we made.


def exit_mult_test(self, new):
    self.recording.stop()
    self.recording.save("/Users/Grant/Downloads/latest.replay")
    if new == 'main_menu':
        buttons.set_buttons(self.main_menu_bts)


def tick_mult_test(self):
    self.clock.tick()
    self.client.tick()
    pygame.display.set_caption(str(self.clock.get_fps()))

    self.player.update(PREDICTION, False)
    # bullets.update()  # Its full of obstacle objects lol

    if (not self.player.alive) and (not self.respawn.is_open):
        # print ("Opening popup")
        popups.open(self.respawn)

    self.hp_bar.val = self.player.health
    self.sh_bar.val = self.player.shield
    self.hp_bar.update()
    self.sh_bar.update()
    self.sh_txt.update_text("Shield: %i" % ceil(self.player.shield))
    self.hp_txt.update_text("Health: %i" % ceil(self.player.health))
    self.kill_txt.update_text("Score: %i" % ceil(self.player.score))
    if DEBUG:
        since_start = (time.time() - self.client.start) * 1000  # Measure in Kb
        txt = "Recv: %.2fKB/s | Send: %.2fKB/s" % (self.client.recv_bytes / since_start,
                                                   self.client.send_bytes / since_start)
        self.debug_txt.update_text(txt)
    if self.player.mode == 'weapon':
        # self.reload_progress = "%.1f" % \
        # self.reload_txt.update_text(self.reload_progress)

        self.ammo_txt.update_text(str(self.player.weapon.ammo) + '/inf')
    else:
        pass  # this stuff is handled in network_update
        # self.reload_txt.update_text("%.1f" % self.player.ability.get_cooldown())
        # action_dur = "%.1f" % (self.player.action_manager.action_duration - self.player.action_manager.progress)
        # self.ammo_txt.update_text(action_dur)

    self.screen.fill([255, 255, 255])

    self.hud_layer._map = self.clear_surf.copy()
    self.hud_layer.draw_group(buttons.visible_bts)
    self.hud_layer.draw_sprite(self.kill_txt)
    self.hud_layer.draw_sprite(self.hp_bar)
    self.hud_layer.draw_sprite(self.hp_txt)
    self.hud_layer.draw_sprite(self.sh_bar)
    self.hud_layer.draw_sprite(self.sh_txt)
    if DEBUG:
        self.hud_layer.draw_sprite(self.debug_txt)
    if self.ammo_txt.text != '0.0':
        self.hud_layer.draw_sprite(self.ammo_txt)
    self.hud_layer.draw_sprite(self.weapon_txt)
    if self.reload_txt.text != '0.0':
        self.hud_layer.draw_sprite(self.reload_txt)

    self.map.fill(self.background_col)
    self.map.draw_group(bullets.get_group())
    self.map.draw_group(self.TEST_MAP)
    self.map.draw_sprite(self.player)
    self.map.draw_group(self.players)
    self.map.get_scroll(self.player.rect.center, self.screen, (self.screen.get_width()/2,
                                                               self.screen.get_height()/2), (True, True))
    self.map.scale_to(self.screen, MAP_ZOOM)
    self.map.blit_to(self.screen)

    popup_open = popups.tick()
    self.hud_layer.scale_to(self.screen, [1, 1])
    self.hud_layer.blit_to(self.screen)

    pygame.display.update(self.current_rect)

    if popup_open:
        self.player.firing = False
        self.player.input_state = {"forward": False, "backward": False, "jump": False}
        return
    send = []
    self.client.enque({"action": 'mouse', "pos": self.player.aiming_at})
    for event in pygame.event.get():
        if event.type == QUIT:
            self.recording.stop()
            self.recording.save("/Users/Grant/Downloads/latest.replay")
        event_logger(self, event)
        self.player.update_event(event, False)
        self.universal_events(event)
        if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
            send.append([event.type, {"button": event.button}])
        if event.type == KEYDOWN:
            send.append([event.type, {"key": event.key}])
            if event.key == K_l:
                popups.open(self.leaderboard)
            '''
            if event.key == K_DOWN:
                self.player.health -= 10
            if event.key == K_UP:
                self.player.health += 10
            '''
            if event.key == K_b:
                self.update_state('main_menu')
        if event.type == KEYUP:
            send.append([event.type, {"key": event.key}])
    if send:
        self.client.enque({"action": "event", "events": send})
