# -*- coding: UTF-8 -*-

from __future__ import print_function

import rencode

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ServerFactory, ClientFactory, connectionDone
import logging

__all__ = ['GenericServerFactory', 'GenericTCPServer', 'GenericTCPClient', 'GenericClientFactory', 'reactor']

load = rencode.loads
dump = rencode.dumps

CProtLog = logging.getLogger('tcp.CliProt')
SProtLog = logging.getLogger('tcp.ServProt')
CFacLog = logging.getLogger('tcp.CliFac')
SFacLog = logging.getLogger('tcp.ServFac')


class GenericTCPServer(Protocol):
    """
    Inherits from [twisted.internet.protocol.Protocol]

    Use in conjunction with [GenericServerFactory]
    """

    address = None

    def __init__(self):
        self.send_que = []

    def dataReceived(self, data):
        """
        Calls [self.network_*data['action]*(data)]

        Users should not override or call this method.

        :param data: "{'action': '...', ...}"
        :rtype: None
        """
        # print ("[CLIENT]", repr(data))
        try:
            data = load(data)
            for packet in data:
                try:
                    if hasattr(self, "network_" + packet["action"]):
                        getattr(self, "network_" + packet["action"])(packet)
                    else:
                        SProtLog.critical("%s Got packet with no handler: %s", self.address, packet)
                except:
                    SProtLog.exception("%s network_%s(%s) failed:", self.address,
                                       "?" if 'action' not in packet else packet['action'], packet)
        except Exception as e:
            SProtLog.exception("%s Invalid packet: %s", self.address, data)

    def _send(self, message):
        """
        Send [message] to a single client.

        :param message: {"action": "...", ...}
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message))
        else:
            self.send_que.append(message)
            SProtLog.critical("%s _send(%s) failed due to null transport.", self.address, message)
            SProtLog.critical("%s Re-appending message to send_que", self.address)

    def enque(self, data):
        self.send_que.append(data)

    def empty_que(self):
        if self.send_que:
            self._send(self.send_que)
            self.send_que = []

    def connectionMade(self):
        self.empty_que()

    def connectionLost(self, reason=connectionDone):
        """
        Print the [reason] why the connection was lost

        :type reason: Failure
        :rtype: None
        """
        SProtLog.critical("%s Connection Lost: %s", self.address, reason)
        reason.printDetailedTraceback()

    def shutdown(self):
        SProtLog.info("%s Shutting down...", self.address)
        self.transport.loseConnection()


class GenericServerFactory(ServerFactory):
    """
    Inherits from [twisted.internet.protocol.ServerFactory]

    Use in conjunction with [GenericTCPServer]
    """

    protocol = GenericTCPServer

    def __init__(self, host, port, max_clients=1):
        """
        Define host and port for later use in [self.load]

        :param host: str (IPv4 host)
        :param port: int (between 0 and 65535)
        :param max_clients: int (How many clients can be connected. Clients kicked if server is full)
        """
        self.max_clients = max_clients
        self.host, self.port = host, port
        self.address = host, port
        self.react_port = None
        self.clients = []

    def buildProtocol(self, addr):
        """
        Append a new client to [self.clients] when a new client connects

        Users shouldn't call this method. If overriden, append your code to this code

        :param addr: IPv4Address(type='TCP', host='...', port=...)
        :rtype: GenericTCPServer
        """
        SFacLog.info("%s New Client%s", self.address, addr)
        np = ServerFactory.buildProtocol(self, addr)
        np.address = addr
        if len(self.clients) < self.max_clients:
            self.clients.append(np)
        else:
            SFacLog.info("%s Game full. Kicking Client%s", self.address, addr)
            np.enque({"action": "kick", "reason": "Game already full"})
        return np

    def _send(self, message, transport):
        """
        Write [message] to [transport]

        :param message: {"action": "...", ...}
        :param transport: transport (can't be None)
        :rtype: None
        """
        if transport is not None:
            transport.write(dump(message))
        else:
            SFacLog.critical("%s _send failed due to null transport being provided.", self.address)

    def empty_all(self):
        [protocol.empty_que() for protocol in self.clients]

    def enque_all(self, data):
        [protocol.enque(data) for protocol in self.clients]

    def load(self):
        """
        Calls [reactor.listenTCP] according to [self.host] and [self.port]

        :rtype: None
        """
        self.react_port = reactor.listenTCP(self.port, self, interface=self.host)
        SFacLog.info("Loading ServerFactory%s", self.address)

    def shutdown(self):
        SFacLog.info("%s Shutting down...", self.address)
        [protocol.shutdown() for protocol in self.clients]
        self.react_port.stopListening()


class GenericTCPClient(Protocol):
    """
    Inherits from [twisted.internet.protocol.Protocol]

    Use in conjunction with [GenericClientFactory]
    """

    address = None

    def __init__(self):
        self.send_que = []

    def dataReceived(self, data):
        """
        Call [self.network_*data['action]*(data)]

        Users shouldn't call or override this method

        :param data: {"action": "...", ...}
        :rtype: None
        """
        # print ("[SERVER]", data)
        try:
            data = load(data)
            for packet in data:
                try:
                    if hasattr(self, "network_" + packet["action"]):
                        getattr(self, "network_" + packet["action"])(packet)
                    else:
                        CProtLog.critical("%s Got packet without handler: %s", self.address, packet)
                except:
                    CProtLog.exception("%s network_%s(%s) failed:", self.address,
                                       "?" if 'action' not in packet else packet['action'], packet)
        except Exception as e:
            CProtLog.exception("Invalid Packet: %s", data)

    def enque(self, data):
        self.send_que.append(data)

    def empty_que(self):
        if self.send_que:
            self._send(self.send_que)
            self.send_que = []

    def _send(self, message):
        """
        Send [message] to the server

        :param message: {"action": "...", ...}
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message))
        else:
            self.send_que.append(message)
            CProtLog.critical("%s _send failed due to null transport!", self.address)
            CProtLog.critical("%s Re-appending message to send_que", self.address)

    def connectionMade(self):
        """
        Empties [self.send_que]

        Users shouldn't call this method. If you override this, append your code to this.

        :rtype: None
        """
        CProtLog.info("%s Connection made! Emptying send que.", self.address)
        self.empty_que()

    def connectionLost(self, reason=connectionDone):
        """
        Print that we lost our connection

        Users shouldn't call this method.

        :type reason: Failure
        :rtype: None
        """
        CProtLog.critical("%s Connection lost: %s", self.address, reason)
        reason.printDetailedTraceback()

    def network_kick(self, data):
        """
        Shutdown if we are kicked

        :param data: {"action": "kick", "reason": "...", ...}
        :rtype: None
        """
        CProtLog.info("%s Was kicked: '%s'", self.address,
                      data['reason'] if 'reason' in data else '?')
        self.factory.shutdown()

    def shutdown(self):
        """
        Shutdown. Calls [self.transport.loseConnection]

        :return: None
        """
        CProtLog.info("%s Shutting down...", self.address)
        self.transport.loseConnection()

    # For testing. Basically useless
    def network_ping(self, message):
        print ("PING")

    def network_ping2(self, message):
        print ("P2")


class GenericClientFactory(ClientFactory):
    """
    Inherits from [twisted.internet.protocol.ClientFactory]

    Use in conjunction with [GenericTCPClient]
    """

    protocol = GenericTCPClient

    def __init__(self, host, port):
        """
        Define [self.host] and [self.port]

        :param host: str (IPv4 host)
        :param port: int (between 0 and 65535)
        """
        self.host, self.port = host, port
        self.address = host, port
        self.connector, self.protocol_instance = None, None

    def buildProtocol(self, addr):
        """
        Create a new [protocol] instance and append it to [self.clients]

        Users shouldn't call this method. If you override this, append your code to this.

        :param addr: IPv4Address(type='TCP', host=..., port=...)
        :rtype: GenericTCPClient
        """
        CFacLog.info("%s Connected! %s", self.address, addr)
        self.protocol_instance = ClientFactory.buildProtocol(self, addr)
        self.protocol_instance.address = addr
        return self.protocol_instance

    def _send(self, message, retry=1):
        """
        Send [message] to server. If [self.protocol_instance] is [None], retry in [retry] seconds.

        :param message: {"action": "...", ...}
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        if self.protocol_instance is not None:
            self.protocol_instance._send(message)
        else:
            reactor.callLater(retry, self._send, message, retry)
            CFacLog.critical("%s _send failed due to null protocol_instance.", self.address)

    def empty_all(self, retry=1):
        if self.protocol_instance is not None:
            self.protocol_instance.empty_que()
        else:
            reactor.callLater(retry, self.empty_all, retry)
            CFacLog.critical("%s emtpy_all() failed due to null protocol_instance.", self.address)

    def enque_all(self, data, retry=1):
        if self.protocol_instance is not None:
            self.protocol_instance.enque(data)
        else:
            reactor.callLater(retry, self.empty_all, data, retry)
            CFacLog.critical("%s enque_all() failed due to null protocol_instance.", self.address)

    def load(self):
        """
        Calls [reactor.connectTCP] according to [self.host] and [self.port]

        :rtype: None
        """
        CFacLog.info("Loading ClientFactory%s", self.address)
        self.connector = reactor.connectTCP(self.host, self.port, self)

    def clientConnectionFailed(self, connector, reason):
        """
        Print that the connection failed.

        Users shouldn't call this method.

        :param connector: transport
        :type reason: Failure
        :rtype: None
        """
        CFacLog.critical("%s Cannot connect to `%s`: %s", self.address, connector, reason)

    def clientConnectionLost(self, connector, reason):
        """
        Print that the connection was lost. If [reason] is [connectionDone], do not treat it as an exception.

        Users shouldn't call this method.

        :param connector:
        :param reason:
        :return:
        """
        CFacLog.critical("%s Connection to `%s` lost: %s", self.address, connector, reason)
        reason.printDetailedTraceback()

    def shutdown(self):
        CFacLog.info("%s Shutting down...", self.address,)
        self.protocol_instance.shutdown()
        self.connector.disconnect()
