import pygame

from genericClasses.clinet_classes import GenericUDPClient
from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class CustomClient(GenericUDPClient):
    def network_update_pos(self, message, address):
        global markerpos
        markerpos = message["pos"]

    def network_terminate(self, message, address):
        reactor.stop()


def update():
    global markerpos
    screen.fill([255, 255, 255])
    screen.blit(marker, markerpos)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            reactor.stop()


pygame.init()
screen = pygame.display.set_mode([640, 480])
running = True
marker = pygame.Surface([50, 50])
markerpos = [0,0]

p = CustomClient("127.0.0.1", 8000)

tick = LoopingCall(update)
tick.start(0)

p.load()
reactor.run()
