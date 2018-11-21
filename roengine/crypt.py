# -*- coding: UTF-8 -*-

import random
import struct
import sys
import hashlib

from threading import Lock
from roengine.maths import is_prime, gcf

__all__ = ('dumps', 'loads', 'RSAGenerator', 'hexify_text', 'dehexify_text', 'hashes', 'single_str')


def hexify_text(txt, pretty_print=True, prefix='0x'):
    hlist = [hex(ord(i))[2:] for i in str(txt)]
    return " ".join(hlist) if pretty_print else prefix + "".join(hlist)


def dehexify_text(txt):
    tlist = [chr(eval("0x"+txt[i:i+2])) for i in range(0, len(txt), 2)]
    return "".join(tlist)


def hashes(p):
    p = str(p)
    s512 = hashlib.sha512(p)
    s384 = hashlib.sha384(p)
    s256 = hashlib.sha256(p)
    s224 = hashlib.sha224(p)
    s1 = hashlib.sha1(p)
    md5 = hashlib.md5(p)
    return ((str(hash(p)), hexify_text(hash(p), False, "")), (s512.digest(), s512.hexdigest()),
            (s384.digest(), s384.hexdigest()), (s256.digest(), s256.hexdigest()), (s224.digest(), s224.hexdigest()),
            (s1.digest(), s1.hexdigest()), (md5.digest(), md5.hexdigest()))


def single_str(p):
    h = hashes(p)
    ret = ""
    for method in h:
        ret += method[1]
    return ret


class RSAGenerator(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
        self.public, self.private = ((0, 0), (0, 0))
        self.generate_keypair()

    def encrypt(self, plaintext):
        # Unpack the key into it's components
        key, n = self.private
        # Convert each letter in the plaintext to numbers based on the character using a^b mod m
        cipher = [pow(ord(char), key, n) for char in plaintext]
        # Return the array of bytes
        return cipher

    def decrypt(self, ciphertext):
        # Unpack the key into its components
        key, n = self.public
        # Generate the plaintext based on the ciphertext and key using a^b mod m
        plain = [chr(pow(char, key, n)) for char in ciphertext]
        # Return the array of bytes as a string
        return ''.join(plain)

    def generate_keypair(self):
        p, q = self.p, self.q
        if not (is_prime(p) and is_prime(q)):
            raise ValueError('Both numbers must be prime.')
        elif p == q:
            raise ValueError('p and q cannot be equal')
        # n = pq
        n = p * q

        # Phi is the totient of n
        phi = (p - 1) * (q - 1)

        # Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)

        # Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = gcf(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = gcf(e, phi)

        # Use Extended Euclid's Algorithm to generate the private key
        d = multiplicative_inverse(e, phi)

        # Return public and private keypair
        # Public key is (e, n) and private key is (d, n)
        self.public = (e, n)
        self.private = (d, n)
        return ((e, n), (d, n))


def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi / e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi


# https://github.com/aresch/rencode
#
# This is tweaked to add native tuple type
#
# Original bencode module by Petru Paler, et al.
#
# Modifications by Connelly Barnes:
#
#  - Added support for floats (sent as 32-bit or 64-bit in network
#    order), bools, None.
#  - Allowed dict keys to be of any serializable type.
#  - Lists/tuples are always decoded as tuples (thus, tuples can be
#    used as dict keys).
#  - Embedded extra information in the 'typecodes' to save some space.
#  - Added a restriction on integer length, so that malicious hosts
#    cannot pass us large integers which take a long time to decode.
#
# Licensed by Bram Cohen under the "MIT license":
#
#  "Copyright (C) 2001-2002 Bram Cohen
#
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction,
#  including without limitation the rights to use, copy, modify, merge,
#  publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  The Software is provided "AS IS", without warranty of any kind,
#  express or implied, including but not limited to the warranties of
#  merchantability,  fitness for a particular purpose and
#  noninfringement. In no event shall the  authors or copyright holders
#  be liable for any claim, damages or other liability, whether in an
#  action of contract, tort or otherwise, arising from, out of or in
#  connection with the Software or the use or other dealings in the
#  Software."
#
# (The rencode module is licensed under the above license as well).
#
# pylint: disable=redefined-builtin

"""
rencode -- Web safe object pickling/unpickling.
Public domain, Connelly Barnes 2006-2007.
The rencode module is a modified version of bencode from the
BitTorrent project.  For complex, heterogeneous data structures with
many small elements, r-encodings take up significantly less space than
b-encodings:
 >>> len(rencode.dumps({'a':0, 'b':[1,2], 'c':99}))
 13
 >>> len(bencode.bencode({'a':0, 'b':[1,2], 'c':99}))
 26
The rencode format is not standardized, and may change with different
rencode module versions, so you should check that you are using the
same rencode version throughout your project.
"""


py3 = sys.version_info[0] >= 3
if py3:
    long = int
    unicode = str

    def int2byte(c):
        return bytes([c])
else:
    def int2byte(c):
        return chr(c)

# Default number of bits for serialized floats, either 32 or 64 (also a parameter for dumps()).
DEFAULT_FLOAT_BITS = 32

# Maximum length of integer when written as base 10 string.
MAX_INT_LENGTH = 64

# The bencode 'typecodes' such as i, d, etc have been extended and
# relocated on the base-256 character set.
CHR_TUPLE = int2byte(58)
CHR_LIST = int2byte(59)
CHR_DICT = int2byte(60)
CHR_INT = int2byte(61)
CHR_INT1 = int2byte(62)
CHR_INT2 = int2byte(63)
CHR_INT4 = int2byte(64)
CHR_INT8 = int2byte(65)
CHR_FLOAT32 = int2byte(66)
CHR_FLOAT64 = int2byte(44)
CHR_TRUE = int2byte(67)
CHR_FALSE = int2byte(68)
CHR_NONE = int2byte(69)
CHR_TERM = int2byte(127)

# Positive integers with value embedded in typecode.
INT_POS_FIXED_START = 0
INT_POS_FIXED_COUNT = 44

# Dictionaries with length embedded in typecode.
DICT_FIXED_START = 102
DICT_FIXED_COUNT = 25

# Negative integers with value embedded in typecode.
INT_NEG_FIXED_START = 70
INT_NEG_FIXED_COUNT = 32

# Strings with length embedded in typecode.
STR_FIXED_START = 128
STR_FIXED_COUNT = 64

# Lists with length embedded in typecode.
LIST_FIXED_START = STR_FIXED_START + STR_FIXED_COUNT
LIST_FIXED_COUNT = 32

# Tuples with length embedded in typecode.
TUPLE_FIXED_START = LIST_FIXED_START + LIST_FIXED_COUNT
TUPLE_FIXED_COUNT = 32

# Whether strings should be decoded when loading
_decode_utf8 = True


def decode_int(x, f):
    f += 1
    newf = x.index(CHR_TERM, f)
    if newf - f >= MAX_INT_LENGTH:
        raise ValueError('overflow')
    try:
        n = int(x[f:newf])
    except (OverflowError, ValueError):
        n = long(x[f:newf])
    if x[f:f + 1] == '-':
        if x[f + 1:f + 2] == '0':
            raise ValueError
    elif x[f:f + 1] == '0' and newf != f + 1:
        raise ValueError
    return (n, newf + 1)


def decode_intb(x, f):
    f += 1
    return (struct.unpack('!b', x[f:f + 1])[0], f + 1)


def decode_inth(x, f):
    f += 1
    return (struct.unpack('!h', x[f:f + 2])[0], f + 2)


def decode_intl(x, f):
    f += 1

    return (struct.unpack('!l', x[f:f + 4])[0], f + 4)


def decode_intq(x, f):
    f += 1
    return (struct.unpack('!q', x[f:f + 8])[0], f + 8)


def decode_float32(x, f):
    f += 1
    n = struct.unpack('!f', x[f:f + 4])[0]
    return (n, f + 4)


def decode_float64(x, f):
    f += 1
    n = struct.unpack('!d', x[f:f + 8])[0]
    return (n, f + 8)


def decode_string(x, f):
    colon = x.index(b':', f)
    try:
        n = int(x[f:colon])
    except (OverflowError, ValueError):
        n = long(x[f:colon])
    if x[f] == '0' and colon != f + 1:
        raise ValueError
    colon += 1
    s = x[colon:colon + n]
    if _decode_utf8:
        s = s.decode('utf8')
    return (s, colon + n)


def decode_list(x, f):
    r, f = [], f + 1
    while x[f:f + 1] != CHR_TERM:
        v, f = decode_func[x[f:f + 1]](x, f)
        r.append(v)
    return (r, f + 1)

def decode_tuple(x, f):
    r, f = [], f + 1
    while x[f:f + 1] != CHR_TERM:
        v, f = decode_func[x[f:f + 1]](x, f)
        r.append(v)
    return (tuple(r), f + 1)

def decode_dict(x, f):
    r, f = {}, f + 1
    while x[f:f + 1] != CHR_TERM:
        k, f = decode_func[x[f:f + 1]](x, f)
        r[k], f = decode_func[x[f:f + 1]](x, f)
    return (r, f + 1)


def decode_true(x, f):
    return (True, f + 1)


def decode_false(x, f):
    return (False, f + 1)


def decode_none(x, f):
    return (None, f + 1)

decode_func = {}
decode_func[b'0'] = decode_string
decode_func[b'1'] = decode_string
decode_func[b'2'] = decode_string
decode_func[b'3'] = decode_string
decode_func[b'4'] = decode_string
decode_func[b'5'] = decode_string
decode_func[b'6'] = decode_string
decode_func[b'7'] = decode_string
decode_func[b'8'] = decode_string
decode_func[b'9'] = decode_string
decode_func[CHR_TUPLE] = decode_tuple
decode_func[CHR_LIST] = decode_list
decode_func[CHR_DICT] = decode_dict
decode_func[CHR_INT] = decode_int
decode_func[CHR_INT1] = decode_intb
decode_func[CHR_INT2] = decode_inth
decode_func[CHR_INT4] = decode_intl
decode_func[CHR_INT8] = decode_intq
decode_func[CHR_FLOAT32] = decode_float32
decode_func[CHR_FLOAT64] = decode_float64
decode_func[CHR_TRUE] = decode_true
decode_func[CHR_FALSE] = decode_false
decode_func[CHR_NONE] = decode_none


def make_fixed_length_string_decoders():
    def make_decoder(slen):
        def f(x, f):
            s = x[f + 1:f + 1 + slen]
            if _decode_utf8:
                s = s.decode("utf8")
            return (s, f + 1 + slen)
        return f
    for i in range(STR_FIXED_COUNT):
        decode_func[int2byte(STR_FIXED_START + i)] = make_decoder(i)

make_fixed_length_string_decoders()


def make_fixed_length_list_decoders():
    def make_decoder(slen):
        def f(x, f):
            r, f = [], f + 1
            for _ in range(slen):
                v, f = decode_func[x[f:f + 1]](x, f)
                r.append(v)
            return (list(r), f)
        return f
    for i in range(LIST_FIXED_COUNT):
        decode_func[int2byte(LIST_FIXED_START + i)] = make_decoder(i)

make_fixed_length_list_decoders()

def make_fixed_length_tuple_decoders():
    def make_decoder(slen):
        def f(x, f):
            r, f = [], f + 1
            for _ in range(slen):
                v, f = decode_func[x[f:f + 1]](x, f)
                r.append(v)
            return (tuple(r), f)
        return f
    for i in range(TUPLE_FIXED_COUNT):
        decode_func[int2byte(TUPLE_FIXED_START + i)] = make_decoder(i)

make_fixed_length_tuple_decoders()

def make_fixed_length_int_decoders():
    def make_decoder(j):
        def f(x, f):
            return (j, f + 1)
        return f
    for i in range(INT_POS_FIXED_COUNT):
        decode_func[int2byte(INT_POS_FIXED_START + i)] = make_decoder(i)
    for i in range(INT_NEG_FIXED_COUNT):
        decode_func[int2byte(INT_NEG_FIXED_START + i)] = make_decoder(-1 - i)

make_fixed_length_int_decoders()


def make_fixed_length_dict_decoders():
    def make_decoder(slen):
        def f(x, f):
            r, f = {}, f + 1
            for _ in range(slen):
                k, f = decode_func[x[f:f + 1]](x, f)
                r[k], f = decode_func[x[f:f + 1]](x, f)
            return (r, f)
        return f
    for i in range(DICT_FIXED_COUNT):
        decode_func[int2byte(DICT_FIXED_START + i)] = make_decoder(i)

make_fixed_length_dict_decoders()


def loads(x, decode_utf8=True):
    global _decode_utf8
    _decode_utf8 = decode_utf8
    try:
        r, l = decode_func[x[0:1]](x, 0)
    except (IndexError, KeyError):
        raise ValueError
    if l != len(x):
        raise ValueError
    return r


def encode_int(x, r):
    if 0 <= x < INT_POS_FIXED_COUNT:
        r.append(int2byte(INT_POS_FIXED_START + x))
    elif -INT_NEG_FIXED_COUNT <= x < 0:
        r.append(int2byte(INT_NEG_FIXED_START - 1 - x))
    elif -128 <= x < 128:
        r.extend((CHR_INT1, struct.pack('!b', x)))
    elif -32768 <= x < 32768:
        r.extend((CHR_INT2, struct.pack('!h', x)))
    elif -2147483648 <= x < 2147483648:
        r.extend((CHR_INT4, struct.pack('!l', x)))
    elif -9223372036854775808 <= x < 9223372036854775808:
        r.extend((CHR_INT8, struct.pack('!q', x)))
    else:
        s = str(x)
        if py3:
            s = bytes(s, "ascii")

        if len(s) >= MAX_INT_LENGTH:
            raise ValueError('overflow')
        r.extend((CHR_INT, s, CHR_TERM))


def encode_float32(x, r):
    r.extend((CHR_FLOAT32, struct.pack('!f', x)))


def encode_float64(x, r):
    r.extend((CHR_FLOAT64, struct.pack('!d', x)))


def encode_bool(x, r):
    r.append({False: CHR_FALSE, True: CHR_TRUE}[bool(x)])


def encode_none(x, r):
    r.append(CHR_NONE)


def encode_string(x, r):
    if len(x) < STR_FIXED_COUNT:
        r.extend((int2byte(STR_FIXED_START + len(x)), x))
    else:
        s = str(len(x))
        if py3:
            s = bytes(s, "ascii")
        r.extend((s, b':', x))


def encode_unicode(x, r):
    encode_string(x.encode("utf8"), r)


def encode_list(x, r):
    if len(x) < LIST_FIXED_COUNT:
        r.append(int2byte(LIST_FIXED_START + len(x)))
        for i in x:
            encode_func[type(i)](i, r)
    else:
        r.append(CHR_LIST)
        for i in x:
            encode_func[type(i)](i, r)
        r.append(CHR_TERM)

def encode_tuple(x, r):
    if len(x) < TUPLE_FIXED_COUNT:
        r.append(int2byte(TUPLE_FIXED_START + len(x)))
        for i in x:
            encode_func[type(i)](i, r)
    else:
        r.append(CHR_TUPLE)
        for i in x:
            encode_func[type(i)](i, r)
        r.append(CHR_TERM)

def encode_dict(x, r):
    if len(x) < DICT_FIXED_COUNT:
        r.append(int2byte(DICT_FIXED_START + len(x)))
        for k, v in x.items():
            encode_func[type(k)](k, r)
            encode_func[type(v)](v, r)
    else:
        r.append(CHR_DICT)
        for k, v in x.items():
            encode_func[type(k)](k, r)
            encode_func[type(v)](v, r)
        r.append(CHR_TERM)

encode_func = {}
encode_func[int] = encode_int
encode_func[long] = encode_int
encode_func[bytes] = encode_string
encode_func[list] = encode_list
encode_func[tuple] = encode_tuple
encode_func[dict] = encode_dict
encode_func[type(None)] = encode_none
encode_func[unicode] = encode_unicode
encode_func[bool] = encode_bool

lock = Lock()


def dumps(x, float_bits=DEFAULT_FLOAT_BITS):
    """
    Dump data structure to str.
    Here float_bits is either 32 or 64.
    """
    with lock:
        if float_bits == 32:
            encode_func[float] = encode_float32
        elif float_bits == 64:
            encode_func[float] = encode_float64
        else:
            raise ValueError('Float bits (%d) is not 32 or 64' % float_bits)
        r = []
        encode_func[type(x)](x, r)
    return b''.join(r)

try:
    import psyco
    psyco.bind(dumps)
    psyco.bind(loads)
except ImportError:
    pass
