# -*- coding: UTF-8 -*-

import pygame

from roengine import *


class DamageTracker(Text):
    def __init__(self, pos):
        self.hp = 0
        Text.__init__(self, "0", pos)

    def damage(self, damage):
        self.hp += damage
        Text.__init__(self, str(int(self.hp)), self.rect.center)

    def __str__(self):
        return str( self.rect.center)


class G111218(Game):
    screen, player, COLLIDABLES, MAP = [Dummy(), ] * 4

    def start(self, *args, **kwargs):

        DPS = 111
        ROF = 1.5

        pygame.init()

        self.screen = pygame.display.set_mode([640, 480])

        self.player = PlatformerPlayer(pygame.Surface([15, 15]).convert_alpha())
        self.COLLIDABLES = pygame.sprite.Group(DummySprite([100, 10], [100, 400]),
                                               DummySprite([100, 10], [150, 428]),
                                               DummySprite([10, 400], [250, 28]),
                                               DummySprite([1920, 50], [320, 480]),
                                               DummySprite([100, 100], [320, 405]))

        self.SHOOTABLES = pygame.sprite.Group(DamageTracker([200, 25]))

        bullets.set_shootables(self.SHOOTABLES)

        self.weapon = Shotgun(DPS, ROF, Bullet, self.player, 5, 8, 200, 6.0)
        self.firing = False

        self.proj = pygame.sprite.Group()
        self.player.collidables = self.COLLIDABLES
        self.MAP = Map([1000, 1000])
        self.running = True

    def tick_main(self, *args, **kwargs):
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.COLLIDABLES)
        self.MAP.draw_group(self.SHOOTABLES)
        self.MAP.draw_sprite(self.player)
        self.MAP.scale_to(self.screen, [2, 2])
        bullets.draw(self.MAP)
        self.MAP.get_scroll(self.player.rect.center, self.screen,
                            [self.screen.get_width()/2, self.screen.get_height()/2], True, [True, False])
        self.MAP.blit_to(self.screen)
        ammo = Text("%s/%s"%(self.weapon.ammo, self.weapon.reserve), (100, 100))
        sprites = Text(str(len(bullets._bullets)), (100, 50))
        self.screen.blit(ammo.image, ammo.rect)
        self.screen.blit(sprites.image,sprites.rect)
        self.player.update()
        mp = self.MAP.translate_pos(pygame.mouse.get_pos())
        self.player.update_rot(mp)
        self.player.check_bounds(self.MAP.get_map())
        bullets.update()
        self.weapon.tick()
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
                if event.key == pygame.K_r:
                    self.weapon.force_reload()

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
