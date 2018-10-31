#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
addr = []

host = '127.0.0.1'
port = 3000

# Here's a UDP version of the simplest possible protocol
class EchoUDP(DatagramProtocol):
    def startProtocol(self):
        #self.transport.connect(host, port)
        pass
    def datagramReceived(self, datagram, address):
        global addr
        if not address in addr:
            addr.append(address)
            print "New client:", address
        self.transport.write(b'got_connect', address)
        #print addr
        #self.transport.write(datagram, address)
        #print (datagram)
        #self.transport.write(str(markerpos), address)
        #addr = address

def main():
    reactor.listenUDP(port, EchoUDP())
    reactor.run()

import pygame

pygame.init()
screen = pygame.display.set_mode([640, 480])
running = True
marker = pygame.Surface([50, 50])
markerpos = [0,0]
def update():
    global markerpos
    screen.fill([255, 255, 255])
    screen.blit(marker, markerpos)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            reactor.stop()
        if event.type == pygame.MOUSEMOTION:
            markerpos = event.pos
            for address in addr:
                protocol.transport.write(str(markerpos), address)


protocol = EchoUDP()
reactor.listenUDP(port, protocol)

tick = LoopingCall(update)
tick.start(1 / 60.0)

reactor.run()

pygame.quit()