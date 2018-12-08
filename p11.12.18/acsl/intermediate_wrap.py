# -*- coding: UTF-8 -*-

ALPH = [chr(i) for i in range(65, 65+26)]  # Capital letters A-Z

def get_num(chr):
    return ord(chr) - 64

def get_chr(num):
    return chr(num+64)

def encode(string):
    num_repr = [get_num(i) for i in string if i in ALPH]  # Checks if the character is in the alphabet
    ret_repr = []
    for i in num_repr:
        v = i
        if 1 <= v <= 5:  # Range A-E
            v *= 2
            ret_repr.append(v)
            continue
        if 6 <= v <= 10:  # Range F-J
            v = int(v % 3) * 5
            ret_repr.append(v)
            continue
        if 11 <= v <= 15:  # Range K-O
            v = int(v / 4) * 8
            ret_repr.append(v)
            continue
        if 16 <= v <= 20:  # Range P-T
            v = sum_digits(v) * 10
            ret_repr.append(v)
            continue
        if 21 <= v <= 26:  # Range U-Z
            v = get_largest_factor(v) * 12
            ret_repr.append(v)
            continue
    final = []
    for i, v in enumerate(ret_repr):
        if i == 0:
            final.append(wrap(1, 26, v+1))  # Count i from 'A'
        else:
            final.append(wrap(1, 26, v+final[i-1]))  # Count i from last char
    return "".join([get_chr(i) for i in final])


def wrap(minimum, maximum, val):
    if minimum <= val <= maximum:
        return val
    while val > maximum:
        val -= maximum
    while val < minimum:
        val = maximum-(minimum-val)
    return val


def sum_digits(v):
    return sum([int(i) for i in str(v)])

def get_largest_factor(v):
    return factorize(v)[-2]

def factorize(n):
    sign = "-" if n < 0 else "+"
    factors = [n, ]
    if sign == "-":
        factors.append(-n)
    for i in range(1, abs(n) + 1):
        if i in factors:
            break
        if abs(n) % i == 0:
            factors.append(i)
            factors.append(abs(n) / i)
            if sign == '-':
                factors.append(-i)
    return sorted(list(set(factors)))  # Remove Duplicates and sort


while True:
    print (encode(raw_input(">> ")))
