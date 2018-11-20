# -*- coding: UTF-8 -*-

import pygame
import time

from roengine import *


class DummyPlayer(pygame.sprite.Sprite):
    def __init__(self, pos, rotation):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([25, 25]).convert_alpha()
        self.image.fill([255, 0, 0])
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.image = pygame.transform.rotate(self.image, float(rotation))


class CustomTCPClient(GenericTCPClient):
    tick_clock = pygame.time.Clock()

    def network_players_at(self, data):
        global game
        self.tick_clock.tick(0)
        game.my_pos = data['my_pos']
        game.players = pygame.sprite.Group()
        for i in data['players']:
            game.players.add(DummyPlayer(i['pos'], float(i['rotation'])))
        game.inp = data['inp']


class CustomGame(Game):
    screen, LISTENFOR, TYPELISTEN, MAP, players, my_pos, obstacles = [None, ] * 7

    def terminate(self, stop_args=()):
        self.running = False
        self.stop(*stop_args)
        factory.shutdown()
        reactor.stop()

    def start(self):
        pygame.init()
        self.inp = "Uninitiated"
        self.screen = pygame.display.set_mode([640, 480])
        self.running = True
        self.LISTENFOR = [pygame.K_d, pygame.K_a, pygame.K_SPACE]
        self.TYPELISTEN = [pygame.KEYDOWN, pygame.KEYUP]
        self.MAP = Map([1000, 1000])
        self.players = pygame.sprite.Group()
        self.my_pos = [0, 0]
        self.clock = pygame.time.Clock()
        self.tick_clock = pygame.time.Clock()
        self.cool = 1.0/16
        self.last_tick = 0
        self.event_que = [pygame.event.Event(pygame.MOUSEMOTION,
                                             {"pos": self.MAP.translate_pos(pygame.mouse.get_pos())}), ]
        self.obstacles = pygame.sprite.Group(DummySprite([100, 10], [100, 400]),
                                               DummySprite([100, 10], [150, 428]),
                                               DummySprite([10, 400], [250, 28]),
                                               DummySprite([1920, 50], [320, 480]),
                                               DummySprite([100, 100], [320, 405]))

    def tick_main(self):
        self.clock.tick(0)
        self.screen.fill([255, 255, 255])
        self.MAP.fill([255, 255, 255])
        self.MAP.draw_group(self.players)
        self.MAP.draw_group(self.obstacles)
        self.MAP.scale_to(self.screen, [2, 2])
        self.MAP.get_scroll(self.my_pos, self.screen,
                            [self.screen.get_width() / 2, self.screen.get_height() / 2], [True, False])
        self.MAP.blit_to(self.screen)
        self.screen.blit(Text("Frame Rate: "+str(self.clock.get_fps()) + " fps").image, [10, 10])
        ping = factory.protocol_instance.tick_clock.get_fps() if factory.protocol_instance is not None else "Uninitiated"
        self.screen.blit(Text("Update Rate: " + str(ping) + " Hz").image, [10, 30])
        if type(self.inp) != str:
            self.inp['pos'] = pygame.mouse.get_pos()
        self.screen.blit(Text("Input State: "+ str(self.inp), size=16).image, [10, 50])
        pygame.display.flip()
        if time.time()-self.last_tick > self.cool:
            self.tick_clock.tick(0)
            # print self.event_que
            factory.send({"action": "event",
                          "events": [{"type": event.type, "dict": event.dict} for event in self.event_que]})
            self.event_que = [pygame.event.Event(pygame.MOUSEMOTION,
                                                 {"pos": self.MAP.translate_pos(pygame.mouse.get_pos())}), ]

        for event in pygame.event.get():
            if event.type in self.TYPELISTEN:
                if event.key in self.LISTENFOR:
                    self.event_que.append(event)
            if event.type == pygame.QUIT:
                self.terminate()

    def stop(self):
        pygame.quit()
        self.running = False


if __name__ == "__main__":
    factory = GenericClientFactory("127.0.0.1", 8000)
    factory.protocol = CustomTCPClient
    factory.load()
    game = CustomGame()
    game.load()
    reactor.run()
