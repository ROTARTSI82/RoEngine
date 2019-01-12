# -*- coding: UTF-8 -*-
import pygame
import numpy
import rand
import wave
import logging
import warnings

from roengine.util import Dummy

BITS = 16
SAMPLE_RATE = 44100
CHANNELS = 2
ZERO_RANGE = 10
AVERAGE = 0.127056277263  # Average after 10 trails with 250ms notes and rests
MAX_SAMPLE = 2 ** (BITS - 1) - 1

logger = logging.getLogger('sound')

NOTES = {
    'REST': 0,
    'A#0': 29.14,
    'A#1': 58.27,
    'A#2': 116.54,
    'A#3': 233.08,
    'A#4': 466.16,
    'A#5': 932.33,
    'A#6': 1864.66,
    'A#7': 3729.3,
    'A#8': 7458.62,
    'A0': 27.5,
    'A1': 55.0,
    'A2': 110.0,
    'A3': 220.0,
    'A4': 440.0,
    'A5': 880.0,
    'A6': 1760.0,
    'A7': 3520.0,
    'A8': 7040.0,
    'Ab0': 25.96,
    'Ab1': 51.91,
    'Ab2': 103.83,
    'Ab3': 207.65,
    'Ab4': 415.3,
    'Ab5': 830.61,
    'Ab6': 1661.22,
    'Ab7': 3322.44,
    'Ab8': 6644.8,
    'B0': 30.87,
    'B1': 61.74,
    'B2': 123.4,
    'B3': 246.94,
    'B4': 493.88,
    'B5': 987.77,
    'B6': 1975.5,
    'B7': 3951.0,
    'B8': 7902.13,
    'Bb0': 29.14,
    'Bb1': 58.27,
    'Bb2': 116.54,
    'Bb3': 233.08,
    'Bb4': 466.16,
    'Bb5': 932.33,
    'Bb6': 1864.66,
    'Bb7': 3729.3,
    'Bb8': 7458.62,
    'C#0': 17.32,
    'C#1': 34.65,
    'C#2': 69.3,
    'C#3': 138.59,
    'C#4': 277.18,
    'C#5': 554.37,
    'C#6': 1108.73,
    'C#7': 2217.46,
    'C#8': 4434.9,
    'C0': 16.35,
    'C1': 32.7,
    'C2': 65.41,
    'C3': 130.8,
    'C4': 261.63,
    'C5': 523.25,
    'C6': 1046.5,
    'C7': 2093.0,
    'C8': 4186.0,
    'D#0': 19.45,
    'D#1': 38.89,
    'D#2': 77.78,
    'D#3': 155.56,
    'D#4': 311.13,
    'D#5': 622.25,
    'D#6': 1244.51,
    'D#7': 2489.02,
    'D#8': 4978.0,
    'D0': 18.35,
    'D1': 36.71,
    'D2': 73.42,
    'D3': 146.83,
    'D4': 293.66,
    'D5': 587.33,
    'D6': 1174.6,
    'D7': 2349.3,
    'D8': 4698.6,
    'Db0': 17.32,
    'Db1': 34.65,
    'Db2': 69.3,
    'Db3': 138.59,
    'Db4': 277.18,
    'Db5': 554.37,
    'Db6': 1108.73,
    'Db7': 2217.46,
    'Db8': 4434.9,
    'E0': 20.6,
    'E1': 41.2,
    'E2': 82.41,
    'E3': 164.81,
    'E4': 329.63,
    'E5': 659.25,
    'E6': 1318.5,
    'E7': 2637.0,
    'E8': 5274.0,
    'Eb0': 19.45,
    'Eb1': 38.89,
    'Eb2': 77.78,
    'Eb3': 155.56,
    'Eb4': 311.13,
    'Eb5': 622.25,
    'Eb6': 1244.51,
    'Eb7': 2489.02,
    'Eb8': 4978.0,
    'F#0': 23.12,
    'F#1': 46.25,
    'F#2': 92.5,
    'F#3': 185.0,
    'F#4': 369.99,
    'F#5': 739.99,
    'F#6': 1479.98,
    'F#7': 2959.96,
    'F#8': 5919.9,
    'F0': 21.83,
    'F1': 43.65,
    'F2': 87.31,
    'F3': 174.61,
    'F4': 349.23,
    'F5': 698.46,
    'F6': 1396.9,
    'F7': 2793.8,
    'F8': 5587.6,
    'G#0': 25.96,
    'G#1': 51.91,
    'G#2': 103.83,
    'G#3': 207.65,
    'G#4': 415.3,
    'G#5': 830.61,
    'G#6': 1661.22,
    'G#7': 3322.44,
    'G#8': 6644.8,
    'G0': 24.5,
    'G1': 49.0,
    'G2': 98.0,
    'G3': 196.0,
    'G4': 392.0,
    'G5': 783.99,
    'G6': 1567.9,
    'G7': 3135.9,
    'G8': 6271.9,
    'Gb0': 23.12,
    'Gb1': 46.25,
    'Gb2': 92.5,
    'Gb3': 185.0,
    'Gb4': 369.99,
    'Gb5': 739.99,
    'Gb6': 1479.98,
    'Gb7': 2959.96,
    'Gb8': 5919.9
}


def set_all(sample_rate=44100, bits=16, channels=2):
    global BITS, SAMPLE_RATE, CHANNELS, MAX_SAMPLE
    BITS = bits
    SAMPLE_RATE = sample_rate
    CHANNELS = channels
    MAX_SAMPLE = 2 ** (BITS - 1) - 1


def pre_init():
    pygame.mixer.pre_init(SAMPLE_RATE, -BITS, CHANNELS)


def get_stereo(left, right, duration):
    sample_num = int(round(SAMPLE_RATE*duration))
    array = []
    for i in range(sample_num):
        array.append([get_sample(left, i), get_sample(right, i)])
    # Make sure that the last item is around 0
    while (not (-ZERO_RANGE) <= array[sample_num-1][0] <= ZERO_RANGE) or \
            (not (-ZERO_RANGE) <= array[sample_num-1][1] <= ZERO_RANGE):
        ap = [0, 0]
        if array[sample_num-1][0] != 0:
            ap[0] = get_sample(left, sample_num)
        if array[sample_num-1][1] != 0:
            ap[1] = get_sample(right, sample_num)
        sample_num += 1
        array.append(ap)
    ret = numpy.array(array, dtype=numpy.int16)
    return pygame.sndarray.make_sound(ret), ret


def get_mono(hz, duration):
    sample_num = int(round(SAMPLE_RATE * duration))
    array = [get_sample(hz, i) for i in range(sample_num)]
    # Make sure that the last item is around 0
    while not (-ZERO_RANGE) <= array[-1] <= ZERO_RANGE:
        array.append(get_sample(hz, sample_num))
        sample_num += 1
    ret = numpy.array(array, dtype=numpy.int16)
    return pygame.sndarray.make_sound(ret), ret


def get_sample(freq, x):
    return int(round(MAX_SAMPLE * numpy.sin(2 * numpy.pi * freq * x / SAMPLE_RATE)))


def add_static(sound, amount):
    array = pygame.sndarray.samples(sound)
    if CHANNELS == 2:
        for i in range(len(array)):
                array[i][0] += rand.randint(-amount, amount)
                array[i][1] += rand.randint(-amount, amount)
    else:  # Don't run the if every loop. That's dumb.
        for i in range(len(array)):
            array[i] += rand.randint(-amount, amount)


def get_mono_static(duration):
    max_val = 2 ** (BITS - 1) - 1
    min_val = -(2 ** BITS)
    sample_num = int(round(SAMPLE_RATE * duration))
    ret = numpy.array([rand.randint(min_val, max_val) for i in range(sample_num)], dtype=numpy.int16)
    return pygame.sndarray.make_sound(ret), ret


def get_stereo_static(duration):
    max_val = 2 ** (BITS - 1) - 1
    min_val = -(2 ** BITS)
    sample_num = int(round(SAMPLE_RATE * duration))
    ret = numpy.zeros((sample_num, 2), dtype=numpy.int16)
    for i in range(sample_num):
        ret[i][0] = rand.randint(min_val, max_val)
        ret[i][1] = rand.randint(min_val, max_val)
    return pygame.sndarray.make_sound(ret), ret


def save_sound(snd, filename):
    fileproc = wave.open(filename, 'w')
    fileproc.setframerate(SAMPLE_RATE)
    fileproc.setnchannels(CHANNELS)
    fileproc.setsampwidth(2)
    fileproc.writeframesraw(snd.get_raw())
    fileproc.close()


class FrequencyPlayer(object):
    def __init__(self, array, build=True):
        self.array = array
        self.sound = Dummy()
        self.compiled = []
        if build:
            self.build()

    def sync_play(self):
        warnings.warn("sync_play is depreciated. Use build() and play()", DeprecationWarning)
        for note in self.array:
            if CHANNELS == 1:
                logger.debug("Playing %s", note[0][0])
                _sound = get_mono(note[0][0], note[1])[0]
            else:
                logger.debug("Playing (Left=%s Right=%s)", note[0][0], note[0][1])
                _sound = get_stereo(note[0][0], note[0][1], note[1])[0]
            _sound.play(-1)
            pygame.time.wait(int(note[1]*1000))
            _sound.stop()
            pygame.time.wait(int(note[2]*1000))

    def play(self):
        self.sound.play()

    def build(self):
        msg = "Compiled note %s of " + str(len(self.array))
        logger.info("Building... (This may take a while...)")
        ret = numpy.array([], dtype=numpy.int16)
        for num, note in enumerate(self.array, 1):
            sound = get_mono(note[0][0], note[1])[1] if CHANNELS == 1 else \
                    get_stereo(note[0][0], note[0][1], note[1])[1]
            ret = sound.copy() if len(ret) == 0 else numpy.append(ret, sound, axis=0)
            wait = numpy.array([0, ] * int(round(SAMPLE_RATE * note[2])), dtype=numpy.int16) if CHANNELS == 1 else \
                   numpy.array([[0, 0], ] * int(round(SAMPLE_RATE * note[2])), dtype=numpy.int16)
            if len(wait) > 0:
                ret = wait.copy() if len(ret) == 0 else numpy.append(ret, wait, axis=0)
            logger.debug(msg, num)
        self.compiled = ret
        self.sound = pygame.sndarray.make_sound(ret)
        logging.info("Compile finished!")


if __name__ == '__main__':
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s|%(name)s] [%(filename)s:%(lineno)d/%(levelname)s]: %(message)s',
                                  '%H:%M:%S')  # Should we write the channel?
    hdlr.setFormatter(formatter)
    root.addHandler(hdlr)

    pre_init()
    pygame.init()
    test = FrequencyPlayer([[[i, i], 0.01, 0] for i in range(20, 20000, 100)])
    test.play()  # Ok this is a bad idea. EDIT: sync_play is event worse.
    # save_sound(test.sound, '~/Downloads/terror.wav')
    while pygame.mixer.get_busy():
        pass
