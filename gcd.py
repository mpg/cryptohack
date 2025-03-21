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
        # Use d for what the paper calls t1,
        # because t1 will be used for something else in Alg 8.
        d = v - u
        if u & 1 == 0:
            u >>= 1
            v, u = max_min(u, d)
        elif v & 1 != 0:
            d >>= 1
            v, u = max_min(d, u)
        else:
            v >>= 1
            v, u = max_min(v, d)

    return v


# [Jin23] "SICT-GCD can be easily obtained by removing
# the computations of q and r from Algorithm 8."
def sict_gcd(p, a):
    assert p >= a >= 0
    assert p & 1 != 0 or a & 1 != 0

    u, v = a, p
    for _ in range(2 * p.bit_length()):
        s, z = u & 1, v & 1
        t1 = (s ^ z) * v + (2 * s * z - 1) * u
        t2 = (s * v + (2 - 2 * s - z) * u) >> 1

        # In real life, use constant-time conditional assign/swap
        if t2 >= t1:
            u, v = t1, t2
        else:
            u, v = t2, t1

    return v


# return a if !cond; b if cond
#
# Usage: a = select(a, b, cond) to emulate a conditional assign
# (as implemented by mbedtls_mpi_core_cond_assign()).
def select(a, b, cond):
    if cond:
        return b
    return a


# return a, b if !cond; b, a if cond
#
# See mbedtls_mpi_core_cond_swap()
def cond_swap(a, b, cond):
    if cond:
        return b, a
    return a, b


# The computation of t1 and t2 in the above has drawabacks:
# 1. Not exactly readable.
# 2. Involves signed numbers (eg in t1 if sz is 0 we add -u).
# Constant time addition is costly (need to compute both x+y and x-y),
# not to mention we haven't implemented it and would rather not.
#
# The paper gives an alternative formula:
#   t1 = s*z*u ^ ((1-s) + (1-z))*(v − u)
#   2*t2 = s*z*(v − u) ^ s*(1-z)*v ^ (1-s)*z*u
# This alternative avoids the use of signed addition,
# but it is not more readable.
#
# Let's try a readable version, directly derived from si_gcd() above,
# and using constant-time primitives we have in tf-psa-crypto.
def sict_gcd2(p, a):
    assert p >= a >= 0
    assert p & 1 != 0 or a & 1 != 0

    u, v = a, p
    for _ in range(2 * p.bit_length()):
        d = v - u

        # s, z in Alg 8 - used meaningful names instead
        u_is_odd, v_is_odd = u & 1 != 0, v & 1 != 0

        # t1 from Alg 8, ie the thing that's kept unshifted
        t1 = d
        t1 = select(t1, u, u_is_odd and v_is_odd)

        # t2 from Alg 8, it the thing that gets shifted
        t2 = u
        t2 = select(t2, d, u_is_odd and v_is_odd)
        t2 = select(t2, v, u_is_odd and not v_is_odd)
        t2 >>= 1

        lt = t2 < t1  # IRL, use mbedtls_mpi_core_lt_ct
        u, v = cond_swap(t1, t2, lt)

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


if __name__ == "__main__":
    test(euclid_gcd, "euclid_gcd")
    test(binary_gcd, "binary_gcd")
    test_ordered_odd(si_gcd, "si_gcd")
    test_ordered_odd(sict_gcd, "sict_gcd")
    test_ordered_odd(sict_gcd2, "sict_gcd2")

    print(math.gcd(66528, 52920))
