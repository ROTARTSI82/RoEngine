from roengine import GenericTCPClient, GenericClientFactory, reactor
from twisted.internet.task import LoopingCall

f = GenericClientFactory("127.0.0.1", 8000)


f.load()

reactor.run()
