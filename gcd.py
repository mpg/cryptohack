import math
import secrets

# Useful properties:
# 1. gcd(a, 0) = a
# 2. gcd(a, a) = a
# 3. gcd(a, b) = gcd(b, a)
# 4. gcd(a, b) = gcd(a, b - a)
# 5. gcd(a, b) = gcd(a, b - n*a) for any integer n
# 6. gcd(a, b) = gcd(a, b % a)
# 7. gcd(a, b) = 2 * gcd(a / 2, b / 2) if a and b both even
# 8. gcd(a, b) = gcd(a, b / 2) if a odd and b even


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

    if b > a:
        a, b = b, a
    if b == 0:
        return a

    # Invariant: g_i * gcd(a_i, b_i) = gcd(a, b)
    # Variant: bitlen(a) and bitlen(b) decreasing
    g = 1
    while a & 1 == 0 and b & 1 == 0:
        a >>= 1
        b >>= 1
        g <<= 1

    # Invariant: a_i >= b_i both odd, and gcd(a_i, b_i) = gcd(a_{i-1}, b_{i-1})
    # Variant: bitlen(a) decreasing
    while a != b:
        a -= b
        while a & 1 == 0:
            a >>= 1

        if b > a:
            a, b = b, a

    return g * a


def test(a, b):
    ref = math.gcd(a, b)
    euc = euclid_gcd(a, b)
    bnr = binary_gcd(a, b)
    assert ref == euc, f"{a} {b} -> {ref} != {euc}"
    assert ref == bnr, f"{a} {b} -> {ref} != {bnr}"


for a in range(10):
    for b in range(10):
        test(a, b)

for _ in range(100):
    a = secrets.randbits(256)
    b = secrets.randbits(256)
    test(a, b)

print(math.gcd(66528, 52920))
