# -*- coding: UTF-8 -*-

"""
Expirement with this stuff :)
"""

from __future__ import print_function
from roengine.crypto import RSAGenerator

import hashlib
import hmac as hmac_module
import traceback
import binascii
import os
import subprocess

import pprint
import marshal

import sys
if sys.version_info.major == 3:
    raw_input = input
else:
    raw_input = raw_input  # Just makes PyCharm happy so that raw_input would always be definite.

SHOW_PASSDUMP = True
HASH_METHOD = 'sha512'
ROUNDS = 100000  # ~100,000 for sha256 as of 2013
SALT_LEN = 16  # 16 or more from os.urandom()
MAX_PASS = 1024
LEN = 64  # 64 default for sha256


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
            return ""
        rsa = RSAGenerator(0, 0, 256, False)
        rsa.public, rsa.private = self.users[user][3]
        return rsa.decrypt_p(psw, self.users[user][2])

    def dec(self, data, user, psw):
        if user not in self.users:
            return ""
        rsa = RSAGenerator(0, 0, 256, False)
        rsa.public, rsa.private = self.users[user][3]
        return rsa.decrypt_p(psw, data)

    def enc(self, dat, user, psw):
        if user not in self.users:
            return []
        rsa = RSAGenerator(0, 0, 256, False)
        rsa.public, rsa.private = self.users[user][3]
        return rsa.encrypt_p(psw, dat)

    def write(self, dat, user, psw):
        if user not in self.users:
            return []
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

    def read_data(self, psw):
        # print (self.current_user, self.psw)
        return self.acc_manager.read(self.current_user, psw)

    def enc_data(self, data, psw):
        return self.acc_manager.enc(data, self.current_user, psw)

    def dec_data(self, data, psw):
        return self.acc_manager.dec(data, self.current_user, psw)

    def write_data(self, data, psw):
        # print (self.current_user, self.psw)
        return self.acc_manager.write(data, self.current_user, psw)


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
            print (prime_start)
        prime_start += 1
    return primes


my_acc_m = AccountManager()
# my_acc_m.make_guest_account()
# my_user = User(my_acc_m)

# print (my_acc_m.new_acc("john.doe@example.com", "l3tm31n!"))
# print (my_acc_m.new_acc("jane-doe@gmail.org", "p@ssw0rd&&"))

with open('users.dat') as fp:
    my_acc_m.users.update(marshal.load(fp))

# print (my_user.login("john.doe@example.com", "l3tm31n!"))
# print (my_user.write_data("Hello World! I'm John Doe!"))

# print (my_user.login("jane-doe@gmail.org", "p@ssw0rd&&"))
# print (my_user.write_data("Hello World! I'm Jane!"))

# user2 = User(my_acc_m)
# print (user2.read_data())
# (user2.login("john.doe@example.com", "l3tm31n!"))
# print (user2.read_data())

# (user2.login("jane-doe@gmail.org", "p@ssw0rd&&"))
# print (user2.read_data())

com_user = User(acc_manager=my_acc_m)

while True:
    command = raw_input(">? ").split(" ")
    if command[0] == "exit":
        break
    if command[0] == 'encfile':
        with open(command[1], 'r') as fp:
            dat = com_user.enc_data(fp.read(), command[2])
        with open(command[1]+'.encrypted', 'w') as fp:
            marshal.dump(dat, fp)
    if command[0] == 'readfile':
        with open(command[1], 'r') as fp:
            dat = marshal.load(fp)
        print (com_user.dec_data(dat, command[2]))
    if command[0] == 'logout':
        com_user.logout()
    if command[0] == 'read':
        print (com_user.read_data(com_user.psw))
    if command[0] == 'write':
        try:
            com_user.write_data(" ".join(command[1:]), com_user.psw)
            print ("Wrote:", " ".join(command[1:]))
        except IndexError:
            print ("Err: `write` take 1 param: [msg]")
    if command[0] == 'login':
        try:
            suc=com_user.login(command[1], command[2])
            if suc:
                print ("Success! Logged in.")
            if suc is 0:
                print ("Invalid Username")
            elif suc is False:
                print ("Invalid Password")
        except IndexError:
            print ("Err: `login` takes 2 params: [user] [psw]")
    if command[0] == 'newacc':
        try:
            my_acc_m.new_acc(command[1], command[2])
        except IndexError:
            print ("Err: `newacc` takes 2 params: [user] [psw]")
    if command[0] == 'py':
        try:
            eval(" ".join(command[1:]))
        except:
            try:
                exec (" ".join(command[1:]))
            except:
                traceback.print_exc()
    if command[0] == 'rm':
        try:
            del my_acc_m.users[command[1]]
        except KeyError:
            print (command[1], 'doesn\'t exist')
        except IndexError:
            print ('Err: `rm` takes 1 param: [user]')
    if command[0] == 'save':
        with open("users.dat", 'w') as fp:
            marshal.dump(my_acc_m.users, fp)
    if command[0] == 'clear':
        my_acc_m.users = {}
        com_user.logout()
    if command[0] == 'users':
        pprint.pprint(my_acc_m.users)
    if command[0] == 'myacc':
        print ('User:', com_user.current_user)
        print ('Password:', com_user.psw)
    if command[0] == 'load':
        with open('users.dat') as fp:
            my_acc_m.users.update(marshal.load(fp))

with open("users.dat", 'w') as fp:
    marshal.dump(my_acc_m.users, fp)

pprint.pprint(my_acc_m.users)
