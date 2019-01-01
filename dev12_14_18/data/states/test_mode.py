# -*- coding: UTF-8 -*-

import logging

from dev12_14_18.data.characters.base import *
from pygame.locals import *
from roengine import *
from dev12_14_18.CONFIG import *

VAL = WEAPON_KEYBINDS.keys()

ABVAL = ABILITY_KEYBINDS.keys()

weapon_switch = Action('player', 10, 0)

test_modeLogger = logging.getLogger('test_mode')


def event_logger(self, event, exclude_events=(), include_events=()):
    if event.type in exclude_events:
        return
    if event.type in include_events:
        test_modeLogger.debug("Event%s: %s", event.type, event.dict)


def enter_test_mode(self, old):
    self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                        Obstacle([100, 10], [150, 428]),
                                        Obstacle([10, 400], [250, 28]),
                                        Obstacle([1920, 50], [320, 480]),
                                        Obstacle([100, 100], [320, 405]),
                                        Obstacle([50, 400], [500, 400]))

    buttons.set_buttons([])
    self.player = BasicCharacter(self)
    self.map = Map([1500, 500])
    self.player.bounds = self.map.get_map()

    self.hp_bar = ProgressBar((0, 100), 100, (HUD_RES[0]-200, 25), (2, 2), ((255, 0, 0), (128, 128, 128)))
    self.hp_bar.rect.center = HUD_RES[0]/2, 25
    bullets.set_bounds(self.map.get_map())

    self.player.collidables = self.TEST_MAP.copy()
    bullets.set_shootables(self.TEST_MAP.copy())

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

    self.enemies = pygame.sprite.Group()
    self.initiated.append('test_mode')


def exit_test_mode(self, new):
    if new == 'main_menu':
        buttons.set_buttons(self.main_menu_bts)


def tick_test_mode(self):
    self.clock.tick()
    pygame.display.set_caption(str(self.clock.get_fps()))

    self.player.update()
    bullets.update()
    self.enemies.update(self.player)

    self.hp_bar.val = self.player.health
    self.hp_bar.update()
    self.hp_txt.update_text("Health: " + str(self.player.health))
    if self.player.mode == 'weapon':
        self.reload_progress = "%.1f"%(self.player.action_manager.action_duration - self.player.action_manager.progress)
        self.reload_txt.update_text(self.reload_progress)

        self.ammo_txt.update_text(str(self.player.weapon.ammo) + '/inf')
    else:
        self.reload_txt.update_text("%.1f" % self.player.ability.get_cooldown())
        action_dur = "%.1f" % (self.player.action_manager.action_duration - self.player.action_manager.progress)
        self.ammo_txt.update_text(action_dur)

    self.hud_layer._map = self.clear_surf.copy()
    self.hud_layer.draw_group(buttons.visible_bts)
    self.hud_layer.draw_sprite(self.hp_bar)
    self.hud_layer.draw_sprite(self.hp_txt)
    if self.ammo_txt.text != '0.0':
        self.hud_layer.draw_sprite(self.ammo_txt)
    self.hud_layer.draw_sprite(self.weapon_txt)
    if self.reload_txt.text != '0.0':
        self.hud_layer.draw_sprite(self.reload_txt)
    self.hud_layer.scale_to(self.screen, [1, 1])

    self.map.fill([255, 255, 255])
    self.map.draw_group(self.TEST_MAP)
    self.map.draw_sprite(self.player)
    self.map.draw_group(self.enemies)
    self.map.draw_group(bullets.get_group())
    self.map.get_scroll(self.player.rect.center, self.screen, (self.screen.get_width()/2,
                                                               self.screen.get_height()/2), (True, True))
    self.map.scale_to(self.screen, MAP_ZOOM)

    self.screen.fill([255, 255, 255])
    self.map.blit_to(self.screen)
    self.hud_layer.blit_to(self.screen)
    test_modeLogger.debug(str(self.clock.get_fps()))
    pygame.display.update(self.current_rect)

    for event in pygame.event.get():
        event_logger(self, event)
        self.player.update_event(event)
        self.universal_events(event)
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
            if event.key == K_e:
                n = TargetDummy()
                n.bounds = self.map.get_map()
                n.collidables = self.TEST_MAP.copy()
                bullets.shootables.add(n)
                self.enemies.add(n)
            if event.key in ABVAL:
                self.player.action_manager.do_action(weapon_switch, True)
                self.player.ability = self.player.abilities[ABILITY_KEYBINDS[event.key]]
                self.player.mode = 'ability'
                # self.logger.debug('ABILITY switching to %s', str(self.player.ability))
                self.weapon_txt.update_text("Ability: " + str(self.player.ability))
            if event.key == K_0:  # Instant reload
                self.player.weapon.ammo = self.player.weapon.maxMag
            if event.key in VAL:
                self.player.action_manager.do_action(weapon_switch, True)
                self.player.weapon = self.player.inv[WEAPON_KEYBINDS[event.key]]
                self.player.mode = 'weapon'
                # self.logger.debug('WEAPON switching to %s', str(self.player.weapon))
                self.weapon_txt.update_text("Item: " + str(self.player.weapon))
            if event.key == K_b:
                self.update_state('main_menu')
