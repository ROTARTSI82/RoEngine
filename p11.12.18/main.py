# -*- coding: UTF-8 -*-

import pygame

from roengine import *
from roengine.util.action import ActionManager, Action

from roengine.gui.popup import *


class TestPop(PopUp):
    def __init__(self):
        PopUp.__init__(self, 'main')
        self.filter = pygame.Color(0, 0, 0, 128)

    def tick_main(self, screen):
        # screen.fill(self.filter)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    popups.close()

    def open(self):
        print ("YAY! OPENED!")
        self.is_open = True

    def close(self, reason):
        print ("CLOSED!", reason)
        self.is_open = False


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


class G111218(Game):
    screen, player, COLLIDABLES, MAP = [Dummy(), ] * 4

    def start(self, *args, **kwargs):

        DPS = 75
        ROF = 10

        pygame.init()

        self.screen = pygame.display.set_mode([640, 480], pygame.RESIZABLE)

        self.player = PlatformerPlayer(pygame.Surface([15, 15]).convert_alpha())
        self.COLLIDABLES = pygame.sprite.Group(DummySprite([100, 10], [100, 400]),
                                               DummySprite([100, 10], [150, 428]),
                                               DummySprite([10, 400], [250, 28]),
                                               DummySprite([1920, 50], [320, 480]),
                                               DummySprite([100, 100], [320, 405]))

        self.SHOOTABLES = pygame.sprite.Group(DamageTracker([200, 25]))
        self.SHOOTABLES.add(self.COLLIDABLES)
        self.test_popup = TestPop()

        bullets.set_shootables(self.SHOOTABLES)
        bullets.set_bounds(self.MAP.get_map())
        self.action_manager = ActionManager()
        Weapon.actionManager = self.action_manager
        self.weapon = Weapon(DPS, ROF, Bullet, self.player, 40, 1000, 3.0)
        self.firing = False

        self.proj = pygame.sprite.Group()
        self.player.collidables = self.COLLIDABLES
        self.MAP = Map([1000, 1000])
        self.running = True
        pygame.mouse.set_cursor(*reticule)

    def tick_main(self, *args, **kwargs):
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.COLLIDABLES)
        self.MAP.draw_group(self.SHOOTABLES)
        self.MAP.draw_sprite(self.player)
        bullets.draw(self.MAP)
        self.MAP.scale_to(self.screen, [2, 2])
        self.MAP.get_scroll(self.player.rect.center, self.screen,
                            [self.screen.get_width()/2, self.screen.get_height()/2], [True, False])
        self.screen.blit(self.MAP.scaled, self.MAP._scroll)
        ammo = Text("%s/%s"%(self.weapon.ammo, self.weapon.reserve), (100, 100))
        sprites = Text(str(len(bullets._bullets)), (100, 50))
        self.screen.blit(ammo.image, ammo.rect)
        self.screen.blit(sprites.image,sprites.rect)
        self.screen.blit(Text(str(self.action_manager.action_duration-self.action_manager.progress)).image, [0, 0])
        self.player.update()
        mp = self.MAP.translate_pos(pygame.mouse.get_pos())
        self.player.update_rot(mp)
        self.player.check_bounds(self.MAP.get_map())
        bullets.update()
        self.weapon.tick()
        if popups.tick(self.screen):
            return
        pygame.display.flip()
        if self.firing:
            self.weapon.tick_fire(mp, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            self.player.update_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.firing = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.firing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    popups.open(self.test_popup)
                if event.key == pygame.K_l:
                    self.weapon.reserve = 1000
                    # self.weapon.reload = 0.1
                    self.SHOOTABLES = pygame.sprite.Group(DamageTracker([200, 25]))
                    bullets.set_shootables(self.SHOOTABLES)
                    bullets.shootables.add(self.COLLIDABLES)
                if event.key == pygame.K_r:
                    self.weapon.force_reload()
                if event.key == pygame.K_i:
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
    game = G111218()
    game.load()
    reactor.run()
