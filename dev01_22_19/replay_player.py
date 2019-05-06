# -*- coding: UTF-8 -*-
import datetime
import json
from math import ceil

from dev01_22_19.data.characters.base import *
from roengine.game.recording import RecordingPlayer


class CustomPlayer(RecordingPlayer):
    def apply_packet(self, packet, actual_time, expected_time):
        bullets._bullets = pygame.sprite.Group(*[DummyBullet(i, self.game.bul_pics) for i in packet['bullets']])
        self.game.players = pygame.sprite.Group(*[DummyPlayer(i, self.game.pic) for i in packet['players']])

        self.game.player.score = packet['score']
        self.game.player.rect.center = packet['pos']
        self.game.player.health = packet['hp']
        self.game.player.shield = packet['sh']
        self.game.player.update_pos()
        self.game.player.rotation = packet['rot']
        self.game.player.image = pygame.transform.rotozoom(self.game.player.master_image, packet['rot'],
                                                           self.game.player.ZOOM)
        self.game.player.mode = 'weapon' if packet['item'][0] == 'w' else 'ability'
        if self.game.player.mode == 'weapon':
            self.game.player.weapon = self.game.player.inv[packet['item'][1:]]
            self.game.weapon_txt.update_text("Item: " + str(self.game.player.weapon))
            self.game.player.weapon.ammo = packet['ammo']
            self.game.reload_txt.update_text("%.1f" % packet["reload_prog"])
        if self.game.player.mode == 'ability':
            self.game.player.ability = self.game.player.abilities[packet['item'][1:]]
            self.game.ammo_txt.update_text("%.1f" % packet['action_dur'])
            self.game.reload_txt.update_text("%.1f" % packet["action_cool"])
            self.game.weapon_txt.update_text("Ability: " + str(self.game.player.ability))


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


def fmtdeltatime(time):
    ret = [0, 0, 0, str(time % 1)[2:]]
    for i in range(2, -1, -1):
        ret[i] = int(time % 60)
        time = int(time / 60)
    return "%.2i:%.2i:%.2i.%s" % tuple(ret)


class ReplayPlayerApp(Game):
    def start(self):
        self.replay = CustomPlayer(self)
        self.replay.set_speed(1)
        self.replay.start()
        msg = self.replay.from_file("/Users/Grant/Downloads/latest.replay")
        # print msg
        print ("===================[NOW PLAYING: /Users/Grant/Downloads/latest.replay]====================")
        print ("Created: %s" % datetime.datetime.fromtimestamp(msg['start']))
        print ("Length: %s" % fmtdeltatime(msg['len']))
        pygame.init()
        self.screen = pygame.display.set_mode([640, 480], RESIZABLE)
        self.map = Map([1500, 500])
        sheet = pygame.image.load("./data/sprites/Player.png").convert_alpha()
        self.pic = from_spritesheet([0, 0, 32, 32], sheet)
        self.bul_pics = [from_spritesheet([32, 96, 32, 32], sheet), from_spritesheet([0, 96, 32, 32], sheet)]
        self.hud_layer = Map([960, 720])
        self.player = BasicCharacter(self)
        self.player.update()
        self.players = pygame.sprite.Group()
        with open("./data/maps/%s.json" % msg['map'], 'r') as fp:
            map_json = json.load(fp)
        self.TEST_MAP = pygame.sprite.Group()
        for i in map_json['blocks']:
            self.TEST_MAP.add(Obstacle(i['size'], i['pos'], 1, i['color']))
        self.background_col = map_json['background']['color']
        self.spawn_locs = map_json['spawns']

        self.clear_surf = pygame.Surface(HUD_RES, SRCALPHA, 32).convert_alpha()

        self.hp_bar = ProgressBar((0, self.player.max_hp), 100,
                                  (HUD_RES[0] - 200, 20), (2, 2), ((255, 0, 0), (128, 128, 128)))
        self.hp_bar.rect.center = HUD_RES[0] / 2, 15
        self.sh_bar = ProgressBar((0, self.player.max_shield[0]), 100,
                                  (HUD_RES[0] - 200, 20), (2, 2), ((0, 0, 255), (128, 128, 128)))
        self.sh_bar.rect.center = HUD_RES[0] / 2, 40

        self.reload_progress = self.player.action_manager.action_duration - self.player.action_manager.progress
        self.reload_txt = Text(str(self.reload_progress)[:3], bg=(255, 255, 255))
        self.reload_txt.rect.right = HUD_RES[0] - 100
        self.reload_txt.rect.centery = 65

        self.weapon_txt = Text("Item: " + str(self.player.weapon), bg=(255, 255, 255))
        self.weapon_txt.rect.center = HUD_RES[0] / 2, 65

        self.debug_txt = Text("Ping: 0 | Recv: 0 | Send: 0", bg=(255, 255, 255))
        self.debug_txt.rect.centerx = HUD_RES[0] / 2
        self.debug_txt.rect.bottom = HUD_RES[1] - 5

        self.hp_txt = Text("Health: " + str(self.player.health))
        self.hp_txt.rect.center = self.hp_bar.rect.center

        self.sh_txt = Text("Shield: 100")
        self.sh_txt.rect.center = self.sh_bar.rect.center

        self.kill_txt = Text("Score: 0", bg=(255, 255, 255))
        self.kill_txt.rect.center = HUD_RES[0] / 2, 87

        self.ammo_txt = Text(str(self.player.weapon.ammo) + '/inf', bg=(255, 255, 255))
        self.ammo_txt.rect.left = 100
        self.ammo_txt.rect.centery = 65

        self.running = True

    def tick_main(self):
        self.replay.update()
        # self.player.update(False, is_replay=True)
        self.player.action_manager.tick()
        self.player.weapon.tick()
        self.hp_bar.val = self.player.health
        self.sh_bar.val = self.player.shield
        self.hp_bar.update()
        self.sh_bar.update()
        self.sh_txt.update_text("Shield: %i" % ceil(self.player.shield))
        self.hp_txt.update_text("Health: %i" % ceil(self.player.health))
        self.kill_txt.update_text("Score: %i" % ceil(self.player.score))
        if self.player.mode == 'weapon':
            #self.weapon_txt.update_text("Item: " + str(self.player.weapon))
            #self.reload_progress = "%.1f" % \
            #                       (self.player.action_manager.action_duration - self.player.action_manager.progress)
            #self.reload_txt.update_text(self.reload_progress)

            self.ammo_txt.update_text(str(self.player.weapon.ammo) + '/inf')
        else:
            pass  # moved into replay player
            #self.weapon_txt.update_text("Ability: " + str(self.player.ability))
            #self.reload_txt.update_text("%.1f" % self.player.ability.get_cooldown())
            #action_dur = "%.1f" % (self.player.action_manager.action_duration - self.player.action_manager.progress)
            #self.ammo_txt.update_text(action_dur)

        self.screen.fill([255, 255, 255])

        self.hud_layer._map = self.clear_surf.copy()
        self.hud_layer.draw_group(buttons.visible_bts)
        self.hud_layer.draw_sprite(self.kill_txt)
        self.hud_layer.draw_sprite(self.hp_bar)
        self.hud_layer.draw_sprite(self.hp_txt)
        self.hud_layer.draw_sprite(self.sh_bar)
        self.hud_layer.draw_sprite(self.sh_txt)
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
        self.map.get_scroll(self.player.rect.center, self.screen, (self.screen.get_width() / 2,
                                                                   self.screen.get_height() / 2), (True, True))
        self.map.scale_to(self.screen, MAP_ZOOM)
        self.map.blit_to(self.screen)

        self.hud_layer.scale_to(self.screen, [1, 1])
        self.hud_layer.blit_to(self.screen)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    self.replay.set_speed(self.replay.speed+0.5)
                    print self.replay.speed
                if event.key == K_LEFT:
                    self.replay.set_speed(self.replay.speed-0.5)
                    print self.replay.speed
            if event.type == VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
            if event.type == QUIT:
                self.terminate()

    def stop(self):
        pygame.quit()
        self.running = False


if __name__ == "__main__":
    game = ReplayPlayerApp()
    game.load()
    reactor.run()
