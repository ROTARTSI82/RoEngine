from roengine import GenericTCPServer, GenericServerFactory, reactor
from twisted.internet.task import LoopingCall

f = GenericServerFactory("127.0.0.1", 8000)


def update():
    f.enque_all({"action": "ping"})
    f.enque_all({"action": "ping2"})
    f.empty_all()


f.load()

lc = LoopingCall(update)
lc.start(1)

reactor.run()
