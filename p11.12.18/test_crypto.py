# -*- coding: UTF-8 -*-
import time

from roengine.misc import crypto as c


def make_enc_safe(string):
    return string.encode('utf-8').strip()


# Just for reference, both are incredibly slow. The following is `rencode`'s time
# av. time 0.0000108517706394 (1.085e-5!) Tot. time 0.00277805328369 (256 cycles)

# Here's `marshal`'s time!
# av. time 0.00000289082527161 (2.89e-6!) Tot. time 0.000740051269531 (256 cycles)

primes1024 = [  # av. time 0.160940841772 Tot. time 41.2008554935 (enc len 512, 256 cycles)
    0x1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bd6d,
    0x1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c90f]
primes512 = [  # av. time 0.038994487375 Tot. time 9.98258876801 (enc len 256, 256 cycles)
    0x1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000123cd,
    0x100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000012621, ]
primes256 = [  # av. time 0.0131396586075 Tot. time 3.36375260353 (enc len 128, 256 cycles)
    0x1000000000000000000000000000000000000000000000000000000000000c1db,
    0x1000000000000000000000000000000000000000000000000000000000000c433,
]
prime128 = [  # av. time 0.00656530074775 Tot. time 1.68071699142 (enc len 64, 256 cycles)
    0x1000000000000000000000000000185b3,
    0x10000000000000000000000000001861f
]
prime64 = [  # av. time 0.00520088709891 Tot. time 1.33142709732 (enc len 32, 256 cycles)
    0x100000000000011ef,
    0x10000000000001267
]
prime32 = [4294969207, 4294969229]  # av. time 0.00472140870988 Tot. time 1.20868062973 (enc len 16, 256 cycles)
prime16 = [0x10429, 0x10439]  # av. time 0.00524639803916 Tot. time 1.34307789803 (enc len 8, 256 cycles)
prime8 = [0x373, 0x377]  # av. time 0.00341407489032 Tot. time 0.874003171921 (enc len 4, 256 cycles)
prime4 = [571, 577]  # av. time 0.00477001909167 Tot. time 1.22112488747 (enc len 2, 256 cycles)
alph = "".join([chr(i) for i in range(256)])
times = []
for i in range(1):
    start = time.time()
    gen = c.RSAGenerator(primes1024[0], primes1024[1], 512)  # p and q are 1024 bits, so len could be at most 512
    ct = gen.encrypt(alph)
    dc = gen.decrypt(ct)
    stop = time.time()
    times.append(stop - start)
print "av. time", sum(times) / float(len(times))
print "Tot. time", sum(times)
print dc == alph