# -*- coding: UTF-8 -*-

import pygame
import time
import math
import random
import os
import logging
import sys

# from generic_logging import new_handlers

from roengine import *
from roengine.util.action import ActionManager, Action

from roengine.gui.popup import *



class Enemy(PlatformerPlayer):
    hp = 100
    def __init__(self):
        PlatformerPlayer.__init__(self, pygame.Surface([15, 15]))
        self.image.fill([0, 255, 0])
        self.last_att =0
        self.shooter = random.choice(SHOOTER_CHANCES)
        if self.shooter:
            self.weapon = Shotgun(75, 1.5, Bullet, None, 5, 12, float('inf'), 4.75, (1.5, 1.5))
            self.weapon.parent=self
            self.weapon.actionManager = ActionManager()
            self.image.fill([0, 0, 255])
        self.at_cool = 0.5
        self.speed = 3

    def damage(self, damage, bullet):
        global MAX_ENEMIES
        if bullet.parent is game.player:
            game.score += damage*(int(self.shooter)+1)
            game.enemy_cooldown = max(1.0 / max(game.score / (100.0 * Enemy.hp), 1), 0.25)
            MAX_ENEMIES = max(min(game.score / (3 * Enemy.hp), 60), 1)
            game.weapon.reserve += 5
        self.hp -= damage
        bullet.req_kill()
        if self.hp <= 0:
            logger.info("%s was killed. (is_shooter: %s)", self, self.shooter)
            #game.weapon.reserve += 10
            self.kill()

    def attack(self):
        if time.time()-self.last_att > self.at_cool:
            logger.info('%s meleed player for 15 damage', self)
            game.player.hp -= 15
            game.hp_bar.val = game.player.hp
            game.hp_bar.update()
            self.last_att = time.time()

    def update(self):
        if self.shooter:
            self.weapon.tick()
            self.weapon.tick_fire(game.player.rect.center, True)
        self.input_state = {"forward": False, "backward": False, "jump": True}
        if game.player.rect.x > self.rect.x:
            self.input_state['forward'] = True
        elif game.player.rect.x < self.rect.x:
            self.input_state['backward'] = True
        PlatformerPlayer.update(self)


class TestPop(PopUp):
    def __init__(self, *args):
        PopUp.__init__(self, *args)
        self.filter = pygame.Surface([0, 0])
        self.filter_color = pygame.Color(0, 0, 0, 128)
        self.text = Text("GAME OVER!", [0, 0], None, 75, [255, 255, 255])

    def tick_main(self):
        global game
        self.filter = pygame.Surface(game.screen.get_size(), pygame.SRCALPHA, 32).convert()
        self.filter.fill(self.filter_color)
        self.filter.set_alpha(200)
        game.screen.blit(self.filter, [0,0])
        game.hud._map = game.clear.copy()
        game.hud.blit(self.text.image, [10, 10])
        game.hud.blit(Text("Score: "+str(int(game.score)), fg=[255, 255, 255], size=50).image, [100, 75])
        game.hud.blit(Text("Hi: " + str(int(game.hi)), fg=[255, 255, 255], size=50).image, [100, 125])
        game.hud.scale_to(game.screen, [1, 1])
        game.hud.blit_to(game.screen)
        pygame.display.flip()
        if game.score > game.hi:
            game.hi = game.score
        for event in game.latest_events:
            if event.type == pygame.QUIT:
                game.terminate()
            if event.type == pygame.VIDEORESIZE:
                game.screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for e in game.enemies:
                        game.SHOOTABLES.remove(e)
                    game.enemies = pygame.sprite.Group()
                    popups.close()
        if self.pause:
            game.latest_events = []

    def open(self):
        logger.info("Game over! Saving high score...")
        if game.score > game.hi:
            game.hi = game.score
        with open("hi.txt", "w") as fp:
            fp.write(str(game.hi))
        self.is_open = True

    def close(self, reason):
        logger.info("Restarting game...")
        game.last_enemy_spawned = time.time()
        game.score = 0
        game.player.hp = 100
        game.weapon.ammo = game.weapon.maxMag
        game.weapon.reserve = AMMO
        game.player.position = pygame.math.Vector2(0, 0)
        self.is_open = False
        with open("hi.txt", "w") as fp:
            fp.write(str(game.hi))


class DamageTracker(Text):
    def __init__(self, pos):
        self.hp = 0
        Text.__init__(self, "0", pos)

    def damage(self, damage, bullet):
        self.hp += damage
        bullet.req_kill()
        Text.__init__(self, str(int(self.hp)), self.rect.center)

    def __str__(self):
        return str( self.rect.center)


class Player(PlatformerPlayer):
    def __init__(self, surf):
        PlatformerPlayer.__init__(self, surf)
        self.hp = 100

    def damage(self, damage, bullet):
        logger.info("%s damaged player for %s damage", bullet, damage)
        bullet.req_kill()
        self.hp -= damage
        game.hp_bar.val = self.hp
        game.hp_bar.update()


class G111218(Game):
    screen, player, COLLIDABLES, MAP = [Dummy(), ] * 4

    def start(self, *args, **kwargs):
        logger.info("Initializing pygame...")

        DPS = 175
        ROF = 8

        pygame.init()

        self.screen = pygame.display.set_mode([640, 480], pygame.RESIZABLE | pygame.SRCALPHA, 32)
        self.hud = Map([640, 480])
        # self.hud._map.set_colorkey([255, 0, 0])
        self.clear = pygame.Surface([640, 480], pygame.SRCALPHA, 32).convert_alpha()

        self.player = Player(pygame.Surface([15, 15]).convert_alpha())
        self.player.image.fill([255, 0, 0])
        self.COLLIDABLES = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                               Obstacle([100, 10], [150, 428]),
                                               Obstacle([10, 400], [250, 28]),
                                               Obstacle([1920, 50], [320, 480]),
                                               Obstacle([100, 100], [320, 405]))

        self.enemies = pygame.sprite.Group()
        self.hp_bar = ProgressBar(110, self.player.hp, [500, 20], [2, 2], colors=((255, 0, 0), (128, 128, 128)))
        self.hp_bar.rect.top = 10
        self.hp_bar.rect.centerx = 320

        self.SHOOTABLES = pygame.sprite.Group(DamageTracker([200, 25]))
        self.SHOOTABLES.add(self.COLLIDABLES)
        self.SHOOTABLES.add(self.player)
        self.game_over = TestPop()

        bullets.set_shootables(self.SHOOTABLES)
        bullets.set_bounds(self.MAP.get_map())
        self.action_manager = ActionManager()
        Weapon.actionManager = self.action_manager
        self.weapon = testwp
        self.weapon.parent = self.player
        self.firing = False
        self.clock = pygame.time.Clock()

        pygame.time.set_timer(pygame.USEREVENT+1, 1000)

        self.proj = pygame.sprite.Group()
        self.score = 0
        if os.path.exists("hi.txt"):
            with open("hi.txt", "r") as fp:
                self.hi = float(fp.read())
        else:
            self.hi = 0
        self.player.collidables = self.COLLIDABLES
        self.MAP = Map([1000, 1000])
        self.running = True
        pygame.mouse.set_cursor(*reticule)

        self.last_enemy_spawned = time.time()
        self.enemy_cooldown = 1

        pygame.display.set_caption("The Great Red Sqaure: The Green Square's Revenge")
        pygame.display.set_icon(self.player.image)
        logger.info("pygame initialized.")

    def tick_main(self, *args, **kwargs):
        global MAX_ENEMIES
        self.clock.empty_que()
        # pygame.display.set_caption(str(self.clock.get_fps()))
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.COLLIDABLES)
        self.MAP.draw_group(self.SHOOTABLES)
        self.MAP.draw_group(self.enemies)
        bullets.draw(self.MAP)
        self.MAP.draw_sprite(self.player)
        # pygame.draw.rect(self.MAP.get_map(), [0, 0, 0], self.player.rect, 1)
        self.MAP.scale_to(self.screen, [2, 2])
        self.MAP.get_scroll(self.player.rect.center, self.screen,
                            [self.screen.get_width()/2, self.screen.get_height()/2], [True, False])
        self.screen.blit(self.MAP.scaled, self.MAP._scroll)
        ammo = Text("%s/%s"%(self.weapon.ammo, self.weapon.reserve), (100, 50), bg=(255, 255, 255))
        sprites = Text("SCORE: "+str(int(self.score)), (100, 30), bg=(255, 255, 255))
        sprites.rect.center = self.hp_bar.rect.center
        sprites.rect.top = self.hp_bar.rect.bottom + 5
        hp = Text("HEALTH: " + str(math.ceil(self.player.hp))[:-2], (100, 10), fg=(0, 0, 0))
        hp.rect.center = self.hp_bar.rect.center
        reload = Text(str(self.action_manager.action_duration-self.action_manager.progress)[:3],
                      bg=(255, 255, 255))
        reload.rect.center = sprites.rect.center
        reload.rect.left = sprites.rect.right + 50
        # self.hud.fill([255, 0, 0])
        self.hud._map = self.clear.copy()
        self.hud.blit(ammo.image, ammo.rect)
        self.hud.blit(sprites.image,sprites.rect)
        self.hud.blit(self.hp_bar.image, self.hp_bar.rect)
        self.hud.blit(hp.image, hp.rect)
        if reload.text != "0":
            self.hud.blit(reload.image, reload.rect)
        self.hud.scale_to(self.screen, [1, 1])
        self.hud.blit_to(self.screen)
        self.player.update()
        self.enemies.update()

        mp = self.MAP.translate_pos(pygame.mouse.get_pos())

        # Aimbot lel
        #targ = random.choice(self.enemies.sprites()).rect.center if self.enemies else [100, 100]
        #mp = self.MAP.get_pos(targ)
        #pygame.mouse.set_pos(mp)

        self.player.update_rot(mp)
        self.player.check_bounds(self.MAP.get_map())
        bullets.update()
        self.weapon.tick()
        self.latest_events = pygame.event.get()
        if time.time()-self.last_enemy_spawned > self.enemy_cooldown and len(self.enemies) < MAX_ENEMIES:
            self.last_enemy_spawned = time.time()
            ne = Enemy()
            #ne.position = pygame.math.Vector2(random.randint(0, self.MAP._map.get_width()),
            #                                  random.randint(0, self.MAP._map.get_height()))
            ne.collidables = self.COLLIDABLES
            self.enemies.add(ne)
            logger.info("Spawning new enemy... (is_shooter: %s)", ne.shooter)
            self.SHOOTABLES.add(ne)
        if popups.tick():
            self.firing = False
            self.player.input_state = {"forward": False, "backward": False, "jump": False}
            return
        for i in pygame.sprite.spritecollide(self.player, self.enemies, False):
            i.attack()
        if self.player.hp <= 0:
            popups.open(self.game_over)
        pygame.display.flip()
        if self.firing:
            self.weapon.tick_fire(mp, True)
        for event in self.latest_events:
            if event.type == pygame.USEREVENT + 1 and self.player.hp > 0:
                self.score += 1
                self.player.hp += REGEN_RATE
                self.player.hp = min(self.player.hp, 110)
                self.enemy_cooldown = max(1.0 / max(self.score / (100.0 * Enemy.hp), 1), 0.25)
                MAX_ENEMIES = max(min(self.score / (3 * Enemy.hp), 60), 1)
                self.hp_bar.val = self.player.hp
                self.hp_bar.update()
            if event.type == pygame.QUIT:
                self.terminate()
            self.player.update_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.firing = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.firing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    self.player.hp = 0
                if event.key == pygame.K_r:
                    self.weapon.force_reload()
                    logger.info("Reloading...")
                if event.key == pygame.K_i:
                    logger.info("Interrupting current action...")
                    self.action_manager.do_action(Action("interrupt", -2, 0), True)
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)

    def stop(self, *args, **kwargs):
        pygame.quit()
        self.running = False

    def new_player(self):
        image = pygame.Surface([25, 25]).convert_alpha()
        image.fill([255, 0, 0])
        return PlatformerPlayer(image)


if __name__ == "__main__":
    logger = logging.getLogger('main.endless_mode')
    logger.setLevel(logging.DEBUG)
    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setFormatter(logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                                        '%H:%M:%S'))
    logger.addHandler(hdlr)

    #for h in new_handlers():
    #    logger.addHandler(h)

    logger.info("Starting...")

    AMMO = 500
    SHOOTER_CHANCES = [False,]
    REGEN_RATE = 3
    MAX_ENEMIES = 10
    testwp =  Weapon(105, 9, Bullet, None, 40, float('inf'), 3, (1.6, 1.6))
    game = G111218()
    game.load()
    reactor.run()
    logger.info("Stopped.")
