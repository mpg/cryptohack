import math
import secrets

# Useful properties:
# 1. gcd(a, 0) = a
# 2. gcd(a, a) = a
# 3. gcd(a, b) = gcd(b, a)
# 4. gcd(a, b) = gcd(a, b - a)
#       if d divides a and b, it also divides b - a
#       if d divides a and b - a, it also divides a + (b-a) = b
# 5. gcd(a, b) = gcd(a, b - n*a) for any integer n
#       iterated version of the above
# 6. gcd(a, b) = gcd(a, b % a)
#       b % a is b - n*a for some n
# 7. gcd(a, b) = 2 * gcd(a / 2, b / 2) if a and b both even
#       factor 2 in common
# 8. gcd(a, b) = gcd(a, b / 2) if a odd and b even
#       the factors 2 in b can't contribute to the GCD since a is odd
#
# For the last two, it is useful to remember that if
# a = 2^e2 * 3^e3 * 5^e5 * 7^e7 * 11^e11 * ...
# b = 2^f2 * 3^f3 * 5^f5 * 7^f7 * 11^f11 * ...
# then GCD(a, b) = 2^g2 * 3^g3 * 5^g5 * ... where g_p = min(e_p, f_p).


# https://en.wikipedia.org/wiki/Euclidean_algorithm
def euclid_gcd(a, b):
    assert a >= 0 and b >= 0

    if b > a:
        a, b = b, a

    # Invariants:
    # gcd(a_i, b_i) = gcd(a_{i-1}, b_{i-1})
    # a_i, b_i non-negative
    # Variant: b_i < b_{i-1}
    # (It can be proven that the number of steps is O(bitlen(b)) though.)
    while b != 0:
        a, b = b, a % b

    return a


# https://en.wikipedia.org/wiki/Binary_GCD_algorithm
def binary_gcd(a, b):
    assert a >= 0 and b >= 0

    # Avoid special cases
    if a == 0:
        return b
    if b == 0:
        return a

    # Take out the factors 2 common to a and b
    g = 1
    while a & 1 == 0 and b & 1 == 0:
        a >>= 1
        b >>= 1
        g <<= 1

    # Take out the remaining factors 2 in a and b
    # These no longer contribute to the GCD since the other is odd
    while a & 1 == 0:
        a >>= 1
    while b & 1 == 0:
        b >>= 1

    # Invariants:
    # gcd(a_i, b_i) = gcd(a_{i-1}, b_{i-1})
    # a and b both odd and non-negative
    # Variant: bitlen(max(a, b)) decreasing at each iteration
    # (a and b are both odd, so a - b is even and there's at least one shift)
    while a != b:
        if b > a:
            a, b = b, a

        a -= b
        while a & 1 == 0:
            a >>= 1

    return g * a


# Algorithm 6 from [Jin23].
# This is a step towards constant-time GCD:
# - avoids nested loops;
# - the loop has a constant number of iterations;
# - the 3 branches in the loop's body are very similar to each other.
#
# However it only works if at least one of the inputs is odd;
# this is something we can guarantee in pratice in cases of interest.
# (Or we could prepend something like the first loop of binary_gcd() above.)
#
# [Jin23] https://www.jstage.jst.go.jp/article/transinf/E106.D/9/E106.D_2022ICP0009/_pdf
def si_gcd(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    def max_min(x, y):
        if x > y:
            return x, y
        return y, x

    u, v = b, a
    for _ in range(2 * a.bit_length()):
        print(v, u)
        t1 = v - u
        if u & 1 == 0:
            u >>= 1
            v, u = max_min(u, t1)
        elif v & 1 != 0:
            t1 >>= 1
            v, u = max_min(t1, u)
        else:
            v >>= 1
            v, u = max_min(v, t1)

    return v


def test_one(func, name, a, b):
    exp = math.gcd(a, b)
    got = func(a, b)
    assert got == exp, f"{name}({a}, {b}) = {got} != {exp}"


def test(func, name):
    for a in range(10):
        for b in range(10):
            test_one(func, name, a, b)

    for _ in range(100):
        a = secrets.randbits(256)
        b = secrets.randbits(256)
        test_one(func, name, a, b)


def test_ordered_odd(func, name):
    for a in range(20):
        for b in range(a + 1):
            if a & 1 != 0 or b & 1 != 0:
                test_one(func, name, a, b)

    for _ in range(100):
        while True:
            a = secrets.randbits(256)
            b = secrets.randbits(256)
            if a & 1 != 0 or b & 1 != 0:
                break
        test_one(func, name, max(a, b), min(a, b))


test(euclid_gcd, "euclid_gcd")
test(binary_gcd, "binary_gcd")
test_ordered_odd(si_gcd, "si_gcd")

print(math.gcd(66528, 52920))
