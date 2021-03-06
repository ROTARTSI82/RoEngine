# -*- coding: UTF-8 -*-

import json
import logging
import sys

from pygame.locals import *

from dev01_22_19.CONFIG import *
from dev01_22_19.data.characters.base import *
from roengine import *
from roengine.net.cUDP import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
hdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s|%(name)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                              '%H:%M:%S')
hdlr.setFormatter(formatter)
root.addHandler(hdlr)

VAL = WEAPON_KEYBINDS.keys()
CURRENT_MAP = 'untitled'
ABVAL = ABILITY_KEYBINDS.keys()

weapon_switch = Action('player', 10, 0)

__version__ = 'dev01.19.19'

test_modeLogger = logging.getLogger('server_test')


def event_logger(self, event, exclude_events=(), include_events=()):
    if event.type in exclude_events:
        return
    if event.type in include_events:
        test_modeLogger.debug("Event%s: %s", event.type, event.dict)


class ServerTest(Game):
    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1, 1])
        self.update_rects([640, 480])
        self.mouse_sprite = Obstacle([10, 10], [0, 0])
        self.mouse_pos = [0, 0]
        self.clock = pygame.time.Clock()

        self.hud_layer = Map(HUD_RES)
        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32)
        self.enter_serv_test('main')
        # REMEMBER: Update the client, too.

        buttons.set_buttons([])
        self.players = pygame.sprite.Group()
        self.map = Map([1500, 500])

        bullets.set_bounds(self.map.get_map())
        bullets.set_shootables(self.TEST_MAP.copy())
        self.running = True

    def universal_events(self, event):
        [bt.update_event(event, self.mouse_sprite) for bt in buttons.visible_bts]
        if event.type == MOUSEMOTION:
            self.mouse_pos = event.pos
            self.mouse_sprite.rect.center = self.hud_layer.translate_pos(self.mouse_pos)
        if event.type == QUIT:
            self.terminate()

    def update_rects(self, size):
        middle = size[0] / 2, size[1] / 2
        self.quad_rects = [pygame.rect.Rect((0, 0), middle), pygame.rect.Rect((middle[0], 0), middle),
                           pygame.rect.Rect(middle, middle), pygame.rect.Rect((0, middle[1]), middle)]
        self.half_y_rects = [pygame.rect.Rect((0, 0), (size[0], middle[1])),
                             pygame.rect.Rect((0, middle[1]), (size[0], middle[1]))]
        self.half_x_rects = [pygame.rect.Rect((0, 0), (middle[0], size[1])),
                             pygame.rect.Rect((middle[0], 0), (middle[0], size[1]))]
        self.whole_rect = [pygame.rect.Rect((0, 0), size)]
        self.rects = getattr(self, RECT_MODE)
        self.rect_len = len(self.rects) - 1
        self.current_rect = self.rects[0]
        self.rect_index = 0

    def tick_rect(self):
        if self.rect_index == self.rect_len:
            self.rect_index = 0
        else:
            self.rect_index += 1
        self.current_rect = self.rects[self.rect_index]

    def global_tick(self):
        self.tick_rect()

    def event_logger(self, event, exclude_events=(), include_events=()):
        if event.type in exclude_events:
            return
        if event.type in include_events:
            test_modeLogger.debug("Event%s: %s", event.type, event.dict)

    def enter_serv_test(self, old):
        try:
            with open("./data/maps/%s.json" % CURRENT_MAP, 'r') as fp:
                map_json = json.load(fp)
            self.TEST_MAP = pygame.sprite.Group()
            for i in map_json['blocks']:
                self.TEST_MAP.add(Obstacle(i['size'], i['pos'], 1, i['color']))
            self.background_col = map_json['background']['color']
            self.spawn_locs = map_json['spawns']
        except (ValueError, IOError, KeyError):
            # TODO: Add individual try/except cluases for each element (map, background color, spawn locations)
            test_modeLogger.exception("Failed to load map: ")
            self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                                Obstacle([100, 10], [150, 428]),
                                                Obstacle([10, 400], [250, 28]),
                                                Obstacle([1920, 50], [320, 480]),
                                                Obstacle([100, 100], [320, 405]),
                                                Obstacle([50, 400], [500, 400]))
            self.background_col = [255, 255, 255]
            self.spawn_locs = [[0, 0], ]

        buttons.set_buttons([])
        self.players = pygame.sprite.Group()
        self.map = Map([1500, 500])

        bullets.set_bounds(self.map.get_map())
        bullets.set_shootables(self.TEST_MAP.copy())

    def new_player(self):
        np = BasicCharacter(self)
        np.spawn_locations = self.spawn_locs  # REMEMBER: Update the client, too.
        np.bounds = self.map.get_map()
        np.collidables = self.TEST_MAP.copy()
        bullets.shootables.add(np)
        np.onRespawn()  # Apply these changes.
        self.players.add(np)
        return np

    def exit_serv_test(self, new):
        pass

    def tick_serv_test(self):
        self.clock.tick()
        pygame.display.set_caption(str(self.clock.get_fps()))

        self.players.update(True, True)
        bullets.update()

        [i.tick() for i in factory.client_protocols.values()]

        '''
        self.map.fill(self.background_col)
        self.map.draw_group(self.TEST_MAP)
        self.map.draw_group(self.players)
        self.map.draw_group(bullets.get_group())
        self.map.scale_to(self.screen, MAP_ZOOM)

        self.screen.fill([255, 255, 255])
        self.map.blit_to(self.screen)
        pygame.display.update(self.current_rect)
        '''

        for event in pygame.event.get():
            event_logger(self, event)
            self.universal_events(event)


class MyProtocol(ServerUDP):
    player = None

    def __init__(self):
        ServerUDP.__init__(self)
        self.frame_num = 0
        self.player = game.new_player()

    def network_event(self, msg):
        for event in [pygame.event.Event(*i) for i in msg['events']]:
            self.player.update_event(event)
            if event.type == KEYDOWN:
                if event.key == K_r and self.player.mode == 'weapon':
                    self.player.weapon.force_reload()
                if event.key in ABILITY_KEYS:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.ability = self.player.abilities[ABILITY_KEYBINDS[event.key]]
                    self.player.mode = 'ability'
                if event.key in WEAPON_KEYS:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.weapon = self.player.inv[WEAPON_KEYBINDS[event.key]]
                    self.player.mode = 'weapon'

    def network_mouse(self, msg):
        self.player.aiming_at = msg['pos']

    def network_cli_settings(self, msg):
        self.player.keybinds = msg['basic_keys']
        self.player.ability_keybinds = msg['ability_keys']
        self.player.weapon_keybinds = msg['weapon_keys']
        self.player.weapon_keys = self.player.weapon_keybinds.keys()
        self.player.ability_keys = self.player.ability_keybinds.keys()
        self.player.name = msg['name']

    def tick(self):
        '''
        if self.frame_num == 0:
            self.update_players()
        if self.frame_num == 1:
            self.update_bullets()
        if self.frame_num == 2:
            self.update_self()
            self.frame_num = -1  # 0 frame wait since frame_num is incremented
        self.frame_num += 1
        '''
        sdict = {}
        sdict.update(self.update_bullets())
        sdict.update(self.update_players())
        sdict.update(self.update_self())
        sdict.update(self.update_stat())
        sdict['action'] = 'update'
        self.enque(sdict)
        self.empty_que()

    def update_players(self):
        rdict = {"action": "players", "players":
                 [[i.rect.center, i.rotation] for i in game.players.sprites() if i != self.player and i.alive]}
        return rdict

    def update_stat(self):
        try:
            stats = []
            for i in self.factory.game.players:
                stats.append([i.score, i.name, i.kills])
                if len(stats) >= 10:
                    break
            stats = sorted(stats)
            stats.reverse()
            return {"action": "stats", "stat": stats}
        except:
            return {}

    def update_bullets(self):
        return {"action": "bullets", 'bullets': [(i.rect.center, i.rotation, i.type)
                                                 for i in bullets.get_group().sprites()]}

    def update_self(self):
        identifier = str(self.player.weapon.id if self.player.mode == 'weapon' else self.player.ability.id)
        msg = {"action": "self", "pos": self.player.rect.center, "item": self.player.mode[0]+identifier,
               'hp': self.player.health, 'score': self.player.score, "rot": self.player.rotation,
               "sh": self.player.shield}
        if self.player.mode == 'weapon':
            msg.update({"ammo": self.player.weapon.ammo})
            msg["reload_prog"] = (self.player.action_manager.action_duration - self.player.action_manager.progress)
        else:
            msg["action_cool"] = self.player.ability.get_cooldown()
            msg["action_dur"] = (self.player.action_manager.action_duration - self.player.action_manager.progress)
        return msg


class MyFactory(UDPServerFactory):
    protocol=MyProtocol

    def __init__(self, host, port, max, game):
        self.game = game
        UDPServerFactory.__init__(self, host, port, max)

    def build_protocol(self, addr):
        if UDPServerFactory.build_protocol(self, addr):
            # This does nothing right now, but might be useful later
            self.verify_send({"action": "settings", "ver": __version__, "map": CURRENT_MAP}, addr)


if __name__ == "__main__":
    game = ServerTest(state='serv_test')
    factory = MyFactory("", 3000, 10, game)
    factory.load()
    game.load()
    reactor.run()
