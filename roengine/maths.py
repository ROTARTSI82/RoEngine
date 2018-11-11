# -*- coding: UTF-8 -*-

__all__ = ['factorize', 'gen_primes', 'is_prime', 'is_perfect', 'gen_perfect', 'prime_factorize',
           'lcm', 'gcf', 'reduce_frac', 'Fraction']


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


def gen_primes(start, stop):
    primes = []
    for i in range(start, stop):
        if is_prime(i):
            primes.append(i)
    return primes


def is_prime(n):
    return factorize(n) == [1, n]


def is_perfect(n):
    fc = factorize(n)
    fc.remove(n)
    return sum(fc) == n


def gen_perfect(start, stop):
    perfects = []
    for i in range(start, stop):
        if is_perfect(i):
            perfects.append(i)
    return perfects


def prime_factorize(n):
    i = 2
    pFactors = [] if n > -1 else [-1,]
    n = abs(n)
    while i <= n:
        if is_prime(i):
            while n % i == 0:
                pFactors.append(i)
                n = n/float(i)
        i += 1
    return sorted(pFactors)


def lcm(*args):
    if len(args) == 2:
        n1pf = prime_factorize(args[0])
        n2pf = prime_factorize(args[1])
        for i in n2pf:
            if i in n1pf:
                n1pf.remove(i)
        lcmi = 1
        for i in n2pf + n1pf:
            lcmi *= i
        return lcmi
    else:
        lcmi = args[0]
        for i in args:
            lcmi = lcm(lcmi, i)
        return lcmi


def gcf(*args):
    multList = []
    if len(args) == 2:
        n1pf = prime_factorize(args[0])
        n2pf = prime_factorize(args[1])
        for i in n2pf:
            if i in n1pf:
                n1pf.remove(i)
                multList.append(i)
        gcfi = 1
        for i in multList:
            gcfi *= i
        return gcfi
    else:
        gcfi = args[0]
        for i in args:
            gcfi = gcf(gcfi, i)
        return gcfi


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

    def to_improper(self):
        # print self
        self.fraction.num += self.whole * self.fraction.denom
        self.whole = 0
        # print self

    def reduce(self):
        frac = self.fraction + Fraction(self.whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) / abs(frac.denom)
        frac.num = abs(frac.num) % abs(frac.denom)
        self.__init__(abs(whole), abs(frac.num), abs(frac.denom), sign)
        return self

    def __add__(self, other):
        frac = other.fraction + self.fraction
        whole = self.whole + other.whole
        frac += Fraction(whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) / abs(frac.denom)
        frac.num = abs(frac.num) % abs(frac.denom)
        return MixedNumber(abs(whole), abs(frac.num), abs(frac.denom), sign)

    def __sub__(self, other):
        frac = self.fraction - other.fraction
        whole = self.whole - other.whole
        frac += Fraction(whole, 1)

        sign = "+"
        if frac.decimal < 0:
            sign = '-'
        whole = abs(frac.num) / abs(frac.denom)
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
            exec inp
