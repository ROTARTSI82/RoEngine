# -*- coding: UTF-8 -*-

from __future__ import print_function


class BaseNumber(object):
    def __init__(self, literal, base):
        self.str_n = literal.lstrip('0')
        self.b = base

    def copy(self):
        return BaseNumber(self.str_n, self.b)

    def add_digit(self, digit):
        self.str_n += digit

    def is_palindrome(self):
        return "".join(reversed(self.str_n)) == self.str_n

    def pop_last(self):
        ret = self.str_n[-1]
        self.str_n = self.str_n[:-1]
        return ret

    def reversed(self):
        return BaseNumber("".join(reversed(self.str_n)), self.b)

    def __add__(self, other):
        assert self.b == other.b
        self_rev = reversed(self.str_n)
        other_rev = reversed(other.str_n)
        const = ""
        carry_over = 0
        digit_add = 0
        sn_not_empty, on_not_empty = True, True
        while carry_over or sn_not_empty or on_not_empty:
            try:
                sn = int(self_rev.next())
            except StopIteration:
                sn_not_empty = False
                sn = 0
            try:
                on = int(other_rev.next())
            except StopIteration:
                on = 0
                on_not_empty = False
            digit_add = on + sn + carry_over
            carry_over = (digit_add - (digit_add % self.b)) / self.b
            digit_add %= self.b
            const = str(digit_add) + const
        return BaseNumber(const, self.b)


def make_palindrome(x):
    for i in range(10):
        if x.is_palindrome():
            return x.str_n
        x = x + x.reversed()
    return None, x.str_n

"""
ten = BaseNumber('1010', 2)  # 0b1010 == 10
two = BaseNumber('10', 2)  # 0b10 == 2

twelve = ten + two

print (twelve.str_n)  # 0b1100 == 12


1. 123, 6 1. 444
2. 43423, 5 2. 23344332
3. 110111, 2 3. 10011001
4. 566523, 7 4. 125404521
5. 43427, 9 5. NONE, 1217685622

1. 87, 10 1. 4884
2. 1211, 3 2. 112211
3. 3112 ,4 3. 233332
4. 196, 10 4. NONE, 18211171


YAY! Passes all unit tests.
"""

test_cases = {
    ('123', 6): '444',
    ('43423', 5): '23344332',
    ('110111', 2): '10011001',
    ('566523', 7): '125404521',
    ('43427', 9): (None, '1217685622'),

    ('87', 10): '4884',
    ('1211', 3): '112211',
    ('3112', 4): '233332',
    ('196', 10): (None, '18211171')
}

num_success = 0

for key, value in zip(test_cases.keys(), test_cases.values()):
    print ("=================[NEW CASE]=================")
    print (key, value)
    success = (make_palindrome(BaseNumber(*key)) == value)
    if success: num_success += 1
    print (success)
    print ()

print ("Score:", str(num_success)+"/"+str(len(test_cases)))
