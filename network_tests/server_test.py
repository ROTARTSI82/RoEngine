# -*- coding: UTF-8 -*-

import pygame
import time

from twisted.internet.task import LoopingCall
from twisted.internet.protocol import ServerFactory
from roengine import *


class CustomGame(Game):
    screen, players, COLLIDABLES, MAP, last_send_pos, send_cool = [Dummy(), ] * 6

    def start(self, *args, **kwargs):
        pygame.init()

        self.screen = pygame.display.set_mode([640, 480])

        self.players = pygame.sprite.Group()
        self.COLLIDABLES = pygame.sprite.Group(Obstacle([100, 10], [100, 400]),
                                               Obstacle([100, 10], [150, 428]),
                                               Obstacle([10, 400], [250, 28]),
                                               Obstacle([1920, 50], [320, 480]),
                                               Obstacle([100, 100], [320, 405]))

        # self.proj = pygame.sprite.Group()
        self.dummy = Obstacle([10, 10], [0, 0])
        for player in self.players: player.collidables = self.COLLIDABLES
        self.MAP = Map([1000, 1000])
        # self.markers = pygame.sprite.Group()
        self.running = True
        self.send_cool = 1.0/16
        self.last_send_pos = 0

    def tick_main(self, *args, **kwargs):
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.COLLIDABLES)
        # markers.draw(MAP._map)
        for player in self.players:
            self.MAP.draw_sprite(player)
        # self.MAP.draw_group(self.proj)
        self.MAP.scale_to(self.screen, [2, 2])
        scrollplayer = self.players.sprites()[0] if self.players.sprites() else self.dummy
        self.MAP.get_scroll(scrollplayer.rect.center, self.screen,
                            [self.screen.get_width()/2, self.screen.get_height()/2], [True, False])
        self.MAP.blit_to(self.screen)
        self.players.update()
        # self.proj.update()
        mp = self.MAP.translate_pos(pygame.mouse.get_pos())
        # for p in self.proj:
        #    p.rot_to_target(mp)
        #    p.vel_to_target(mp)

        if time.time()-self.last_send_pos > self.send_cool:
            factory.send_pos_all()
            self.last_send_pos = time.time()

        #[player.update_rot(mp) for player in self.players]
        [player.check_bounds(self.MAP.get_map()) for player in self.players]
        pygame.display.flip()
        [client.tick_player() for client in factory.clients]
        factory.empty_all()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            # [player.update_event(event) for player in self.players]
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #    self.players.add(self.new_player())
            #    for player in self.players: player.collidables = self.COLLIDABLES
            #    self.proj.add(Projectile(pygame.Surface([10, 10]).convert_alpha(), 5))
            #    print (self.proj)
            #    self.player.collidables.add(self.proj)

    def stop(self, *args, **kwargs):
        pygame.quit()
        self.running = False


class CustomProtocol(GenericTCPServer):
    player = Dummy()
    last_in = 0

    def __init__(self):
        GenericTCPServer.__init__(self)
        self.looking = [0, 0]

    def network_event(self, data):
        for e in data['events']:
            self.last_in += 1
            event = pygame.event.Event(e['type'], e['dict'])
            # print "GOT EVENT", event
            self.player.update_event(event)
            try:
                self.looking = event.pos
            except: pass

    def tick_player(self):
        old_scroll = game.MAP._scroll
        scroll =game.MAP.get_scroll(self.player.rect.center, game.screen,
                                    [game.screen.get_width()/2, game.screen.get_height()/2], [True, False])
        looking = game.MAP.translate_pos(self.looking)
        game.MAP._scroll = old_scroll
        self.player.update_rot(looking)

    def send_pos(self):
        dat = {"action": "players_at", "my_pos": self.player.rect.center, "last": self.last_in,
                "players": [{"pos": i.rect.center, "rotation": i.rotation} for i in game.players]
               }
        #print dat
        self.enque(dat)


class CustomFactory(GenericServerFactory):
    protocol = CustomProtocol

    def buildProtocol(self, addr):
        print ("New client:", addr)

        np = ServerFactory.buildProtocol(self, addr)
        np.address = addr

        if len(self.clients) < self.max_clients:
            self.clients.append(np)
        else:
            print ("Game full. Kicking", addr)
            np.enque({"action": "kick", "reason": "Game already full"})
            return np

        image = pygame.Surface([25, 25]).convert_alpha()
        image.fill([255, 0, 0])
        np.player = PlatformerPlayer(image)
        game.players.add(np.player)
        for player in game.players: player.collidables = game.COLLIDABLES
        return np

    def send_pos_all(self):
        for client in self.clients:
            client.send_pos()


if __name__ == "__main__":
    factory = CustomFactory("127.0.0.1", 8000, 2)
    factory.load()
    game = CustomGame()
    game.load()
    reactor.run()
