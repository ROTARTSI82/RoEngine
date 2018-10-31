from genericClasses.clinet_classes import GenericTCPClient, GenericClientFactory, reactor
from twisted.internet.task import LoopingCall

f = GenericClientFactory("127.0.0.1", 8000)


def update():
    f.send({"action": "ping"})


f.load()

lc = LoopingCall(update)
lc.start(1)

reactor.run()
