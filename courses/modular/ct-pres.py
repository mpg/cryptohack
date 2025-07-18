import math
import secrets

# Useful properties:
# gcd(a, 0) = a
# gcd(a, b) = gcd(a, b - a)
#    if d divides a and b, it also divides b - a
#    if d divides a and b - a, it also divides a + (b-a) = b
# gcd(a, b) = 2 * gcd(a / 2, b / 2) if a and b both even
#    factor 2 in common
# gcd(a, b) = gcd(a, b / 2) if a odd and b even
#    the factors 2 in b can't contribute to the GCD since a is odd
#
# For the last two, it is useful to remember that if
# a = 2^e2 * 3^e3 * 5^e5 * 7^e7 * 11^e11 * ...
# b = 2^f2 * 3^f3 * 5^f5 * 7^f7 * 11^f11 * ...
# then GCD(a, b) = 2^g2 * 3^g3 * 5^g5 * ... where g_p = min(e_p, f_p).
#
# For all the algorithms here, we're going to assume at least one
# of a, b is odd - that way we know there's no factor 2 in the GCD.


# "Classical" binary GCD - just the core loop after we've removed factors 2.
def binary_gcd(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    # (Normally we'd have a first loop here to handle factors 2.)

    while a != 0 and b != 0:  # Problem 1: outer while loop
        while a & 1 == 0:  # Problem 2: inner while loops
            a >>= 1
        while b & 1 == 0:
            b >>= 1

        if a > b:  # Problem 3: if branches
            a -= b
        else:
            b -= a

    return max(a, b)  # Problem 3: if branches


# Emulate mbedtls_mpi_core_cond_swap()
def cond_swap(a, b, cond):
    if cond:
        return b, a
    return a, b


# Emulate mbedtls_mpi_core_cond_assign())
def select(a, b, cond):
    if cond:
        return b
    return a


# Fix the 3rd problem (if branches)
def bin_gcd_fix3(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    while b != 0:  # Problem 1: outer while loop
        while a & 1 == 0:  # Problem 2: inner while loops
            a >>= 1
        while b & 1 == 0:
            b >>= 1

        swap = a > b  # IRL use mbedtls_mpi_core_lt
        a, b = cond_swap(a, b, swap)
        b -= a

    return select(a, b, a == 0)  # IRL use constant-time ==


# Fix the first problem (outer while loop)
def bin_gcd_fix13(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    # IRL take a public upper bound for bitlen(a) as an argument
    nb_iter = a.bit_length()
    for _ in range(nb_iter):
        while a & 1 == 0 and a != 0:  # Problem 2: inner while loops
            a >>= 1
        while b & 1 == 0 and b != 0:
            b >>= 1

        swap = b > a
        a, b = cond_swap(a, b, swap)
        a -= b

    return select(a, b, a == 0)


# Fix the 2nd problem (inner while loop)
def bin_gcd_fix12(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    nb_iter = a.bit_length() * 3  # notice factor 3
    for _ in range(nb_iter):
        # Re-introduces problem 3 (if branches) temporarily
        if a & 1 == 0:
            a >>= 1
        elif b & 1 == 0:
            b >>= 1
        else:
            a, b = cond_swap(a, b, b > a)
            a -= b

    return select(a, b, a == 0)


# Fix all 3 problems (but performance is not great)
def bin_gcd_fix123(a, b):
    assert a >= b >= 0
    assert a & 1 != 0 or b & 1 != 0

    nb_iter = a.bit_length() * 3  # factor 3 is still bad for performance
    for _ in range(nb_iter):
        shift_a = a & 1 == 0
        a = select(a, a >> 1, shift_a)

        shift_b = b & 1 == 0
        b = select(b, b >> 1, shift_b)

        subtract = not shift_a and not shift_b
        a, b = cond_swap(a, b, b > a and subtract)
        a = select(a, a - b, subtract)
        # Each iteration does 2 shifts, 1 subtract and 1 compare

    return select(a, b, a == 0)


# Algorithm 6 from [Jin23].
# This is a step towards constant-time GCD:
# - avoids inner loop (fixes problem 2);
# - the (outer) loop has a constant number of iterations (fixes problem 1);
# - the 3 branches in the loop's body are very similar to each other
#   (step towards fixing problem 3 efficiently).
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
    for _ in range(2 * a.bit_length()):  # Notice factor 2 only
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
        # Each iteration does 1 shift, 1 subtract, 1 compare

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

        u, v = cond_swap(t1, t2, t2 < t1)

    return v


# The computation of t1 and t2 in the above has drawbacks:
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
def sict_gcd_readable(p, a):
    assert p >= a >= 0
    assert p & 1 != 0 or a & 1 != 0

    u, v = a, p
    for _ in range(2 * p.bit_length()):
        # s, z in Alg 8 - use meaningful names instead
        u_is_odd, v_is_odd = u & 1 != 0, v & 1 != 0

        d = v - u

        # t1 from Alg 8, ie the thing that's kept unshifted
        t1 = d
        t1 = select(t1, u, u_is_odd and v_is_odd)

        # t2 from Alg 8, ie the thing that gets shifted
        t2 = u
        t2 = select(t2, d, u_is_odd and v_is_odd)
        t2 = select(t2, v, u_is_odd and not v_is_odd)
        t2 >>= 1

        u, v = cond_swap(t1, t2, t2 < t1)

    return v


# Compute x * 2^-1 mod n, ie x / 2 mod n (assuming n is odd)
def div2_mod(x, n):
    even_x = select(x, x + n, x & 1 != 0)
    return even_x >> 1


# Compute x - y mod n, result in [0, n)
def sub_mod(x, y, n):
    larger_x = select(x, x + n, x < y)
    return larger_x - y


# "Classical" binary modinv
def bin_modinv(a, n):
    assert n >= a > 0
    assert n & 1 != 0

    # Invariants:
    # gcd(u, v) = gcd(a, n)
    # v = a * q mod n
    # u = a * r mod n
    u, v, q, r = a, n, 0, 1
    while u != 0 and v != 0:
        while u & 1 == 0:
            u >>= 1
            r = div2_mod(r, n)
        while v & 1 == 0:
            v >>= 1
            q = div2_mod(q, n)

        if u > v:
            u -= v
            r = sub_mod(r, q, n)
        else:
            v -= u
            q = sub_mod(q, r, n)

    # At this point one relation is 0 = a * 0 mod n
    # and the other is 1 = gcd(a, n) = a * a^-1 mod n (if a and n coprime)
    if u == 0:
        assert v == 1
        return q
    else:
        assert u == 1
        return r


# This is Algorithm 8 from [Jin23], except:
# - more readable
# - not using signed addition,
# - using constant-time primitives like those we have in tf-psa-crypto,
# - skipping an optimisation for now (see below).
#
# See also Alg 7, but t1, ..., t4 are those from Alg 8.
def sict_mi2(a, p):
    assert p >= a >= 0
    assert p & 1 != 0

    u, v, q, r = a, p, 0, 1
    for _ in range(2 * p.bit_length()):
        # s, z in Alg 8 - use meaningful names instead
        u_is_odd, v_is_odd = u & 1 != 0, v & 1 != 0

        # This is the same as sict_gcd_readable()
        d = v - u  # (t1 from Alg 7)
        t1 = d
        t1 = select(t1, u, u_is_odd and v_is_odd)
        t2 = u
        t2 = select(t2, d, u_is_odd and v_is_odd)
        t2 = select(t2, v, u_is_odd and not v_is_odd)
        t2 >>= 1

        # Do the same with q, r, t3, t4 (but decisions still based on u, v)
        d = sub_mod(q, r, p)  # (t2 from Alg 7)
        t3 = d
        t3 = select(t3, r, u_is_odd and v_is_odd)
        t4 = r
        t4 = select(t4, d, u_is_odd and v_is_odd)
        t4 = select(t4, q, u_is_odd and not v_is_odd)
        t4 = div2_mod(t4, p)

        lt = t2 < t1  # IRL, use mbedtls_mpi_core_lt_ct
        u, v = cond_swap(t1, t2, lt)
        r, q = cond_swap(t3, t4, lt)

    assert v == 1  # We also get the GCD for free
    return q


# Compute x * 2^-l mod n when l = 2 * bitlen(n) (assuming n is odd)
# In tf-psa-crypto this can be done with two Montgomery multiplications by 1,
# which is faster that the loop below.
def div2l_mod(x, n):
    for _ in range(2 * n.bit_length()):
        x = div2_mod(x, n)
    return x


# This is Algorithm 8 from [Jin23], except:
# - more readable
# - not using signed addition,
# - using constant-time primitives like those we have in tf-psa-crypto.
#
# See also Alg 7, but t1, ..., t4 are those from Alg 8.
def sict_mi(a, p):
    assert p >= a >= 0
    assert p & 1 != 0

    u, v, q, r = a, p, 0, 1
    for _ in range(2 * p.bit_length()):
        # s, z in Alg 8 - use meaningful names instead
        u_is_odd, v_is_odd = u & 1 != 0, v & 1 != 0

        d = v - u  # (t1 from Alg 7)
        t1 = d
        t1 = select(t1, u, u_is_odd and v_is_odd)
        t2 = u
        t2 = select(t2, d, u_is_odd and v_is_odd)
        t2 = select(t2, v, u_is_odd and not v_is_odd)
        t2 >>= 1

        # We should divide t4 by 2 but we're deferring that,
        # so to compensate we multiply t3 by 2
        # to scale them both the same way.
        d = sub_mod(q, r, p)  # (t2 from Alg 7)
        t3 = d
        t3 = select(t3, r, u_is_odd and v_is_odd)
        t3 = t3 * 2 % p
        t4 = r
        t4 = select(t4, d, u_is_odd and v_is_odd)
        t4 = select(t4, q, u_is_odd and not v_is_odd)

        lt = t2 < t1  # IRL, use mbedtls_mpi_core_lt_ct
        u, v = cond_swap(t1, t2, lt)
        r, q = cond_swap(t3, t4, lt)

    assert v == 1  # We also get the GCD for free
    return div2l_mod(q, p)  # Do the deferred divisions (more efficiently)


# Compute modular inverse modulo a number that's not odd but is 2 mod 4
# (ie, it's a multiple of 2 but not 4, ie the bottom two bits are 10).
def sict_mi_2mod4(a, n):
    assert 0 < a < n
    assert n % 4 == 2

    # Consider i = a^-1 mod n, ie such that a * i = 1 mod n.
    # That is, a*i = 1 + n*k = 1 + (n/2)*2k
    # Hence, a*i = 1 mod (n/2), ie i = a^-1 mod (n/2) as well.
    #
    # So, we can first compute i2 = a^-1 mod (n/2), and we know that
    # i = i2 mod (n/2), so lifting up mod n we have either
    # i = i2 mod n or i = i2 + (n/2) mod n.
    # Speficically, we can pick the one that's odd (since n is even,
    # only odd numbers are invertible mod n).

    n2 = n >> 1
    i2 = sict_mi(a % n2, n2)

    return select(i2, i2 + n2, i2 & 1 == 0)


# Compute a^-1 mod n where a is odd and n might be even, including
# a muliple of 2^k for arbitrary k. Requires a > 1 and n > 1.
#
# Since gcd(a, n) can only be 1 if at least one of a, n is odd,
# so whenever a^-1 mod n exists, it can be computed with one of
# sict_mi() (if n is odd, possibly reducing a mod n first to satisfy the
# ordering condition) or this function (otherwise).
def sict_mi_a_odd(a, n):
    assert a > 1
    assert n > 1

    # Compute n1 = n^-1 mod a
    n1 = sict_mi(n % a, a)
    # Now we know n * n1 = 1 + k * a for some k, which we can compute
    k = (n * n1 - 1) // a
    # Now we have a Bezout relation for (a, n): n * n1 - k * a = 1,
    # which is to say the inverse of a mod n is -k.
    #
    # We know k < n by this point because n1 < a;
    # also k is clearly non-negative and can't be zero.
    return n - k


def test_gcd_one(func, name, a, b):
    exp = math.gcd(a, b)
    got = func(a, b)
    assert got == exp, f"{name}({a}, {b}) = {got} != {exp}"


def test_gcd(func):
    name = func.__name__
    for a in range(20):
        for b in range(a + 1):
            if a & 1 != 0 or b & 1 != 0:
                test_gcd_one(func, name, a, b)

    for _ in range(100):
        while True:
            a = secrets.randbits(256)
            b = secrets.randbits(256)
            if a & 1 != 0 or b & 1 != 0:
                break
        test_gcd_one(func, name, max(a, b), min(a, b))

    for _ in range(10):
        a = secrets.randbits(1024)
        for b in range(10):
            aa = a | (1 - (b & 1))
            test_gcd_one(func, name, aa, b)


def test_mi_one(func, name, a, n):
    a1 = func(a, n)
    assert 0 <= a1 < n, f"{name}({a}, {n}) = {a1} not in range"
    assert a1 * a % n == 1, f"{name}({a}, {n}) = {a1} incorrect ({a1 * a % n})"


def test_mi(func):
    name = func.__name__
    for n in range(1, 22, 2):
        for a in range(1, n):
            if math.gcd(a, n) != 1:
                continue
            test_mi_one(func, name, a, n)

    for _ in range(100):
        while True:
            n = secrets.randbits(1024) | 1
            a = secrets.randbelow(n)
            if math.gcd(a, n) == 1:
                break
        test_mi_one(func, name, a, n)


def test_mi_2mod4():
    for n in range(1, 20):
        if n % 4 != 2:
            continue
        for a in range(1, n):
            if math.gcd(a, n) != 1:
                continue
            ai = sict_mi_2mod4(a, n)
            assert 0 <= ai < n
            assert (ai * a) % n == 1, f"{ai} * {a} mod {n} != 1"

    for _ in range(10):
        while True:
            n = (secrets.randbits(1022) << 2) | 2
            a = secrets.randbelow(n)
            if math.gcd(a, n) == 1:
                break
        ai = sict_mi_2mod4(a, n)
        assert 0 <= ai < n
        assert (ai * a) % n == 1, f"{ai} * {a} mod {n} != 1"


def test_mi_a_odd():
    for n in range(2, 20):
        for a in range(2, 20):
            if a % 2 == 0:
                continue
            if math.gcd(a, n) != 1:
                continue
            ai = sict_mi_a_odd(a, n)
            assert 0 < ai < n
            assert (ai * a) % n == 1, f"{ai} * {a} mod {n} != 1"

    for _ in range(10):
        while True:
            n = secrets.randbits(256)
            a = (secrets.randbits(256) << 1) | 1
            if math.gcd(a, n) == 1:
                break
        ai = sict_mi_a_odd(a, n)
        assert 0 < ai < n
        assert (ai * a) % n == 1, f"{ai} * {a} mod {n} != 1"

    for _ in range(10):
        while True:
            n = secrets.randbits(1024)
            a = (secrets.randbits(1023) << 1) | 1
            if math.gcd(a, n) == 1:
                break
        ai = sict_mi_a_odd(a, n)
        assert 0 < ai < n
        assert (ai * a) % n == 1, f"{ai} * {a} mod {n} != 1"


if __name__ == "__main__":
    test_gcd(binary_gcd)
    test_gcd(bin_gcd_fix3)
    test_gcd(bin_gcd_fix13)
    test_gcd(bin_gcd_fix12)
    test_gcd(bin_gcd_fix123)
    test_gcd(si_gcd)
    test_gcd(sict_gcd)
    test_gcd(sict_gcd_readable)

    test_mi(bin_modinv)
    test_mi(sict_mi2)
    test_mi(sict_mi)

    test_mi_2mod4()
    test_mi_a_odd()
