# -*- coding: UTF-8 -*-

import pygame

from roengine import *


class CustomGame(Game):
    screen, players, COLLIDABLES, MAP = [Dummy(), ] * 4

    def start(self, *args, **kwargs):
        pygame.init()

        self.screen = pygame.display.set_mode([640, 480])

        self.players = pygame.sprite.Group(PlatformerPlayer(pygame.Surface([15, 15]).convert_alpha()))
        self.COLLIDABLES = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                               Obstacle([100, 10], [150, 428]),
                                               Obstacle([10, 400], [250, 28]),
                                               Obstacle([1920, 50], [320, 480]),
                                               Obstacle([100, 150], [320, 405]))

        # self.proj = pygame.sprite.Group()
        for player in self.players: player.collidables = self.COLLIDABLES
        self.MAP = Map([1000, 1000])
        # self.markers = pygame.sprite.Group()
        self.running = True

    def tick(self, *args, **kwargs):
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.COLLIDABLES)
        # markers.draw(MAP._map)
        for player in self.players:
            self.MAP.draw_sprite(player)
        # self.MAP.draw_group(self.proj)
        self.MAP.scale_to(self.screen, [2, 2])
        scrollplayer = self.players.sprites()[0]
        self.MAP.get_scroll(scrollplayer.rect.center, self.screen,
                            [self.screen.get_width()/2, self.screen.get_height()/2], True, [True, False])
        self.MAP.blit_to(self.screen)
        self.players.update()
        # self.proj.update()
        mp = self.MAP.translate_pos(pygame.mouse.get_pos())
        # for p in self.proj:
        #    p.rot_to_target(mp)
        #    p.vel_to_target(mp)
        [player.update_rot(mp) for player in self.players]
        [player.check_bounds(self.MAP.get_map()) for player in self.players]
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            [player.update_event(event) for player in self.players]
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.players.add(self.new_player())
                for player in self.players: player.collidables = self.COLLIDABLES
            #    self.proj.add(Projectile(pygame.Surface([10, 10]).convert_alpha(), 5))
            #    print (self.proj)
            #    self.player.collidables.add(self.proj)

    def stop(self, *args, **kwargs):
        pygame.quit()
        self.running = False

    def new_player(self):
        image = pygame.Surface([25, 25]).convert_alpha()
        image.fill([255, 0, 0])
        return PlatformerPlayer(image)


if __name__ == "__main__":
    game = CustomGame()
    game.load()
    reactor.run()
