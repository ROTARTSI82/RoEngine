# -*- coding: UTF-8 -*-

from __future__ import print_function

import rencode
import logging
import socket

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


__all__ = ['ServerUDP', 'EnqueUDPClient', 'UDPServerFactory', 'adopt_udp_port']

load = rencode.loads
dump = rencode.dumps

cUDPServerLogger = logging.getLogger('cUDP.ServFac')
cUDPClientLogger = logging.getLogger('cUDP.CliFac')
cUDPServProtLogger = logging.getLogger('cUDP.ServProt')

LOG_NO_HANDLERS = False
LOG_SENDS = False
LOG_GETS = False


def cUDP_settings(lsends=False, lgets=False, lnhdlrs=False):
    global LOG_GETS, LOG_SENDS, LOG_NO_HANDLERS
    LOG_SENDS, LOG_GETS, LOG_NO_HANDLERS = lsends, lgets, lnhdlrs


def adopt_udp_port(cls, addr=('127.0.0.1', 3000), args=(), kwargs={}):
    """
    From https://twistedmatrix.com/documents/15.1.0/core/howto/udp.html

    :param cls:
    :param addr:
    :return: None
    """
    portSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Make the port non-blocking and start it listening.
    portSocket.setblocking(False)
    portSocket.bind(addr)

    # Now pass the port file descriptor to the reactor
    port = reactor.adoptDatagramPort(portSocket.fileno(), socket.AF_INET, cls(*args, **kwargs))

    # The portSocket should be cleaned up by the process that creates it.
    return portSocket, port


class ServerUDP(object):
    factory = None
    address = None

    def __init__(self):
        self.send_que = []

    def enque(self, msg):
        self.send_que.append(msg)

    def network_ping(self, msg):
        print ("PING from UDPServerProtocol")

    def empty_que(self):
        try:
            if self.send_que and self.factory is not None:
                self.factory.transport.write(dump(self.send_que), self.address)
                if LOG_SENDS:
                    cUDPServProtLogger.debug("%s SEND %s --> %s", self.address, self.send_que, self.address)
                self.send_que = []
        except:
            cUDPServProtLogger.exception("%s empty_que() failed.", self.address)


class UDPServerFactory(DatagramProtocol):
    protocol = ServerUDP

    def __init__(self, host, port, maxClients=1):
        self.max_clients = maxClients
        self.clients = []
        self.client_protocols = {}
        self.arrivals_confirmed = {}
        self.host, self.port = host, port
        self.address = host, port

    def _send(self, msg, addr):
        try:
            self.transport.write(dump([msg, ]), addr)
            if LOG_SENDS:
                cUDPServerLogger.debug("%s SEND %s --> %s", self.address, msg, addr)
        except:
            cUDPServerLogger.exception("%s _send() failed.", self.address)

    def empty_all(self):
        for cp in self.client_protocols.values():
            cp.empty_que()

    def load(self):
        reactor.listenUDP(self.port, self, interface=self.host)
        cUDPServerLogger.info("Loading UDPServerFactory%s", self.address)

    def datagramReceived(self, message, address):
        if address not in self.clients:
            cUDPServerLogger.critical("%s Got packet from unknown Client%s.", self.address, address)
            cUDPServerLogger.critical("%s Attempting to build...", self.address)
            self.build_protocol(address)
        try:
            message = load(message)
            for packet in message:
                try:
                    if hasattr(self.client_protocols[address], "network_" + packet["action"]):
                        getattr(self.client_protocols[address], "network_" + packet["action"])(packet)
                    elif LOG_NO_HANDLERS:
                        cUDPServerLogger.critical('%s Got packet without handler: %s', self.address, packet)
                except Exception as e:
                    cUDPServerLogger.exception("%s Protocol's network_ failed on: %s", self.address, packet)
                try:
                    if hasattr(self, "network_" + packet["action"]):
                        getattr(self, "network_" + packet["action"])(packet, address)
                    elif LOG_NO_HANDLERS:
                        cUDPServerLogger.critical('%s Got packet without handler: %s', self.address, packet)
                except Exception as e:
                    cUDPServerLogger.exception("%s Self's network_ failed on: %s", self.address, packet)
        except Exception as e:
            cUDPServerLogger.exception("%s Invalid packet from %s: %s", self.address, address, message)
        if LOG_GETS:
            cUDPServerLogger.debug("%s GET %s <-- %s", self.address, message, address)

    def send_to_all(self, message):
        [self.send_to_addr(message, addr) for addr in self.clients]

    def verify_send_to_all(self, message):
        [self.verify_send(message, addr) for addr in self.clients]

    def send_to_addr(self, message, addr):
        if self.transport is not None:
            if addr in self.client_protocols:
                self.client_protocols[addr].enque(message)
            else:
                cUDPServerLogger.critical('%s send_to_addr%s failed. Trying _send()',
                                          self.address, (message, addr))
                self._send(message, addr)
            # self.transport.write(dump(message), addr)
        else:
            cUDPServerLogger.critical('%s send_to_addr%s failed due to null transport. Trying _send()',
                                      self.address, (message, addr))
            self._send(message, addr)

    def network_connect_notify(self, message, address):
        if address not in self.clients:
            cUDPServerLogger.info("%s Got new Client%s", self.address, address)
            self.build_protocol(address)

    def network_ping(self, msg, addr):
        print ("PING! from UDPServerFactory")

    def build_protocol(self, addr):
        if addr not in self.clients:
            np = self.protocol()
            np.factory = self
            np.address = addr
            if len(self.clients) < self.max_clients:
                self.clients.append(addr)
                self.client_protocols[addr] = np
                cUDPServerLogger.info('%s Successfully built Client%s', self.address, addr)
                return True
            else:
                cUDPServerLogger.info('%s Kicking Client%s: Game already full', self.address, addr)
                np.enque({'action': 'kick', 'reason': 'Game already full'})
                np.empty_que()
        else:
            cUDPServerLogger.critical('%s Client%s is already built!', self.address, addr)
        return False

    def network_verify_send(self, message, address):
        message['action'] = 'confirm_arrival'
        self.send_to_addr(message, address)
        cUDPServerLogger.info("%s verify_send%s", self.address, (message, address))
        '''
        if message['id'] in self.handled_ids:
            cUDPServerLogger.critical("%s Got repeat verify_send! Ignoring...", self.address)
            return
        self.handled_ids.append(message['id'])
        '''
        try:
            if hasattr(self.client_protocols[address], "network_" + message['data']["action"]):
                getattr(self.client_protocols[address], "network_" + message['data']["action"])(message['data'])
            elif LOG_NO_HANDLERS:
                cUDPServerLogger.critical('%s Got packet without handler: %s', self.address, message)
        except Exception as e:
            cUDPServerLogger.exception("%s Protocol's network_%s(%s) failed:", self.address,
                                       "?" if 'action' not in message else message['data']['action'], message)
        try:
            if hasattr(self, "network_" + message['data']["action"]):
                getattr(self, "network_" + message['data']["action"])(message['data'], address)
            elif LOG_NO_HANDLERS:
                cUDPServerLogger.critical('%s Got packet without handler: %s', self.address, message)
        except Exception as e:
            cUDPServerLogger.exception("%s Self's network_%s(%s) failed:", self.address,
                                       "?" if 'action' not in message else message['data']['action'], message)

    def confirm_arrivals(self, message, address, retry):
        if not self.arrivals_confirmed[message['id']]:
            cUDPServerLogger.critical("%s Cannot confirm packet: %s Retrying in %s", self.address, message, retry)
            self.send_to_addr(message, address)
            reactor.callLater(retry, self.confirm_arrivals, message, address, retry)
        else:
            cUDPServerLogger.info("%s Packet was confirmed: %s", self.address, message)

    def verify_send(self, message, address, retry=1):
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.send_to_addr(message, address)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, address, retry)

    def network_confirm_arrival(self, message, address):
        if self.arrivals_confirmed[message['id']]:
            cUDPServerLogger.critical("%s Got repeat confirm_arrival! Ignoring...", self.address)
            return
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message['data'], address)
            elif LOG_NO_HANDLERS:
                cUDPServerLogger.critical('%s Got packet without verified_ handler: %s', self.address, message)
        except Exception as e:
            cUDPServerLogger.exception("%s Self's verified_ failed on: ", self.address, message)

        try:
            if hasattr(self.client_protocols[address], "verified_" + message["data"]["action"]):
                getattr(self.client_protocols[address],
                        "verified_" + message["data"]["action"])(message['data'], address)
            elif LOG_NO_HANDLERS:
                cUDPServerLogger.critical('%s Got packet without verified_ handler: %s', self.address, message)
        except Exception as e:
            cUDPServerLogger.exception("%s Protocol's verified_ failed on: %s", self.address, message)


class EnqueUDPClient(DatagramProtocol):
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.address = host, port
        self.connection_success = False
        self.send_que = []
        self.handled_ids = []
        self.arrivals_confirmed = {}

    def load(self):
        reactor.listenUDP(0, self, interface=self.host)
        cUDPClientLogger.info("Loading EnqueUDPClient%s", self.address)

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
                    elif LOG_NO_HANDLERS:
                        cUDPClientLogger.critical('%s Got packet without handler: %s', self.address, message)
                except Exception as e:
                    cUDPClientLogger.exception("%s network_ failed on: %s", self.address, message)
        except Exception as e:
            cUDPClientLogger.exception("%s Invalid packet from %s: %s", self.address, address, message)
        if LOG_GETS:
            cUDPClientLogger.debug("%s GET %s <-- %s", self.address, message, address)

    def enque(self, message):
        self.send_que.append(message)

    def network_ping(self, msg, addr):
        print ("PING! from Client")

    def empty_que(self):
        try:
            if self.send_que:
                self.transport.write(dump(self.send_que))
                if LOG_SENDS:
                    cUDPClientLogger.debug("%s SEND %s --> %s", self.address, self.send_que, self.address)
                self.send_que = []
        except:
            cUDPClientLogger.exception("%s empty_que() failed.", self.address)
            # reactor.callLater(retry, self.empty_que, retry)

    def _send(self, message):
        if self.transport is not None:
            self.transport.write(dump([message, ]))
            if LOG_SENDS:
                cUDPClientLogger.debug("%s SEND %s --> %s", self.address, message, self.address)
        else:
            cUDPClientLogger.critical("%s _send() failed due to null transport", self.address)

    def confirm_arrivals(self, message, retry=1):
        if not self.arrivals_confirmed[message['id']]:
            cUDPClientLogger.critical("%s Cannot confirm packet: %s Retrying in %s", self.address, message, retry)
            self.enque(message)
            reactor.callLater(retry, self.confirm_arrivals, message, retry)
        else:
            cUDPClientLogger.info("%s Packet was confirmed: %s", self.address, message)

    def verify_send(self, message, retry=1):
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.enque(message)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, retry)

    def network_kick(self, message, address):
        cUDPClientLogger.info("%s Was kicked: '%s'.", self.address,
                              message['reason'] if 'reason' in message else '?')
        reactor.stop()

    def network_confirm_arrival(self, message, address):
        if self.arrivals_confirmed[message['id']]:
            cUDPClientLogger.critical("%s Got repeat confirm_arrival! Ignoring...", self.address)
            return
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message['data'], address)
            elif LOG_NO_HANDLERS:
                cUDPClientLogger.critical('%s Got packet without handler: %s', self.address, message)
        except Exception as e:
            cUDPClientLogger.exception("%s verify_ failed on: %s", self.address, message)

    def network_verify_send(self, message, address):
        message['action'] = 'confirm_arrival'
        self.enque(message)
        '''
        if message['id'] in self.handled_ids:
            cUDPClientLogger.critical("%s Got repeat verify_send! Ignoring...", self.address)
            return
        self.handled_ids.append(message['id'])
        '''
        try:
            if hasattr(self, "network_" + message['data']["action"]):
                getattr(self, "network_" + message['data']["action"])(message['data'], address)
            elif LOG_NO_HANDLERS:
                cUDPClientLogger.critical('%s Got packet without handler: %s', self.address, message)
        except Exception as e:
            cUDPClientLogger.exception("%s network_ failed on: %s", self.address, message)
