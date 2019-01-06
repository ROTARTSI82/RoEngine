# -*- coding: UTF-8 -*-

from __future__ import division

import os
import binascii
import time


class URandom(object):
    def __init__(self, length=127):
        self.length = length

    def random(self):
        MAX = 256 ** self.length - 1
        n = int(binascii.hexlify(os.urandom(self.length)), 16)
        return float(n) / float(MAX)  # Scale result to fit between [0, 1] uniformly

    def randint(self, a, b):
        return int(round(self.uniform(a, b)))

    def uniform(self, a, b):
        g = max(a, b)
        l = min(a, b)
        return l + (g - l) * self.random()

    def choice(self, iterable):
        return iterable[int(self.random() * len(iterable))]


def _nrand():
    return int(binascii.hexlify(os.urandom(8)), 16)


class XORShift(object):
    """
    Literally just the C code from
    https://en.wikipedia.org/wiki/Xorshift
    """
    def __init__(self, randfunc=_nrand):
        self.state = {"128+": [randfunc(), randfunc()],
                      "1024*": (0, [randfunc() for i in range(16)]),
                      '64*': randfunc(), 'wow': [randfunc() for i in range(5)], '32': randfunc(), '64': randfunc(),
                      '128': [randfunc() for i in range(6)]}

    def xorshift32(self):
        """
        # Algorithm "xor" from p.4 of Marsaglia, "Xorshift RNGs"
        """
        x = self.state['32']
        x ^= x << 13
        x ^= x >> 17
        x ^= x << 5
        self.state['32'] = x
        return x

    def xorshift64(self):
        x = self.state['64']
        x ^= x << 13
        x ^= x >> 7
        x ^= x << 17
        self.state['64'] = x
        return x

    def xorshift128(self):
        """
        # Algorithm "xor128" from p.5 of Marsaglia, "Xorshift RNGs"
        """
        state = self.state['128']
        s, t = state[3], state[4]  # These it is again. ???
        t ^= t << 11
        t ^= t >> 8
        state[3] = state[2]
        state[2] = state[1]
        state[1] = s = state[0]
        t ^= s
        t ^= s >> 19
        state[0] = t
        self.state['128'] = state
        return t

    def xorwow(self):
        """
        # Algorithm "xorwow" from p.5 of Marsaglia, "Xorshift RNGs"
        """
        state = self.state['wow']
        # Wait what? `s, t = state[3]`
        s, t = state[3], state[4]  # This is my best guess, considering xorwow requires a len 5 array.
        t ^= t >> 2
        t ^= t << 1
        state[3] = state[2]
        state[2] = state[1]
        state[1] = s = state[0]
        t ^= s
        t ^= s << 4
        state[0] = t
        state[4] += 362437
        self.state['wow'] = state
        return t + state[4]

    def xorshift1024star(self):
        p, s = self.state['1024*']
        s0 = s[p]
        p += 1
        s1 = s[p]
        p &= 15
        s1 ^= s1 << 31 # a
        s1 ^= s1 >> 11 # b
        s1 ^= s0 ^ (s0 >> 30) # c
        s[p] = s1
        self.state['1024*'] = p, s
        return s1 * 1181783497276652981

    def xorshift64star(self):
        x = self.state['64*'] # The state must be seeded with a non-zero value.
        x ^= x >> 12  # a
        x ^= x << 25  # b
        x ^= x >> 27  # c
        self.state['64*'] = x
        return x * 0x2545F4914F6CDD1D

    def xorshift128plus(self):
        x = self.state['128+'][0]
        y = self.state['128+'][1]
        self.state['128+'][0] = y
        x ^= x << 23  # a
        self.state['128+'][1] = x ^ y ^ (x >> 17) ^ (y >> 26)  # b, c
        return self.state['128+'][1] + y


CONST = {
    "32":
        {
            ("w", "n", "m", "r"): (32, 624, 397, 31),
            ("a", ): (0x9908B0DF, ),
            ("u", "d"): (11, 0xFFFFFFFF),
            ("s", "b"): (7, 0x9D2C5680),
            ("t", "c"): (15, 0xEFC60000),
            ("l", ): (18, ),
            ("f", ): (1812433253, ),
        },
    "64":
        {
            ("w", "n", "m", "r"): (64, 312, 156, 31),
            ("a", ): (0xB5026F5AA96619E9, ),
            ("u", "d"): (29, 0x5555555555555555),
            ("s", "b"): (17, 0x71D67FFFEDA60000),
            ("t", "c"): (37, 0xFFF7EEE000000000),
            ("l", ): (43, ),
            ("f", ): (6364136223846793005, ),
        }
}


def _lowest(x, nbits):
    return x & ((1 << nbits) - 1)


class Twister(object):
    """
    Literally just the Pseudocode from
    https://en.wikipedia.org/wiki/Mersenne_Twister
    """
    w = 0
    n = 0
    m = 0
    r = 0
    a = 0
    u = 0
    d = 0
    s = 0
    b = 0
    t = 0
    c = 0
    l = 0
    f = 0

    def __init__(self, const='64'):
        self.set_consts(CONST[const])
        self.MT = [0, ] * self.n  # Size n array to store state
        self.index = self.n + 1
        self.lower_mask = (1 << self.r) - 1  # Binary (r 1s)
        self.upper_mask = _lowest(~self.lower_mask, self.w)  # Lowest w bits of (not lower_mask)

    def set_consts(self, consts):
        for k, v in zip(consts.keys(), consts.values()):
            for c, val in zip(k, v):
                setattr(self, c, val)

    def seed_mt(self, seed):
        """
        Seed the generator.

        :param seed: int
        :return: None
        """
        self.index = self.n
        self.MT[0] = seed
        for i in range(1, self.n):
            self.MT[i] = _lowest(self.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.w-2))) + i, self.w)

    def extract_number(self):
        """
        Extract a tempered value based on MT[index]
        calling twist() every n numbers

        :return: int
        """
        if self.index >= self.n:
            if self.index > self.n:
                # The generator was never seeded! Alternatively, we could seed it with a constant value
                # The following code was ripped from the random module. The pseudocode just raised an error.
                try:
                    self.seed_mt(int(binascii.hexlify(os.urandom(2500)), 16))
                except:
                    self.seed_mt(time.time() * 256)
            self.twist()

        y = self.MT[self.index]
        y ^= (y >> self.u) & self.d
        y ^= (y << self.s) & self.b
        y ^= (y << self.t) & self.c
        y ^= y >> self.l

        self.index += 1
        return _lowest(y, self.w)  # Or should we just return y?

    def twist(self):
        """
        Generate the next n values from the series x_i

        :return: None
        """
        for i in range(self.n):
            x = (self.MT[i] & self.upper_mask) + (self.MT[(i + 1) % self.n] & self.lower_mask)
            xA = x >> 1
            if x % 2 != 0:
                # In this case, the lowest bit of x is 1
                xA ^= self.a
            self.MT[i] = self.MT[(i + self.m) % self.n] ^ xA
        self.index = 0

    def random(self):
        return (self.extract_number() / (1 << self.w)) % 1.0

    def uniform(self, a, b):
        g = max(a, b)
        l = min(a, b)
        return l + (g - l) * self.random()

    def randint(self, a, b):
        return int(round(self.uniform(a, b)))

    def choice(self, seq):
        # It is impossible for for self.random to be 1, so this expression cannot be equal to len(seq)
        return seq[int(len(seq) * self.random())]
