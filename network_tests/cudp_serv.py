import logging
import sys

from twisted.internet.task import LoopingCall

from roengine.net.cUDP import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
hdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s|%(name)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                              '%H:%M:%S')
hdlr.setFormatter(formatter)
root.addHandler(hdlr)

serv = UDPServerFactory('127.0.0.1', 3000)


def tick():
    serv.send_to_all({"action": "ping"})
    serv.empty_all()


ticker = LoopingCall(tick)
ticker.start(0.1)
serv.load()
reactor.run()
