# -*- coding: UTF-8 -*-

import random
import hashlib
import os
import binascii
import hmac as hmac_module
import base64
import subprocess

from roengine.maths import is_prime, gcf

__all__ = ('RSAGenerator', 'hmac', 'User', 'AccountManager', 'is_prime_openssl')


SHOW_PASSDUMP = True
HASH_METHOD = 'sha512'
ROUNDS = 100000  # ~100,000 for sha256 as of 2013
SALT_LEN = 16  # 16 or more from os.urandom()
MAX_PASS = 1024
LEN = 64  # 64 default for sha256


def split(txt, n, head):
    return [head+txt[i:i+n] for i in range(0, len(txt), n)]


def pad(txt, n, pt):
    if len(txt) > n:
        return txt
    chars_needed = (n - len(txt))
    # Find how many whole `pt`s we could fit, then add the first `remainder` characters of pt
    append = pt * (chars_needed // len(pt)) + pt[:(chars_needed % len(pt))]
    return txt + append


class AccountManager(object):
    def __init__(self, hash_method='sha512', salt_len=16, hash_len=64, rounds=100000):
        self.method = hash_method
        self.salt_len = salt_len
        self.hash_len = hash_len
        self.iter = rounds
        self.users = {}

    def make_guest_account(self):
        self.new_acc("Guest", "guest123")
        dummy_user = User(self)
        dummy_user.write_data("Hello World! This is the Guest account. Please sign in.")

    def read(self, user, psw):
        if user not in self.users:
            return False
        rsa = RSAGenerator(0, 0, 256, False)
        rsa.public, rsa.private = self.users[user][3]
        return rsa.decrypt_p(psw, self.users[user][2])

    def write(self, dat, user, psw):
        if user not in self.users:
            return False
        rsa = RSAGenerator(0, 0, 256, False)
        rsa.public, rsa.private = self.users[user][3]
        self.users[user][2] = rsa.encrypt_p(psw, dat)
        return self.users[user]

    def get_login(self, user, psw):
        if user not in self.users:
            print("Invalid Username!")
            return 0  # Returns int (not bool) but equates to False if interpreted as one.
        if hmac_module.compare_digest(hmac(psw, self.users[user][1]), self.users[user][0]):
            return self.users[user]
        return False

    def new_acc(self, user, psw):
        if user in self.users:
            print("Username already taken!")
            return False
        salt = get_salt(self.users, self.salt_len)
        current_primes = get_primes(salt)
        current_rsa = RSAGenerator(current_primes[0], current_primes[1], 256)
        self.users[user] = [hmac(psw, salt), salt,  [], [current_rsa.public, current_rsa.private]]
        return True


class User(object):
    def __init__(self, acc_manager):
        self.current_user = "Guest"
        self.psw = "guest123"
        self.acc_manager = acc_manager

    def login(self, user, psw):
        userdat = self.acc_manager.get_login(user, psw)
        if userdat:
            self.current_user = user
            self.psw = psw
        return userdat

    def logout(self):
        self.current_user = "Guest"
        self.psw = "guest123"

    def read_data(self):
        return self.acc_manager.read(self.current_user, self.psw)

    def write_data(self, data):
        return self.acc_manager.write(data, self.current_user, self.psw)


def get_salt(userdict, salt_len=SALT_LEN):
    salt = os.urandom(salt_len)
    salts = [i[1] for i in userdict.values()]
    while salt in salts:
        salt = os.urandom(salt_len)
    return salt


def hmac(psw, salt, method=HASH_METHOD, iter=ROUNDS, length=LEN):
    return binascii.hexlify(hashlib.pbkdf2_hmac(method, psw, salt, iter, length))


def wrap(minimum, maximum, val):
    if minimum <= val <= maximum:
        return val
    while val > maximum:
        val -= maximum + 1
    while val < minimum:
        val = maximum-(minimum-val) + 1
    return val


def is_prime_openssl(n):
    return subprocess.check_output(['openssl', 'prime', str(n)]).endswith('is prime\n')


def get_primes(salt, maximum=1024, minimum=512, power=2):
    prime_start = pow(power, wrap(minimum, maximum, sum([ord(i) for i in salt])))
    primes = []
    while len(primes) < 2:
        if is_prime_openssl(prime_start):
            primes.append(prime_start)
            # print (prime_start)
        prime_start += 1
    return primes

# BELOW IS A COMBINATION OF: https://gist.github.com/JonCooperWorks/5314103 and
# http://code.activestate.com/recipes/578838-rsa-a-simple-and-easy-to-read-implementation/


class RSAGenerator(object):
    def __init__(self, p, q, enc_len=8, gen_keys=True):
        self.p, self.q = p, q
        self.enc_len = enc_len
        self.public, self.private = ((0, 0), (0, 0))
        if gen_keys:
            self.generate_keypair()

    def encrypt(self, plaintext):  # NOTE: Not secure in any way! Basically a Caesar Cipher
        key, n = self.public

        # binascii.hexlify(...) <-- Gets hex repr of str. Each byte is 2 hex chrs. Basically [hex(ord(i)) for i in txt]
        # split(...) <--  Returns list. All elements of list are the same len, except for maybe the last one.
        # print [int(i, 0) for i in split(binascii.hexlify(plaintext, False, ''), self.enc_len-1, '0x1')]

        return [self.encrypt_n(int(i, 0))  # Loop through what `split` returns, interpret it as int, encrypt.
                for i in split(binascii.hexlify(plaintext), self.enc_len-1, '0x1')]

    def encrypt_n(self, num):
        key, n = self.public
        return pow(num, key, n)

    def encrypt_p(self, key, clear, en_b64=True):
        enc = []
        for i in range(len(clear)):
            key_c = key[i % len(key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        enc = "".join(enc)
        if en_b64:
            enc = base64.urlsafe_b64encode(enc)
        return self.encrypt(enc)

    def decrypt_p(self, key, enc, en_b64=True):
        enc = self.decrypt(enc)
        dec = []
        if en_b64:
            enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = key[i % len(key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)

    def decrypt(self, ciphertext):
        key, n = self.private
        # get hex val of int, ignore first 3 bytes ('0x1') and interpret the rest as text.
        # print ([hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext])
        split_str = [hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext]
        return binascii.unhexlify("".join(split_str))

    def decrypt_n(self, num):
        key, n = self.private
        return pow(num, key, n)

    def generate_keypair(self):
        p, q = self.p, self.q
        # I've chosen crazy big primes with openssl. Checking for primes would take too long, and is redundant.
        #if not (is_prime(p) and is_prime(q)):
        #    raise ValueError('Both numbers must be prime.')
        if p == q:
            raise ValueError('p and q cannot be equal')
        n = p * q
        phi = (p - 1) * (q - 1)
        e = random.randrange(1, phi)

        g = gcf(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = gcf(e, phi)

        d = multiplicative_inverse(e, phi)

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
