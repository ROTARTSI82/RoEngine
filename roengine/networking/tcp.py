# -*- coding: UTF-8 -*-

from __future__ import print_function

import marshal
#from networking import rencode

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ServerFactory, ClientFactory, connectionDone

__all__ = ['GenericServerFactory', 'GenericTCPServer', 'GenericTCPClient', 'GenericClientFactory', 'reactor']

load = marshal.loads
dump = marshal.dumps


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
        try:
            data = load(data)
            if hasattr(self, "network_" + data["action"]):
                eval("self.network_" + data["action"])(data)
        except Exception as e:
            print ("err:", data, e)

    def send(self, message):
        """
        Send [message] to a single client.

        :param message: {"action": "...", ...}
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message))
        else:
            self.send_que.append(message)
            print ("err:", "transport == None")

    def connectionMade(self):
        print ("emptying send que")
        prev_send_que = self.send_que[:]
        self.send_que = []
        [self.send(message) for message in prev_send_que]

    def send_to_all(self, message):
        """
        Send [message] to all clients in [self.factory.clients]

        NOTE: Do not use this. Use [GenericServerFactory.send_to_all] instead

        :param message: {"action": "...", ...}
        :rtype: None
        """
        [protocol.send(message) for protocol in self.factory.clients]

    def connectionLost(self, reason=connectionDone):
        """
        Print the [reason] why the connection was lost

        :type reason: Failure
        :rtype: None
        """
        print ("conn lost:", reason)
        reason.printDetailedTraceback()

    def shutdown(self):
        print ("shutdown called")
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
        self.react_port = None
        self.clients = []

    def buildProtocol(self, addr):
        """
        Append a new client to [self.clients] when a new client connects

        Users shouldn't call this method. If overriden, append your code to this code

        :param addr: IPv4Address(type='TCP', host='...', port=...)
        :rtype: GenericTCPServer
        """
        print ("New client:", addr)
        np = ServerFactory.buildProtocol(self, addr)
        np.address = addr
        if len(self.clients) < self.max_clients:
            self.clients.append(np)
        else:
            print ("Game full. Kicking", addr)
            np.send({"action": "kick", "reason": "Game already full"})
        return np

    def send(self, message, transport):
        """
        Write [message] to [transport]

        :param message: {"action": "...", ...}
        :param transport: transport (can't be None)
        :rtype: None
        """
        if transport is not None:
            transport.write(dump(message))
        else:
            print ("err:", "transport == None")

    def send_to_all(self, message):
        """
        Send message to all clients in [self.clients]

        :param message: {"action": "...", ...}
        :rtype: None
        """
        [protocol.send(message) for protocol in self.clients]

    def load(self):
        """
        Calls [reactor.listenTCP] according to [self.host] and [self.port]

        :rtype: None
        """
        self.react_port = reactor.listenTCP(self.port, self, interface=self.host)

    def shutdown(self):
        print ("shutdown called")
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
        try:
            data = load(data)
            if hasattr(self, "network_" + data["action"]):
                eval("self.network_" + data["action"])(data)
        except Exception as e:
            print ("err:", data, e)

    def send(self, message):
        """
        Send [message] to the server

        :param message: {"action": "...", ...}
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message))
        else:
            self.send_que.append(message)
            print ("err:", "transport == None")

    def connectionMade(self):
        """
        Empties [self.send_que]

        Users shouldn't call this method. If you override this, append your code to this.

        :rtype: None
        """
        print ("Emptying send_que...")
        prev_send_que = self.send_que[:]
        self.send_que = []
        [self.send(message) for message in prev_send_que]

    def connectionLost(self, reason=connectionDone):
        """
        Print that we lost our connection

        Users shouldn't call this method.

        :type reason: Failure
        :rtype: None
        """
        print ("conn lost: ", reason)
        reason.printDetailedTraceback()

    def network_kick(self, data):
        """
        Shutdown if we are kicked

        :param data: {"action": "kick", "reason": "...", ...}
        :rtype: None
        """
        print ("Was kicked:", data['reason'])
        self.factory.shutdown()

    def shutdown(self):
        """
        Shutdown. Calls [self.transport.loseConnection]

        :return: None
        """
        print ("shutdown called")
        self.transport.loseConnection()

    def network_ping(self, message):
        print ("PING")


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
        self.connector, self.protocol_instance = None, None

    def buildProtocol(self, addr):
        """
        Create a new [protocol] instance and append it to [self.clients]

        Users shouldn't call this method. If you override this, append your code to this.

        :param addr: IPv4Address(type='TCP', host=..., port=...)
        :rtype: GenericTCPClient
        """
        print ("Connected:", addr)
        self.protocol_instance = ClientFactory.buildProtocol(self, addr)
        self.protocol_instance.address = addr
        return self.protocol_instance

    def send(self, message, retry=1):
        """
        Send [message] to server. If [self.protocol_instance] is [None], retry in [retry] seconds.

        :param message: {"action": "...", ...}
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        if self.protocol_instance is not None:
            self.protocol_instance.send(message)
        else:
            reactor.callLater(retry, self.send, message)
            print ("err:", "self.protocol_instance == None")

    def load(self):
        """
        Calls [reactor.connectTCP] according to [self.host] and [self.port]

        :rtype: None
        """
        self.connector = reactor.connectTCP(self.host, self.port, self)

    def clientConnectionFailed(self, connector, reason):
        """
        Print that the connection failed.

        Users shouldn't call this method.

        :param connector: transport
        :type reason: Failure
        :rtype: None
        """
        print ("conn failed:", reason)

    def clientConnectionLost(self, connector, reason):
        """
        Print that the connection was lost. If [reason] is [connectionDone], do not treat it as an exception.

        Users shouldn't call this method.

        :param connector:
        :param reason:
        :return:
        """
        print ("conn lost:", reason)
        reason.printDetailedTraceback()

    def shutdown(self):
        print ("shutdown called")
        self.protocol_instance.shutdown()
        self.connector.disconnect()
