# -*- coding: UTF-8 -*-

__all__ = ['factorize', 'gen_primes', 'is_prime', 'is_perfect', 'gen_perfect', 'prime_factorize',
           'lcm', 'gcf', 'reduce_frac', 'Fraction']


def factorize(n):
    factors = [n, ]
    for i in range(1, n+1):
        if i in factors:
            break
        if n / float(i) == int(n / float(i)):
            factors.append(i)
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


class Fraction(object):
    def __init__(self, num, denom):
        self.num = num
        self.denom = denom
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
        return Fraction(other.num - self.num, lcmi)

    def __mul__(self, other):
        return Fraction(self.num * other.num, other.denom * self.denom)

    def __str__(self):
        return str(self.num) + "/" + str(self.denom)

    def __div__(self, other):
        return self.__mul__(Fraction(other.denom, other.num))


if __name__ == "__main__":
    while True:
        inp = raw_input(">>>")
        try:
            print(eval(inp))
        except:
            exec inp
