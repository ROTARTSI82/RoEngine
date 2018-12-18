# -*- coding: UTF-8 -*-

"""
Warning: `roengine.net.udp` is depreciated; it is replaced by `roengine.net.cUDP`
"""

from __future__ import print_function

import rencode
import warnings
import logging

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

__all__ = ['GenericUDPServer', 'GenericUDPClient', 'reactor']

load = rencode.loads
dump = rencode.dumps

ServLog = logging.getLogger('udp.server')
CliLog = logging.getLogger('udp.client')

warnings.warn("roengine.net.udp is depreciated. Use roengine.net.cUDP", DeprecationWarning)


class GenericUDPServer(DatagramProtocol):
    """
    Inherits from [twisted.internet.protocol.DatagramProtocol]
    """

    def __init__(self, host, port):
        """
        Define [self.host] and [self.port] for [self.load]

        :param host: str (IPv4 host)
        :param port: int (between 0 and 65535)
        """
        self.clients = []
        self.arrivals_confirmed = {}
        self.host, self.port = host, port

    def load(self):
        """
        Calls [reactor.listenUDP] according to [self.host] and [self.port]

        :return:
        """
        ServLog.info("Loading UDPServer%s", (self.host, self.port))
        reactor.listenUDP(self.port, self, interface=self.host)

    def datagramReceived(self, message, address):
        """
        Calls [self.network_*message['action']*(message, address)]

        Users shouldn't call or override this method.

        :param message: "{'action': '...', ...}"
        :param address: (host, port)
        :rtype: None
        """
        try:
            message = load(message)
        except Exception as e:
            print ("cannot load:", message, e)

        try:
            if hasattr(self, "network_" + message["action"]):
                getattr(self, "network_" + message["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)

    def send_to_all(self, message):
        """
        Sends [message] to all of [self.clients]

        :param message: {"action": "...", ...}
        :rtype: None
        """
        [self.send(message, addr) for addr in self.clients]

    def verify_send_to_all(self, message):
        """
        Verify sends [message] to all of [self.clients]

        See [self.verify_send]

        :param message: {"action": "...", ...}
        :rtype: None
        """
        [self.verify_send(message, addr) for addr in self.clients]

    def send(self, message, addr):
        """
        Send [message] to [addr]

        :param message: {"action": "...", ...}
        :param addr: (host, port)
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message), addr)
        else:
            print("err:", "transport == None")

    def network_connect_notify(self, message, address):
        """
        Append [address] to [self.clients]

        Called by [self.datagramReceived]. Users shouldn't call this.

        :param message: {"action": "connect_notify", ...}
        :param address: (host, port)
        :rtype: None
        """
        if address not in self.clients:
            self.clients.append(address)
            print ("New client:", address)

    def network_verify_send(self, message, address):
        """
        When a [verify_send] action is received, send a [confirm_arrival] action back to [address]

        Called by [self.datagramReceived]. Users shouldn't call this.

        :param message: {"action": "verify_send", "data": ..., ...}
        :param address: (host, port)
        :rtype: None
        """
        message['action'] = 'confirm_arrival'
        self.send(message, address)
        self.datagramReceived(message['data'], address)

    def confirm_arrivals(self, message, address, retry):
        """
        Called every [retry] second(s) to see if the client responded

        Users shouldn't call this method.

        :param message: {"action": "...", ...}
        :param address: (host, port)
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        if not self.arrivals_confirmed[message['id']]:
            print (message, "failed. Retrying...")
            self.send(message, address)
            reactor.callLater(retry, self.confirm_arrivals, message, address, retry)
        else:
            print (message, "was confirmed.")

    def verify_send(self, message, address, retry=1):
        """
        Send [message] and keep resending every [retry] second(s) until the client responds

        :param message: {"action": "...", ...}
        :param address: (host, port)
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.send(message, address)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, address, retry)

    def network_confirm_arrival(self, message, address):
        """
        Confirms that the client got our datagram

        Called by [self.datagramReceived]. Users should not call this.

        :param message: {"action": "confirm_arrival", "id": ...}
        :param address: Not used. Can be anything
        :rtype: None
        """
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)


class GenericUDPClient(DatagramProtocol):
    """
    Inherits from [twisted.internet.protocol.DatagramProtocol]
    """

    def __init__(self, host, port):
        """
        Defines [self.host], [self.port] for use in [self.load]

        :param host: str (IPv4 host)
        :param port: int (between 0 and 65535)
        """
        self.host, self.port = host, port
        self.connection_success = False
        self.arrivals_confirmed = {}

    def load(self):
        """
        Calls [reactor.listenUDP] on port [0] and [self.host]

        :rtype: None
        """
        reactor.listenUDP(0, self, interface=self.host)

    def startProtocol(self):
        """
        Sends [{"action": "connect_notify"}] and connects transport.

        Users shouldn't call this method. If you override this method, append you code to this code.

        :rtype: None
        """
        self.transport.connect(self.host, self.port)
        self.verify_send({"action": "connect_notify"})

    def datagramReceived(self, message, address):
        """
        Calls [self.network_*message['action']*(message, host)]

        Users shouldn't override or call this method

        :param message: {"action": "...", ...}
        :param address: (host, port)
        :rtype: None
        """
        try:
            message = load(message)
        except Exception as e:
            print("cannot load:", message, e)

        try:
            if hasattr(self, "network_" + message["action"]):
                getattr(self, "network_" + message["action"])(message, address)
        except Exception as e:
            print("err:", message, e)

    def send(self, message):
        """
        Sends [message] to the server

        :param message: {"action": "...", ...}
        :rtype: None
        """
        if self.transport is not None:
            self.transport.write(dump(message))
        else:
            print ("err:", "transport == None")

    def confirm_arrivals(self, message, retry):
        """
        Called every [retry] seconds to see if the server responded

        Users shouldn't call or override this method.

        :param message: {"action": "...", "id": ...}
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        if not self.arrivals_confirmed[message['id']]:
            print (message, "failed. Retrying...")
            self.send(message)
            reactor.callLater(retry, self.confirm_arrivals, message, retry)
        else:
            print (message, "was confirmed.")

    def verify_send(self, message, retry=1):
        """
        Keep resending [message] every [retry] seconds until the server responds

        :param message: {"action": "...", ...}
        :param retry: int (cannot be <= 0)
        :rtype: None
        """
        keys = sorted(self.arrivals_confirmed.keys())
        pid = keys[len(keys)-1] if keys else 0
        message = {"action": "verify_send", "id": pid, "data": message}
        self.send(message)
        self.arrivals_confirmed[pid] = False
        reactor.callLater(retry, self.confirm_arrivals, message, retry)

    def network_confirm_arrival(self, message, address):
        """
        Confirms that the server got our datagram.

        Called by [self.datagramReceived]. Users shouldn't call this method.

        :param message: {"action": "confirm_arrival", "id": ..., ...}
        :param address: (host, port)  # NOTE: Address is unused
        :rtype: None
        """
        self.arrivals_confirmed[message['id']] = True
        try:
            if hasattr(self, "verified_" + message["data"]["action"]):
                getattr(self, "verified_" + message["data"]["action"])(message, address)
        except Exception as e:
            print ("err:", message, e)

    def network_verify_send(self, message, address):
        """
        When a [verify_send] action is received, send a [confirm_arrival] action back to [address]

        Called by [self.datagramReceived]. Users shouldn't call this.

        :param message: {"action": "verify_send", "data": "...", ..}
        :param address: (host, port)
        :rtype: None
        """
        message['action'] = 'confirm_arrival'
        self.send(message)
        self.datagramReceived(message['data'], address)
