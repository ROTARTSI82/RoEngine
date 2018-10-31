from genericClasses.server_classes import GenericTCPServer, GenericServerFactory, reactor
from twisted.internet.task import LoopingCall

f = GenericServerFactory("127.0.0.1", 8000)


def update():
    f.send_to_all({"action": "ping"})


f.load()

lc = LoopingCall(update)
lc.start(1)

reactor.run()
