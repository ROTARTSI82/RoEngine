# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *

import logging, sys
from dev12_14_18.data.characters.base import *
from pygame.locals import *
from roengine import *
from roengine.net.cUDP import *
from dev12_14_18.CONFIG import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
hdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s|%(name)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                                  '%H:%M:%S')
hdlr.setFormatter(formatter)
root.addHandler(hdlr)

VAL = WEAPON_KEYBINDS.keys()

ABVAL = ABILITY_KEYBINDS.keys()

weapon_switch = Action('player', 10, 0)

test_modeLogger = logging.getLogger('server_test')


def event_logger(self, event, exclude_events=(), include_events=()):
    if event.type in exclude_events:
        return
    if event.type in include_events:
        test_modeLogger.debug("Event%s: %s", event.type, event.dict)


class ServerTest(Game):
    def start(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_RES)
        self.mouse_sprite = Obstacle([10, 10], [0, 0])
        self.mouse_pos = [0, 0]
        self.clock = pygame.time.Clock()

        self.hud_layer = Map(HUD_RES)
        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32)
        self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                            Obstacle([100, 10], [150, 428]),
                                            Obstacle([10, 400], [250, 28]),
                                            Obstacle([1920, 50], [320, 480]),
                                            Obstacle([100, 100], [320, 405]),
                                            Obstacle([50, 400], [500, 400]))

        buttons.set_buttons([])
        # self.player = BasicCharacter(self)
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

    def event_logger(self, event, exclude_events=(), include_events=()):
        if event.type in exclude_events:
            return
        if event.type in include_events:
            test_modeLogger.debug("Event%s: %s", event.type, event.dict)

    def enter_serv_test(self, old):
        self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                            Obstacle([100, 10], [150, 428]),
                                            Obstacle([10, 400], [250, 28]),
                                            Obstacle([1920, 50], [320, 480]),
                                            Obstacle([100, 100], [320, 405]),
                                            Obstacle([50, 400], [500, 400]))

        buttons.set_buttons([])
        #self.player = BasicCharacter(self)
        self.players = pygame.sprite.Group()
        self.map = Map([1500, 500])

        # self.hp_bar = ProgressBar((0, 100), 100, (HUD_RES[0] - 200, 25), (2, 2), ((255, 0, 0), (128, 128, 128)))
        # self.hp_bar.rect.center = HUD_RES[0] / 2, 25

        bullets.set_bounds(self.map.get_map())

        bullets.set_shootables(self.TEST_MAP.copy())
        '''
        self.reload_progress = self.player.action_manager.action_duration - self.player.action_manager.progress
        self.reload_txt = Text(str(self.reload_progress)[:3], bg=(255, 255, 255))
        self.reload_txt.rect.right = HUD_RES[0] - 100
        self.reload_txt.rect.centery = 55

        self.weapon_txt = Text("Item: " + str(self.player.weapon), bg=(255, 255, 255))
        self.weapon_txt.rect.center = HUD_RES[0] / 2, 55

        self.hp_txt = Text("Health: " + str(self.player.health))
        self.hp_txt.rect.center = self.hp_bar.rect.center

        self.ammo_txt = Text(str(self.player.weapon.ammo) + '/inf', bg=(255, 255, 255))
        self.ammo_txt.rect.left = 100
        self.ammo_txt.rect.centery = 55
        '''

    def new_player(self):
        np = BasicCharacter(self)
        np.bounds = self.map.get_map()
        np.collidables = self.TEST_MAP.copy()
        bullets.shootables.add(np)
        self.players.add(np)
        return np

    def exit_serv_test(self, new):
        pass

    def tick_serv_test(self):
        self.clock.tick()
        pygame.display.set_caption(str(self.clock.get_fps()))

        self.players.update()
        bullets.update()

        [i.tick() for i in factory.client_protocols.values()]

        '''
        self.hp_bar.val = self.player.health
        self.hp_bar.update()
        self.hp_txt.update_text("Health: " + str(self.player.health))
        if self.player.mode == 'weapon':
            self.reload_progress = "%.1f" % (
                        self.player.action_manager.action_duration - self.player.action_manager.progress)
            self.reload_txt.update_text(self.reload_progress)

            self.ammo_txt.update_text(str(self.player.weapon.ammo) + '/inf')
        else:
            self.reload_txt.update_text("%.1f" % self.player.ability.get_cooldown())
            action_dur = "%.1f" % (self.player.action_manager.action_duration - self.player.action_manager.progress)
            self.ammo_txt.update_text(action_dur)
        '''
        #self.hud_layer._map = self.clear_surf.copy()
        #self.hud_layer.draw_group(buttons.visible_bts)
        '''
        self.hud_layer.draw_sprite(self.hp_bar)
        self.hud_layer.draw_sprite(self.hp_txt)
        if self.ammo_txt.text != '0.0':
            self.hud_layer.draw_sprite(self.ammo_txt)
        self.hud_layer.draw_sprite(self.weapon_txt)
        if self.reload_txt.text != '0.0':
            self.hud_layer.draw_sprite(self.reload_txt)
        '''
        #self.hud_layer.scale_to(self.screen, [1, 1])

        self.map.fill([255, 255, 255])
        self.map.draw_group(self.TEST_MAP)
        #self.map.draw_sprite(self.player)
        self.map.draw_group(self.players)
        self.map.draw_group(bullets.get_group())
        #self.map.get_scroll(self.player.rect.center, self.screen, (self.screen.get_width() / 2,
        #                                                           self.screen.get_height() / 2), (True, True))
        self.map.scale_to(self.screen, MAP_ZOOM)

        self.screen.fill([255, 255, 255])
        self.map.blit_to(self.screen)
        #self.hud_layer.blit_to(self.screen)
        #test_modeLogger.debug(str(self.clock.get_fps()))
        pygame.display.update(self.hud_layer.flush_rects() + self.map.flush_rects())

        for event in pygame.event.get():
            event_logger(self, event)
            self.universal_events(event)
            '''
            self.player.update_event(event)
            if event.type == MOUSEMOTION:
                self.player.aiming_at = self.map.translate_pos(event.pos)
            if event.type == MOUSEBUTTONDOWN:
                self.player.firing = True
            if event.type == MOUSEBUTTONUP:
                self.player.firing = False
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    self.player.health -= 10
                if event.key == K_UP:
                    self.player.health += 10
                if event.key == K_r and self.player.mode == 'weapon':
                    self.player.weapon.force_reload()
                if event.key in ABVAL:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.ability = self.player.abilities[ABILITY_KEYBINDS[event.key]]
                    self.player.mode = 'ability'
                    # self.logger.debug('ABILITY switching to %s', str(self.player.ability))
                    self.weapon_txt.update_text("Ability: " + str(self.player.ability))
                if event.key in VAL:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.weapon = self.player.inv[WEAPON_KEYBINDS[event.key]]
                    self.player.mode = 'weapon'
                    # self.logger.debug('WEAPON switching to %s', str(self.player.weapon))
                    self.weapon_txt.update_text("Item: " + str(self.player.weapon))
            '''


class MyProtocol(ServerUDP):
    player = None

    def __init__(self):
        ServerUDP.__init__(self)
        self.latest = 0
        self.frame_num = 0
        self.player = game.new_player()

    def network_event(self, msg):
        if msg['num'] > self.latest:
            self.latest = msg['num']
        for event in [pygame.event.Event(*i) for i in msg['events']]:
            self.player.update_event(event)
            if event.type == MOUSEMOTION:
                self.factory.game.map.get_scroll(self.player.rect.center, self.factory.game.screen,
                                                 (self.factory.game.screen.get_width() / 2,
                                                  self.factory.game.screen.get_height() / 2), (True, True))
                self.player.aiming_at = self.factory.game.map.translate_pos(event.pos)
            if event.type == KEYDOWN:
                if event.key == K_r and self.player.mode == 'weapon':
                    self.player.weapon.force_reload()
                if event.key in ABVAL:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.ability = self.player.abilities[ABILITY_KEYBINDS[event.key]]
                    self.player.mode = 'ability'
                    # self.logger.debug('ABILITY switching to %s', str(self.player.ability))
                    #self.weapon_txt.update_text("Ability: " + str(self.player.ability))
                if event.key in VAL:
                    self.player.action_manager.do_action(weapon_switch, True)
                    self.player.weapon = self.player.inv[WEAPON_KEYBINDS[event.key]]
                    self.player.mode = 'weapon'
                    # self.logger.debug('WEAPON switching to %s', str(self.player.weapon))
                    # self.weapon_txt.update_text("Item: " + str(self.player.weapon))

    def tick(self):
        if self.frame_num == 0:
            self.update_players()
        if self.frame_num == 1:
            self.update_bullets()
        if self.frame_num == 2:
            self.update_self()
        if self.frame_num == 3:
            self.frame_num = -1
        self.frame_num += 1
        self.empty_que()

    def update_players(self):
        self.enque({"action": "players", "players":
            [i.rect.center for i in game.players.sprites() if i != self.player]})

    def update_bullets(self):
        self.enque({"action": "bullets", 'bullets': [i.rect.center for i in bullets.get_group().sprites()]})

    def update_self(self):
        identifier = str(self.player.weapon.id if self.player.mode == 'weapon' else self.player.ability.id)
        msg = {"action": "self", "last": self.latest, "pos": self.player.rect.center,
               "item": self.player.mode[0]+identifier, 'hp': self.player.health,
               'prog': [self.player.action_manager.action_duration, self.player.action_manager.action_start]}
        if self.player.mode == 'weapon':
            msg.update({"ammo": self.player.weapon.ammo})
        if self.player.mode == 'ability':
            msg.update({"cool": self.player.ability.get_cooldown()})
        self.enque(msg)


class MyFactory(UDPServerFactory):
    protocol=MyProtocol
    def __init__(self, host, port, max, game):
        self.game = game
        UDPServerFactory.__init__(self, host, port, max)


if __name__ == "__main__":
    game = ServerTest(state='serv_test')
    factory = MyFactory("127.0.0.1", 3000, 2, game)
    factory.load()
    game.load()
    reactor.run()
