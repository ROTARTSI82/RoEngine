# -*- coding: UTF-8 -*-

from __future__ import print_function

import rencode

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

load = rencode.loads
dump = rencode.dumps


class ServerUDP(object):
    factory = None
    address = None
    def __init__(self):
        self.send_que = []

    def enque(self, msg):
        self.send_que.append(msg)

    def network_ping(self, msg):
        print ('got ping! from prot')

    def tick(self, retry=1):
        try:
            if self.send_que and self.factory is not None:
                self.factory.transport.write(dump(self.send_que), self.address)
                self.send_que = []
        except:
            print ("failed. retrying...")
            reactor.callLater(retry, self.tick, retry)


class UDPServerFactory(DatagramProtocol):
    protocol = ServerUDP
    def __init__(self, host, port, maxClients=1):
        self.max_clients = maxClients
        self.clients = []
        self.client_protocols = {}
        self.arrivals_confirmed = {}
        self.host, self.port = host, port

    def _send(self, msg, addr):
        try:
            self.transport.write(dump([msg, ]), addr)
        except:
            print ('_send failed.')

    def tick(self):
        for cp in self.client_protocols.values():
            cp.tick()

    def load(self):
        reactor.listenUDP(self.port, self, interface=self.host)

    def datagramReceived(self, message, address):
        if address not in self.client_protocols:
            self.build_protocol(address)
        try:
            message = load(message)
            for packet in message:
                try:
                    if hasattr(self.client_protocols[address], "network_" + packet["action"]):
                        getattr(self.client_protocols[address], "network_" + packet["action"])(packet)
                except Exception as e:
                    print("err:", message, e)
                try:
                    if hasattr(self, "network_" + packet["action"]):
                        getattr(self, "network_" + packet["action"])(packet, address)
                except Exception as e:
                    print("err:", message, e)
        except Exception as e:
            print ("cannot load:", message, e)

    def send_to_all(self, message):
        [self.send_to_addr(message, addr) for addr in self.clients]

    def verify_send_to_all(self, message):
        [self.verify_send(message, addr) for addr in self.clients]

    def send_to_addr(self, message, addr):
        if self.transport is not None:
            if addr in self.client_protocols:
                self.client_protocols[addr].enque(message)
            else:
                print ('not connected')
                self._send(message, addr)
            #self.transport.write(dump(message), addr)
        else:
            print("err:", "transport == None")
            self._send(message, addr)

    def network_connect_notify(self, message, address):
        print ('heya')
        if address not in self.clients:
            self.build_protocol(address)
            print ("New client:", address)

    def network_ping(self, msg, addr):
        print ('got ping! from fac')

    def build_protocol(self, addr):
        if addr not in self.clients:
            np = self.protocol()
            np.factory = self
            np.address = addr
            if len(self.clients) < self.max_clients:
                self.clients.append(addr)
                self.client_protocols[addr] = np
            else:
                print ('Kicking %s; game full' % str(addr))
                np.enque({'action': 'kick', 'reason': 'Game already full'})
                np.tick()

    def network_verify_send(self, message, address):
        message['action'] = 'confirm_arrival'
        self.send_to_addr(message, address)
        print ("verify:", message, address)
        try:
            if hasattr(self.client_protocols[address], "network_" + message['data']["action"]):
                getattr(self.client_protocols[address], "network_" + message['data']["action"])(message)
        except Exception as e:
            print("err:", message, e)
        try:
            if hasattr(self, "network_" + message['data']["action"]):
                getattr(self, "network_" + message['data']["action"])(message, address)
        except Exception as e:
            print("err:", message, e)

    def confirm_arrivals(self, message, address, retry):
        if not self.arrivals_confirmed[message['id']]:
            print (message, "failed. Retrying...")
            self.send_to_addr(message, address)
            reactor.callLater(retry, self.confirm_arrivals, message, address, retry)
        else:
            print (message, "was confirmed.")

    def verify_send(self, message, address, retry=1):
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.send_to_addr(message, address)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, address, retry)

    def network_confirm_arrival(self, message, address):
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)

        try:
            if hasattr(self.client_protocols[address], "verified_" + message["data"]["action"]):
                getattr(self.client_protocols[address], "verified_" + message["data"]["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)


class EnqueUDPClient(DatagramProtocol):
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.connection_success = False
        self.server_instance = None
        self.send_que = []
        self.arrivals_confirmed = {}

    def load(self):
        reactor.listenUDP(0, self, interface=self.host)

    def startProtocol(self):
        self.transport.connect(self.host, self.port)
        self.verify_send({"action": "connect_notify"})

    def datagramReceived(self, message, address):
        try:
            message = load(message)
            for packet in message:
                try:
                    if hasattr(self, "network_" + packet["action"]):
                        getattr(self, "network_" + packet["action"])(packet, address)
                except Exception as e:
                    print("err:", packet, e)
        except Exception as e:
            print ("cannot load:", message, e)

    def enque(self, message):
        self.send_que.append(message)

    def network_ping(self, msg, addr):
        print ('got ping! from cli')

    def tick(self, retry=1):
        try:
            if self.send_que:
                self.transport.write(dump(self.send_que))
                self.send_que = []
        except:
            print ('failed. retrying...')
            reactor.callLater(retry, self.tick, retry)

    def _send(self, message):
        if self.transport is not None:
            self.transport.write(dump([message,]))
        else:
            print ("err:", "transport == None")

    def confirm_arrivals(self, message, retry=1):
        if not self.arrivals_confirmed[message['id']]:
            print (message, "failed. Retrying...")
            self.enque(message)
            reactor.callLater(retry, self.confirm_arrivals, message, retry)
        else:
            print (message, "was confirmed.")

    def verify_send(self, message, retry=1):
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.enque(message)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, retry)

    def network_kick(self, message, address):
        print ('was kicked: %s' % message['reason'])
        reactor.stop()

    def network_confirm_arrival(self, message, address):
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)

    def network_verify_send(self, message, address):
        message['action'] = 'confirm_arrival'
        self.enque(message)
        self.datagramReceived([message['data'],], address)
