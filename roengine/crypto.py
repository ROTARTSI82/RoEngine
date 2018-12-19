# -*- coding: UTF-8 -*-

import random
import logging
import hashlib
import os
import binascii
import hmac as hmac_module
import subprocess

from roengine.maths import gcf

__all__ = ('RSAGenerator', 'hmac', 'User', 'AccountManager', 'is_prime_openssl')


SHOW_PASSDUMP = True
HASH_METHOD = 'sha512'
ROUNDS = 100000  # ~100,000 for sha256 as of 2013
SALT_LEN = 16  # 16 or more from os.urandom()
MAX_PASS = 1024
LEN = 64  # 64 default for sha256
PRIME_RANGE = (512, 1024)
CHUNK_SIZE = 2**512

cryptLog = logging.getLogger('crypto')
rsaGenLog = logging.getLogger('crypto.rsa')
userLog = logging.getLogger('crypto.user')
accLog = logging.getLogger('crypto.account')


def split(txt, n, head=''):
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
        accLog.info("New AccountManager(method=%s, salt_len=%s, hash_len=%s, iter=%s)",
                      hash_method, salt_len, hash_len, rounds)
        self.method = hash_method
        self.salt_len = salt_len
        self.hash_len = hash_len
        self.iter = rounds
        self.users = {}

    def make_guest_account(self):
        accLog.info("Making guest account!")
        self.new_acc("Guest", "guest123")
        dummy_user = User(self)
        dummy_user.write_data("Hello World! This is the Guest account. Please sign in.")

    def dec(self, data, user, psw):
        if user not in self.users:
            return ""
        seed = sum(ord(i) for i in psw)
        current_primes = get_primes(psw)
        random.seed(seed)
        rsa = RSAGenerator(current_primes[0], current_primes[1], PRIME_RANGE[0] / 2)
        return rsa.decrypt_p(psw, data, seed)  # use auto seed?

    def enc(self, dat, user, psw):
        if user not in self.users:
            return []
        seed = sum(ord(i) for i in psw)
        current_primes = get_primes(psw)
        random.seed(seed)
        rsa = RSAGenerator(current_primes[0], current_primes[1], PRIME_RANGE[0] / 2)
        return rsa.encrypt_p(psw, dat, seed)  # use auto seed?

    def read(self, user, psw):
        if user not in self.users:
            return False
        seed = sum(ord(i) for i in psw)
        current_primes = get_primes(psw)
        random.seed(seed)
        rsa = RSAGenerator(current_primes[0], current_primes[1], PRIME_RANGE[0]/2)
        return rsa.decrypt_p(psw, self.users[user][2], seed)  # use auto seed?

    def write(self, dat, user, psw):
        if user not in self.users:
            return False
        seed = sum(ord(i) for i in psw)
        current_primes = get_primes(psw)
        random.seed(seed)
        rsa = RSAGenerator(current_primes[0], current_primes[1], PRIME_RANGE[0]/2)
        self.users[user][2] = rsa.encrypt_p(psw, dat, seed)  # use auto seed?
        return self.users[user][2]

    def get_login(self, user, psw):
        accLog.info("Attempting to log into: '%s'", user)
        if user not in self.users:
            accLog.info("Unregistered username!")
            return 0  # Returns int (not bool) but equates to False if interpreted as one.
        if hmac_module.compare_digest(hmac(psw, self.users[user][1]), self.users[user][0]):
            accLog.info("Successfully logged in!")
            return self.users[user]
        accLog.info("Invalid passcode!")
        return False

    def new_acc(self, user, psw):
        accLog.info("Attempting to create new account: '%s'", user)
        if user in self.users:
            accLog.info("Username already taken!")
            return False
        salt = get_salt(self.users, self.salt_len)
        self.users[user] = [hmac(psw, salt), salt, []]
        accLog.info("Account successfully created.")
        return True


class User(object):
    def __init__(self, acc_manager):
        self.current_user = "Guest"
        self.psw = "guest123"
        self.salt = "****************"
        self.acc_manager = acc_manager

    def login(self, user, psw):
        userLog.info("User attempting to login to '%s'", user)
        userdat = self.acc_manager.get_login(user, psw)
        if userdat:
            userLog.info("Login successful.")
            self.current_user = user
            self.psw = psw
            self.salt = userdat[1]
            return userdat
        userLog.info("Login unsuccessful")
        return userdat

    def logout(self):
        cryptLog.info("logging out...")
        self.current_user = "Guest"
        self.psw = "guest123"
        self.salt = "****************"

    def read_data(self, psw='auto'):
        psw = self.psw + self.salt if psw == 'auto' else psw
        # print (self.current_user, self.psw)
        return self.acc_manager.read(self.current_user, psw)

    def enc_data(self, data, psw='auto'):
        psw = self.psw + self.salt if psw == 'auto' else psw
        return self.acc_manager.enc(data, self.current_user, psw)

    def dec_data(self, data, psw='auto'):
        psw = self.psw + self.salt if psw == 'auto' else psw
        return self.acc_manager.dec(data, self.current_user, psw)

    def write_data(self, data, psw='auto'):
        psw = self.psw + self.salt if psw == 'auto' else psw
        # print (self.current_user, self.psw)
        return self.acc_manager.write(data, self.current_user, psw)


def get_salt(userdict, salt_len=SALT_LEN):
    salt = os.urandom(salt_len)
    salts = [i[1] for i in userdict.values()]
    cryptLog.info("Getting unused salt...")
    iternum = 1
    while salt in salts:  # Execution might get stuck so log it.
        cryptLog.info("Salt taken! retrying... (Attempt #%s)", iternum)
        salt = os.urandom(salt_len)
        iternum += 1
    return salt


def hmac(psw, salt, method=HASH_METHOD, iter=ROUNDS, length=LEN):
    return binascii.hexlify(hashlib.pbkdf2_hmac(method, psw, salt, iter, length))


# Wrap function from https://pymorton.wordpress.com/2015/02/16/wrap-integer-values-to-fixed-range/
def wrap(minimum, maximum, val):
    return (val - minimum) % (maximum - minimum + 1) + minimum


def is_prime_openssl(n):
    return subprocess.check_output(['openssl', 'prime', str(n)]).endswith('is prime\n')


def get_primes(salt, minimum=2**PRIME_RANGE[0], maximum=2**PRIME_RANGE[1], mult=CHUNK_SIZE):
    prime_start = wrap(minimum, maximum, mult*sum([ord(i) for i in salt]))
    primes = []
    cryptLog.info("Generating primes... (this may take a second)")
    while len(primes) < 2:
        if is_prime_openssl(prime_start):
            primes.append(prime_start)
            # print (prime_start)
        prime_start += 1
    cryptLog.info("Got primes with bit-length of %s", primes[0].bit_length())
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

    def encrypt_p(self, key, clear, seed=0):
        enc = psw_encrypt(clear, key, seed=seed)
        return [self.encrypt_n(i) for i in enc]

    def decrypt_p(self, key, enc, seed=0):
        enc = [self.decrypt_n(i) for i in enc]
        return psw_decrypt(enc, key, seed=seed)

    def decrypt(self, ciphertext):
        key, n = self.private
        # get hex val of int, ignore first 3 bytes ('0x1') and interpret the rest as text.
        # print ([hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext])
        try:
            split_str = [hex(self.decrypt_n(i)).strip("L")[3:] for i in ciphertext]
            return binascii.unhexlify("".join(split_str))
        except:
            rsaGenLog.exception("decrypt() Got malformed ciphertext. Is chunk size from encrypt() too large?")

    def decrypt_n(self, num):
        key, n = self.private
        return pow(num, key, n)

    def generate_keypair(self):
        rsaGenLog.info("Generating keypair from p & q")
        p, q = self.p, self.q
        # I've chosen 512-bit+ primes with openssl. Checking for primes would take too long, and is redundant.
        #if not (is_prime(p) and is_prime(q)):
        #    raise ValueError('Both numbers must be prime.')
        if p == q:
            raise ValueError('p and q cannot be equal')
        n = p * q
        phi = (p - 1) * (q - 1)
        e = random.randrange(1, phi)  # Can be seeded! :(

        g = gcf(e, phi)
        while g != 1:
            e = random.randrange(1, phi)  # Can be seeded too! :(
            g = gcf(e, phi)

        d = multiplicative_inverse(e, phi)

        self.private = (d, n)
        self.public = (e, n)
        rsaGenLog.info("Done generating keypair!")
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


def psw_decrypt(ciphertext, psw, seed=0, psw_chunk_size=32):
    random.seed(ord(psw[0]) if seed == 0 else seed)
    psw_hex = [int(i, 0) for i in split(binascii.hexlify(psw), psw_chunk_size - 1, '0x1')]
    psw_sum = sum([ord(i) for i in psw])
    split_str = [hex((i-psw_sum)/random.choice(psw_hex)).strip("L")[3:] for i in ciphertext]
    try:
        return binascii.unhexlify("".join(split_str))
    except:
        cryptLog.exception('psw_decrypt failed. Is chunk size from psw_encrypt too large? Invalid passcode?')
        return ""


def psw_encrypt(plaintext, psw, seed=0, chunk_size=32, psw_chunk_size=32):
    random.seed(ord(psw[0]) if seed == 0 else seed)
    psw_sum = sum([ord(i) for i in psw])
    psw_hex = [int(i, 0) for i in split(binascii.hexlify(psw), psw_chunk_size - 1, '0x1')]
    return [int(i, 0)*random.choice(psw_hex)+psw_sum
            for i in split(binascii.hexlify(plaintext), chunk_size - 1, '0x1')]
