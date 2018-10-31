import pygame

from genericClasses.server_classes import GenericUDPServer
from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class CustomServer(GenericUDPServer):

    def network_connect_notify(self, m, a):
        GenericUDPServer.network_connect_notify(self, m, a)
        self.verify_send({"action": "test"}, a)

def update():
    global markerpos
    screen.fill([255, 255, 255])
    screen.blit(marker, markerpos)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            p.verify_send_to_all({"action": "terminate"})
            reactor.callLater(1, reactor.stop)
        if event.type == pygame.MOUSEMOTION:
            markerpos = event.pos
            p.send_to_all({"action": "update_pos", "pos": markerpos})


pygame.init()
screen = pygame.display.set_mode([640, 480])
running = True
marker = pygame.Surface([50, 50])
markerpos = [0,0]

p = CustomServer("", 8000)
#p.load()

tick = LoopingCall(update)
tick.start(0)

p.load()
reactor.run()
