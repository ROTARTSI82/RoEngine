# -*- coding: UTF-8 -*-

import itertools
import math
import sys

#__all__ = ['factorize', 'is_prime', 'is_perfect', 'prime_factorize',
#           'lcm', 'gcf', 'reduce_frac', 'Fraction', 'MixedNumber']

if sys.version_info.major == 3:
    xrange = range
    raw_input = input


def factorize(n):
    sign = "-" if n < 0 else "+"
    factors = [n, ]
    if sign == "-":
        factors.append(-n)
    for i in range(1, abs(n)+1):
        if i in factors:
            break
        if abs(n) % i == 0:
            factors.append(i)
            if sign == '-':
                factors.append(-i)
    return sorted(factors)


def is_perfect(n):
    fc = factorize(n)
    fc.remove(n)
    return sum(fc) == n


def prime_factorize(n):
    prime_factors = []
    if n < 0:
        prime_factors.append(-1)
        n = abs(n)
    for i in itertools.chain([2], itertools.count(3, 2)):
        if n <= 1:
            break
        while n % i == 0:
            n //= i
            prime_factors.append(i)
    return prime_factors


def lcm(*args):
    if len(args) == 2:
        return args[0] * args[1] // gcf(*args)
    else:
        lcmi = args[0]
        for i in args[1:]:
            lcmi = lcm(lcmi, i)
        return lcmi


def gcf(*args):
    args = list(args)
    if len(args) == 2:
        while args[1]:
            args[0], args[1] = args[1], args[0] % args[1]
        return args[0]
    else:
        igcf = args[0]
        for i in args[1:]:
            igcf = gcf(igcf, i)
        return igcf


def is_prime(n):
    if n < 3 or n % 2 == 0:
        return n == 2
    else:
        for i in range(3, int(n ** 0.5 + 2), 2):
            if n % i == 0:
                return False
        return True


def is_golden(a, b):
    g = float(max(a, b))
    l = float(min(a, b))
    return g / l, (g + l) / g


def find_golden(x):
    while True:
        yield x
        x = math.sqrt(1 + x)


def find_fib(n, phi=(5 ** 0.5 * 0.5 + 0.5)):
    return ( phi ** n - (1-phi) ** n ) / math.sqrt(5)


def gen_fib():
    yield 1
    yield 1
    a, b = 1, 1
    while True:
        y = a + b
        a = b
        b = y
        yield y


def get_cyclops(n, base=10, add=1):
    return base ** (2 * n + add) - base ** n - 1


DECIMAL_CHR = '.'
MAX_PRECISION = float('inf')
def to_base(n, base=2, exp='str(%s)'):  # Use exp=chr(%s) for base256
    suffix = ""
    schr = eval(exp % '0')
    if n == 0:
        return schr
    prefix = '+' if n >= 0 else '-'
    digits = ''
    n = abs(n)

    dec = n - int(n)
    dec_digits = ""
    place = -1
    iternum = 0
    while dec > 0 and iternum < MAX_PRECISION:
        digit = min(int(dec / base ** place), base-1)  # How many times could we fit without going over?
        dec_digits += eval(exp % 'digit')
        dec -= base ** place * digit
        iternum += 1
        place -= 1
    if dec_digits:
        suffix = DECIMAL_CHR + dec_digits.rstrip(schr)

    n = int(n)
    numdigits = 0
    while n - base ** numdigits > 0:
        numdigits += 1
    while n > 0 or numdigits >= 0:
        digit = n / base ** numdigits
        n -= digit * base ** numdigits
        digits += eval(exp % 'digit')
        numdigits -= 1
    return prefix + digits.lstrip(schr) + suffix


def from_base(n, base=2, exp='int(%s)'):  # Use exp=ord(%s) for base256
    ret = 0
    isNegative = False
    n = n.split(DECIMAL_CHR)
    if len(n) > 2:
        raise ValueError("Invalid format: more than 1 decimal point.")
    if len(n) > 1:
        dec = n[1]
        place = -1
        for i in dec:
            ret += base ** place * eval(exp % 'i')
            place -= 1
    n = n[0]
    if n.startswith('+'):
        n = n[1:]
    if n.startswith('-'):
        n = n[1:]
        isNegative = True
    for i, v in enumerate(reversed(n)):
        ret += base ** i * eval(exp % 'v')
    return ret if not isNegative else -ret


b256_dec = lambda x: from_base(x, 256, 'ord(%s)')
b256_enc = lambda x: to_base(x, 256, 'chr(%s)')


def are_relatively_prime(a, b):
    for n in range(2, min(a, b) + 1):
        if a % n == b % n == 0:
            return False
    return True


def wrap(minimum, maximum, val):
    return (val - minimum) % (maximum - minimum + 1) + minimum


def reduce_frac(num, dom):
    if num == 0:
        return 0, 1
    n1pf = prime_factorize(num)
    n2pf = prime_factorize(dom)
    n2Copy = n2pf[:]
    for i in n2Copy:
        if i in n1pf:
            n2pf.remove(i)
            n1pf.remove(i)
    num = 1
    dom = 1
    for i in n2pf:
        dom *= i
    for i in n1pf:
        num *= i
    return num, dom


def to_whole(a, b):
    a = float(a)
    b = float(b)
    while not (int(a) == a and int(b) == b):
        a *= 10
        b *= 10
    return int(a), int(b)


class Fraction(object):
    def __init__(self, num, denom):
        self.num, self.denom = to_whole(num, denom)
        self.decimal = num / float(denom)
        self.reduce()

    def reduce(self):
        self.num, self.denom = reduce_frac(self.num, self.denom)

    def __add__(self, other):
        lcmi = lcm(self.denom, other.denom)
        self_multiplier = lcmi / float(self.denom)
        other_multiplier = lcmi / float(other.denom)
        other.num *= other_multiplier
        self.num *= self_multiplier
        other.reduce()
        self.reduce()
        return Fraction(other.num + self.num, lcmi)

    def __sub__(self, other):
        lcmi = lcm(self.denom, other.denom)
        self_multiplier = lcmi / float(self.denom)
        other_multiplier = lcmi / float(other.denom)
        other.num *= other_multiplier
        self.num *= self_multiplier
        other.reduce()
        self.reduce()
        return Fraction(self.num - other.num, lcmi)

    def __mul__(self, other):
        return Fraction(self.num * other.num, other.denom * self.denom)

    def __str__(self):
        return str(self.num) + "/" + str(self.denom)

    def __div__(self, other):
        return self.__mul__(Fraction(other.denom, other.num))


class MixedNumber(object):
    def __init__(self, whole, num, denom, sign="+"):
        self.fraction = Fraction(num, denom)
        self.whole = whole
        self.sign = sign
        if sign == "-":
            self.whole = -whole
            self.fraction = Fraction(0, 1) - self.fraction
        self.reduce()

    def to_improper(self):
        # print self
        self.fraction.num += self.whole * self.fraction.denom
        self.whole = 0
        return self

    def reduce(self):
        frac = self.fraction + Fraction(self.whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) // abs(frac.denom)
        frac.num = abs(frac.num) % abs(frac.denom)
        # self.__init__(abs(whole), abs(frac.num), abs(frac.denom), sign)
        self.fraction = Fraction(abs(frac.num), abs(frac.denom))
        self.whole = abs(whole)
        self.sign = sign
        if sign == "-":
            self.whole = -whole
            self.fraction = Fraction(0, 1) - self.fraction
        return self

    def __add__(self, other):
        frac = other.fraction + self.fraction
        whole = self.whole + other.whole
        frac += Fraction(whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) // abs(frac.denom)
        frac.num = abs(frac.num) % abs(frac.denom)
        return MixedNumber(abs(whole), abs(frac.num), abs(frac.denom), sign)

    def __sub__(self, other):
        frac = self.fraction - other.fraction
        whole = self.whole - other.whole
        frac += Fraction(whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) // abs(frac.denom)
        frac.num = abs(frac.num) % abs(frac.denom)
        return MixedNumber(abs(whole), abs(frac.num), abs(frac.denom), sign)

    def __mul__(self, other):
        self.to_improper()
        other.to_improper()
        frac = self.fraction * other.fraction
        res = MixedNumber(0, abs(frac.num), abs(frac.denom), "-" if frac.decimal < 0 else "+")
        res.reduce()
        return res

    def __div__(self, other):
        self.to_improper()
        other.to_improper()
        frac = self.fraction / other.fraction
        res = MixedNumber(0, abs(frac.num), abs(frac.denom), "-" if frac.decimal < 0 else "+")
        res.reduce()
        return res

    def __str__(self):
        return "%s %s" % (self.whole, self.fraction)


if __name__ == "__main__":
    while True:
        inp = raw_input(">>>")
        try:
            print(eval(inp))
        except:
            exec (inp)
