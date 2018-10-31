from twisted.internet import reactor
from twisted.internet.task import LoopingCall

inp = raw_input("Type r for reactor and l for LoopingCall >>> ")
if inp == 'r':
    def countdown(countfrom):
        if countfrom <= 0:
            print countfrom
            print "DONE!!!"
            reactor.stop()
        else:
            print countfrom
            reactor.callLater(1, countdown, countfrom-1)
    reactor.callWhenRunning(countdown, input("Count from >>> "))
    reactor.run()
else:
    num_countdowns = input("Number of countdowns >>> ")

    counters = [0 for i in range(num_countdowns)]

    def countdown(countfrom, callobjindex):
        global counters, tick
        #print countfrom, counter
        print countfrom - counters[callobjindex]
        if (countfrom - counters[callobjindex]) <= 0:
            print "DONE!!!"
            counter = 0
            loopingcalls[callobjindex].stop()
            loopingcalls[callobjindex] = None
            if loopingcalls == [None for i in range(num_countdowns)]:
                reactor.stop()
        counters[callobjindex] += 1
        #print "exit"

    loopingcalls = []
    waittimes = [input("Count from >>> ") for i in range(num_countdowns)]
    for i in range(num_countdowns):
        loopingcalls.append(LoopingCall(countdown, waittimes[i], i))
        loopingcalls[i].start(1.0)
    reactor.run()
    #reactor.stop()
