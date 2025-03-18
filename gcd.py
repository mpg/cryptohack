import math
import secrets

# Useful properties:
# 1. gcd(a, 0) = a
# 2. gcd(a, a) = a
# 3. gcd(a, b) = gcd(b, a)
# 4. gcd(a, b) = gcd(a, b - a)
#       if d divides a and b, it also divides b - a
#       if d divides a and b - a, it also divdes a + (b-a) = b
# 5. gcd(a, b) = gcd(a, b - n*a) for any integer n
#       iterated version of the above
# 6. gcd(a, b) = gcd(a, b % a)
#       b % a is b - n*a for some n
# 7. gcd(a, b) = 2 * gcd(a / 2, b / 2) if a and b both even
#       factor 2 in common
# 8. gcd(a, b) = gcd(a, b / 2) if a odd and b even
#       the factors 2 in b can't contribute to the GCD since a is odd


# https://en.wikipedia.org/wiki/Euclidean_algorithm
def euclid_gcd(a, b):
    assert a >= 0 and b >= 0

    if b > a:
        a, b = b, a

    # Invariant: a_i >= b_i and gcd(a_i, b_i) = gcd(a_{i-1}, b_{i-1})
    # Variant: a_i < a_{i-1}
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

    # Invariants:
    # gcd(a_i, b_i) = gcd(a_{i-1}, b_{i-1})
    # a_i and b_i both odd (except possibly first iteration)
    # Variant: bitlen(a) decreasing (except possibly first iteration)
    while a != b:
        if b > a:
            a, b = b, a

        a -= b
        while a & 1 == 0:
            a >>= 1

    return g * a


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


test(euclid_gcd, "euclid_gcd")
test(binary_gcd, "binary_gcd")

print(math.gcd(66528, 52920))
