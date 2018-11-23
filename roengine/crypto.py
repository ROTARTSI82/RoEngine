# -*- coding: UTF-8 -*-

import random
import hashlib

from roengine.maths import is_prime, gcf

__all__ = ('RSAGenerator', 'hexify_text', 'dehexify_text', 'hashes', 'single_str')


def hexify_text(txt, pretty_print=True, prefix='0x'):
    hlist = []
    for i in str(txt):
        val = hex(ord(i))[2:]
        val = "0" + val if len(val) < 2 else val
        hlist.append(val)
    return " ".join(hlist) if pretty_print else prefix + "".join(hlist)


def dehexify_text(txt):
    tlist = [chr(eval("0x"+txt[i:i+2])) for i in range(0, len(txt), 2)]
    return "".join(tlist)


def split(txt, n, head):
    return [head+txt[i:i+n] for i in range(0, len(txt), n)]


def pad(txt, n, pt):
    if len(txt) > n:
        return txt
    chars_needed = (n - len(txt))
    # Find how many whole `pt`s we could fit, then add the first `remainder` characters of pt
    append = pt * (chars_needed // len(pt)) + pt[:(chars_needed % len(pt))]
    return txt + append


def hashes(p):
    p = str(p)
    s512 = hashlib.sha512(p)
    s384 = hashlib.sha384(p)
    s256 = hashlib.sha256(p)
    s224 = hashlib.sha224(p)
    s1 = hashlib.sha1(p)
    md5 = hashlib.md5(p)
    return ((s512.digest(), s512.hexdigest()), (s384.digest(), s384.hexdigest()), (s256.digest(), s256.hexdigest()),
            (s224.digest(), s224.hexdigest()), (s1.digest(), s1.hexdigest()), (md5.digest(), md5.hexdigest()),
            (str(hash(p)), hex(hash(p)).split('x')[1]))


def single_str(p):
    p = str(p)
    s512 = hashlib.sha512(p)
    s384 = hashlib.sha384(p)
    s256 = hashlib.sha256(p)
    s224 = hashlib.sha224(p)
    s1 = hashlib.sha1(p)
    md5 = hashlib.md5(p)
    h = (s512.hexdigest(), s384.hexdigest(), s256.hexdigest(), s224.hexdigest(),
         s1.hexdigest(), md5.hexdigest(), hex(hash(p)).split("0x")[1])
    return h


# BELOW IS A COMBINATION OF: https://gist.github.com/JonCooperWorks/5314103 and
# http://code.activestate.com/recipes/578838-rsa-a-simple-and-easy-to-read-implementation/

class RSAGenerator(object):
    def __init__(self, p, q, enc_len=8):
        self.p, self.q = p, q
        self.enc_len = enc_len
        self.public, self.private = ((0, 0), (0, 0))
        self.generate_keypair()

    def encrypt(self, plaintext):  # NOTE: Not secure in any way! Basically a Caesar Cipher
        key, n = self.public
        # Convert each letter in the plaintext to numbers based on the character using a^b mod m
        # cipher = [pow(ord(char), key, n) for char in plaintext]
        # Return the array of bytes
        # return cipher

        # hexify_text(...) <-- Gets hex repr of str. Each byte is 2 hex chrs. Basically [hex(ord(i)) for i in txt]

        # split(...) <--  Returns list. All elements of list are the same len, except for maybe the last one.

        # print [int(i, 0) for i in split(hexify_text(plaintext, False, ''), self.enc_len-1, '0x1')]

        return [self.encrypt_n(int(i, 0))  # Loop through what `split` returns, interpret it as int, encrypt.
                for i in split(hexify_text(plaintext, False, ''), self.enc_len-1, '0x1')]

    def encrypt_n(self, num):
        key, n = self.public
        return pow(num, key, n)

    def decrypt(self, ciphertext):  # NOTE: Not secure in any way! Basically a Caesar Cipher
        key, n = self.private
        # Generate the plaintext based on the ciphertext and key using a^b mod m
        # plain = [chr(pow(char, key, n)) for char in ciphertext]
        # Return the array of bytes as a string
        # return ''.join(plain)

        # get hex val of int, ignore first 3 bytes ('0x1') and interpret the rest as text.
        print [hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext]
        split_str = [hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext]
        return dehexify_text("".join(split_str))

    def decrypt_n(self, num):
        key, n = self.private
        return pow(num, key, n)

    def generate_keypair(self):
        p, q = self.p, self.q
        #if not (is_prime(p) and is_prime(q)):
        #    raise ValueError('Both numbers must be prime.')
        if p == q:
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
        self.private = (d, n)
        self.public = (e, n)
        return (e, n), (d, n)


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
