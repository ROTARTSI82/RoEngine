# -*- coding: UTF-8 -*-

import time
import logging
logger = logging.getLogger("recording")

from roengine.net.rencode import dumps, loads
RANGE = 1 / 6.0


class GameRecorder(object):
    def __init__(self):
        self.content = {"start": -1, "end": -1, "len": -1, "gets": {}, "map": "uninitiated", "version": "uninitiated"}

    def start(self):
        self.content['start'] = time.time()

    def stop(self):
        self.content['end'] = time.time()
        self.content['len'] = self.content['end'] - self.content['start']

    def record_gets(self, packets, addr=None):
        return [self.record_get(i, addr) for i in packets]

    def record_get(self, packet, addr=None):
        assert self.content['start'] != -1, "GameRecorder not started."
        try:
            if hasattr(self, 'got_%s' % packet['action']):
                getattr(self, 'got_%s' % packet['action'])(packet, addr)
            return 0
        except Exception:
            logger.exception("record_get failed (was a invalid packet supplied?)")
            return 1

    def got_settings(self, packet, addr):
        self.content['version'] = packet['ver']
        self.content['map'] = packet['map']

    def got_update(self, packet, addr):
        key = time.time()-self.content['start']
        if not key in self.content['gets']:
            self.content['gets'][key] = []
        self.content['gets'][key].append(packet)

    def save(self, file=None):
        assert self.content['end'] != -1, "GameRecorder not stopped."
        dat = dumps(self.content)
        if file is not None:
            with open(file, "w") as fp:
                fp.write(dat)
        return dat


class RecordingPlayer(object):
    def __init__(self, game):
        self.started_on = -1
        self.speed = 1
        self.game = game
        self.prog = 0
        self.lastUpdate = -1
        self.contents = {}

    def from_file(self, filename):
        with open(filename, "r") as fp:
            self.contents = loads(fp.read())
        return self.contents

    def from_dict(self, x):
        self.contents = x
        return self.contents

    def from_rencode(self, x):
        self.contents = loads(x)
        return self.contents

    def start(self):
        self.started_on = time.time()

    def set_speed(self, speed):
        self.speed = speed

    def update(self):
        assert self.started_on != -1, "RecordingPlayer not started"
        now = time.time()
        if self.lastUpdate == -1:
            self.lastUpdate = now
        self.prog += (now - self.lastUpdate) * self.speed
        self.lastUpdate = now
        canidates = {}
        for i in self.contents['gets'].keys():
            if self.prog-RANGE <= i <= self.prog+RANGE:
                canidates[i] = self.contents['gets'][i]
        if self.speed < 0 and canidates:
            best = sorted(canidates.keys())[0]
            [self.apply_packet(packet, now, best) for packet in canidates[best]]
        elif canidates:
            best = sorted(canidates.keys())[-1]
            [self.apply_packet(packet, now, best) for packet in canidates[best]]

    def apply_packet(self, packet, actual_time, expected_time):
        pass
