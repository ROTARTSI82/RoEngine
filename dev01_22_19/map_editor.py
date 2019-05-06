# -*- coding: UTF-8 -*-

# -*- coding: UTF-8 -*-

import json
import logging
from pprint import pprint

from pygame.locals import *

from dev01_22_19.CONFIG import *
from dev01_22_19.data.characters.base import *
from roengine import *

logger = logging.getLogger('map_editor')

LOADFILE = './data/maps/untitled.json'


def event_logger(self, event, exclude_events=(), include_events=()):
    if event.type in exclude_events:
        return
    if event.type in include_events:
        logger.debug("Event%s: %s", event.type, event.dict)


class MapEditor(Game):
    def start(self):
        pygame.init()
        self.initiated = []

        self.screen = pygame.display.set_mode(SCREEN_RES, SCREEN_FLAGS)
        self.update_rects(SCREEN_RES)

        self.hud_layer = Map(HUD_RES)
        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32)

        self.clock = pygame.time.Clock()
        self.mouse_sprite = Obstacle([10, 10], [0, 0])
        self.mouse_pos = [0, 0]

        self._state = 'test_mode'
        self.enter_test_mode('main')
        self.running = True

    def update_rects(self, size):
        middle = size[0] / 2, size[1] / 2
        self.quad_rects = [pygame.rect.Rect((0, 0), middle), pygame.rect.Rect((middle[0], 0), middle),
                           pygame.rect.Rect(middle, middle), pygame.rect.Rect((0, middle[1]), middle)]
        self.half_y_rects = [pygame.rect.Rect((0, 0), (size[0], middle[1])),
                             pygame.rect.Rect((0, middle[1]), (size[0], middle[1]))]
        self.half_x_rects = [pygame.rect.Rect((0, 0), (middle[0], size[1])),
                             pygame.rect.Rect((middle[0], 0), (middle[0], size[1]))]
        self.whole_rect = [pygame.rect.Rect((0, 0), size)]
        if RECT_MODE in ['quad_rects', 'half_y_rects', 'half_x_rects', 'whole_rect']:
            self.rects = getattr(self, RECT_MODE)
        else:
            logger.critical("Invalid option RECT_MODE: %s", RECT_MODE)
            self.rects = self.whole_rect
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

    def universal_events(self, event):
        [bt.update_event(event, self.mouse_sprite) for bt in buttons.visible_bts]
        if event.type == MOUSEMOTION:
            self.mouse_pos = event.pos
            self.mouse_sprite.rect.center = self.hud_layer.translate_pos(self.mouse_pos)
        if event.type == QUIT:
            self.terminate()
        if event.type == VIDEORESIZE:
            logger.info("VIDEORESIZE: %s", event.dict['size'])
            self.screen = pygame.display.set_mode(event.dict['size'], SCREEN_FLAGS)
            self.update_rects(event.dict['size'])

    def tick_arbitrary(self, state):
        logger.fatal("Arbitrary _state: '%s'", state)
        logger.fatal("Setting _state to 'main_menu'")
        self.update_state('main_menu')

    def unhandled_update_state(self, old, new):
        logger.warn("Arbitrary update_state: '%s' -> '%s'", old, new)

    def stop(self):
        pygame.quit()
        logger.info("Terminating...")

    def enter_test_mode(self, old):
        '''
        self.TEST_MAP = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                            Obstacle([100, 10], [150, 428]),
                                            Obstacle([10, 400], [250, 28]),
                                            Obstacle([1920, 50], [320, 480]),
                                            Obstacle([100, 100], [320, 405]),
                                            Obstacle([50, 400], [500, 400]))
        self.spawn_loc = [[0, 0], ]
        self.background_col = [255, 255, 255]
        '''
        self.TEST_MAP = pygame.sprite.Group()
        with open(LOADFILE, 'r') as fp:
            dat = json.load(fp)
        self.spawn_loc = dat['spawns']
        self.background_col = dat['background']["color"]
        for i in dat["blocks"]:
            self.TEST_MAP.add(Obstacle(i['size'], i['pos'], 1, i['color']))  # Climb difficulty isn't saved.. yet
        self.selected = None
        self.clip = None

        buttons.set_buttons([])
        self.player = BasicCharacter(self)
        self.player.spawn_locations = self.spawn_loc
        self.map = Map([1500, 500])
        self.player.bounds = self.map.get_map()

        self.hp_bar = ProgressBar((0, 100), 100, (HUD_RES[0]-200, 25), (2, 2), ((255, 0, 0), (128, 128, 128)))
        self.hp_bar.rect.center = HUD_RES[0]/2, 25
        bullets.set_bounds(self.map.get_map())
        self.spawn_sprite = Obstacle([10, 10], [0, 0], color=[0, 255, 0])

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
        self.player.onRespawn()

    def adjust_size(self, mode, amount):
        reset = False
        if self.selected is None:
            real_pos = Obstacle([0, 0], self.map.translate_pos(self.mouse_sprite.rect.center))
            for hit in pygame.sprite.spritecollide(real_pos, self.TEST_MAP, False):
                self.selected = hit
            reset = True
        self.selected.size[mode] += amount
        self.selected.update_size()
        if reset:
            self.selected = None

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

        self.map.fill(self.background_col)
        for i in self.spawn_loc:
            self.spawn_sprite.rect.center = i
            self.map.draw_sprite(self.spawn_sprite)
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
        # test_modeLogger.debug(str(self.clock.get_fps()))
        pygame.display.update(self.current_rect)

        for event in pygame.event.get():
            event_logger(self, event)
            self.player.update_event(event)
            self.universal_events(event)
            if event.type == MOUSEMOTION:
                self.player.aiming_at = self.map.translate_pos(event.pos)
                if self.selected is not None:
                    self.selected.rect.center = self.player.aiming_at
            if event.type == MOUSEBUTTONDOWN:
                if self.selected is not None:
                    self.selected = None
                    continue
                real_pos = Obstacle([0, 0], self.map.translate_pos(self.mouse_sprite.rect.center))
                for hit in pygame.sprite.spritecollide(real_pos, self.TEST_MAP, False):
                    self.selected = hit
                self.player.firing = True
            if event.type == MOUSEBUTTONUP:
                self.player.firing = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.selected = None
                    self.clip = None
                if event.key == K_e:
                    n = TargetDummy()
                    n.bounds = self.map.get_map()
                    n.collidables = self.player.collidables
                    bullets.shootables.add(n)
                    self.enemies.add(n)
                if event.key == K_n:
                    self.selected = Obstacle([10, 10], self.map.translate_pos(self.mouse_sprite.rect.center))
                    bullets.shootables.add(self.selected)
                    self.player.collidables.add(self.selected)
                    self.TEST_MAP.add(self.selected)
                if event.key == K_x:
                    if self.selected is None:
                        real_pos = Obstacle([0, 0], self.map.translate_pos(self.mouse_sprite.rect.center))
                        pygame.sprite.spritecollide(real_pos, self.TEST_MAP, True)
                    else:
                        self.selected.kill()
                        self.selected = None
                if event.key == K_b:
                    try:
                        self.background_col = input("background: ")
                        self.screen.fill(self.background_col)
                    except:
                        print ("Invalid color!")
                if event.key == K_l:
                    self.spawn_loc.append(self.map.translate_pos(self.mouse_sprite.rect.center))
                if event.key == K_k:
                    self.spawn_loc = self.spawn_loc[:-1]
                if event.key == K_UP:
                    self.adjust_size(1, +5)
                if event.key == K_DOWN and self.selected is not None:
                    self.adjust_size(1, -5)
                if event.key == K_LEFT and self.selected is not None:
                    self.adjust_size(0, -5)
                if event.key == K_RIGHT and self.selected is not None:
                    self.adjust_size(0, +5)
                if event.key == K_j:
                    self.player.onRespawn()
                if event.key == K_o and self.selected is not None:
                    reset = False
                    if self.selected is None:
                        real_pos = Obstacle([0, 0], self.map.translate_pos(self.mouse_sprite.rect.center))
                        for hit in pygame.sprite.spritecollide(real_pos, self.TEST_MAP, False):
                            self.selected = hit
                        reset = True
                    try:
                        col = input("color: ")
                        self.selected.image.fill(col)
                        self.selected.color = col
                    except:
                        print ("Invalid color!")
                    if reset:
                        self.selected = None
                if event.key == K_p:
                    if self.selected is not None:
                        self.clip = self.selected.copy()  # copy selected if nothing else available
                    real_pos = Obstacle([0, 0], self.map.translate_pos(self.mouse_sprite.rect.center))
                    for hit in pygame.sprite.spritecollide(real_pos, self.TEST_MAP, False):
                        self.clip = getattr(hit, 'copy', Dummy)()
                if event.key == K_t and self.clip is not None and self.selected is None:
                    self.selected = self.clip.copy()
                    bullets.shootables.add(self.selected)
                    self.player.collidables.add(self.selected)
                    self.TEST_MAP.add(self.selected)
                    self.selected.rect.center = self.map.translate_pos(pygame.mouse.get_pos())
                if event.key == K_RETURN:
                    exp = {"background": {"name": "solid_color", "color": self.background_col}, "blocks": [],
                           "spawns": self.spawn_loc}
                    for i in self.TEST_MAP.sprites():
                        exp["blocks"].append({"name": "solid_color", "size": i.size, "color": i.color,
                                              "pos": i.rect.center})  # Climb difficulty isn't saved.. yet
                    pprint(exp)


if __name__ == "__main__":
    game = MapEditor()
    game.load()
    reactor.run()
