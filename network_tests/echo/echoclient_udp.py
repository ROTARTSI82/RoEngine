#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

#from __future__ import print_function

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

port = 3000
host = '127.0.0.1'

class EchoClientDatagramProtocol(DatagramProtocol):
    strings = [
        b"Hello, world!",
        b"What a fine day it is.",
        b"Bye-bye!"
    ]
    
    def startProtocol(self):
        self.transport.connect(host, port)
        self.connection_received = False
    
    def sendDatagram(self):
        #if len(self.strings):
        #    datagram = self.strings.pop(0)
        #    self.transport.write(datagram)
        #else:
        #    reactor.stop()
        #self.transport.write(input(">"))
        pass

    def send_connect(self):
        print "trying to connect..."
        if not self.connection_received:
            self.transport.write(b'connected', (host, port))
            reactor.callLater(1, self.send_connect)
            print "failed. retrying in 1 sec"
        else:
            print "success!"

    def datagramReceived(self, datagram, address):
        global markerpos
        if datagram == b'got_connect':
            print "Success! Connected!"
            self.connection_received = True
            return
        try:
            markerpos = eval(datagram)
        except:
            pass
        #print "pos: ", markerpos
        #self.transport.write(b'dummy', address)

def main():
    protocol = EchoClientDatagramProtocol()
    t = reactor.connectUDP(host, port, protocol)
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
        #if event.type == pygame.MOUSEMOTION:
        #markerpos = event.pos

protocol = EchoClientDatagramProtocol()
reactor.listenUDP(0, protocol)

reactor.callLater(1, protocol.send_connect)

tick = LoopingCall(update)
tick.start(1 / 60.0)

reactor.run()

pygame.quit()