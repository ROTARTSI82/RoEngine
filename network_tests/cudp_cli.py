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

cli = EnqueUDPClient('127.0.0.1', 3000)


def tick():
    cli.enque({"action": "ping"})
    cli.empty_que()


ticker = LoopingCall(tick)
ticker.start(0.1)
cli.load()
reactor.run()
