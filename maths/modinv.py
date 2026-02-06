import math
import secrets
import egcd
from gcd import select, cond_swap


# Compute a^-1 mod n using the Extended Euclidean Algorithm
def modinv_euclid(a, n):
    g, u, v = egcd.euclid_direct(a, n)
    assert g == 1
    u = (u % n + n) % n
    return u


# Compute a^-1 mod n using the Binary Extended Euclidean Algorithm
def modinv_binary(a, n):
    g, u, v = egcd.binary(a, n)
    assert g == 1
    u = (u % n + n) % n
    return u


# Compute x * 2^-1 mod n (assuming n is odd)
def div2_mod(x, n):
    if x & 1 == 0:
        return x >> 1
    return (x + n) >> 1


# Compute x * 2^-l mod n when l = 2 * bitlen(n) (assuming n is odd)
# In tf-psa-crypto this can be done with two Montgomery multiplications by 1.
def div2l_mod(x, n):
    for _ in range(2 * n.bit_length()):
        x = div2_mod(x, n)
    return x


# Compute x - y mod n, result in [0, n)
def sub_mod(x, y, n):
    if x < y:
        return x + n - y
    return x - y


# Compute x + y mod n, result in [0, n)
def add_mod(x, y, n):
    z = x + y
    if z > n:
        return z - n
    return z


# This is Algorithm 8 from [Jin23], except:
# - more readable
# - not using signed addition,
# - using constant-time primitives like those we have in tf-psa-crypto.
#
# See comments on sict_gcd2() in gcd.py.
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

        d = sub_mod(q, r, p)  # (t2 from Alg 7)
        t3 = d
        t3 = select(t3, r, u_is_odd and v_is_odd)
        t3 = add_mod(t3, t3, p)
        t4 = r
        t4 = select(t4, d, u_is_odd and v_is_odd)
        t4 = select(t4, q, u_is_odd and not v_is_odd)

        lt = t2 < t1  # IRL, use mbedtls_mpi_core_lt_ct
        u, v = cond_swap(t1, t2, lt)
        r, q = cond_swap(t3, t4, lt)

    assert v == 1  # We also get the GCD for free
    return div2l_mod(q, p)


def test_one(func, name, a, n):
    a1 = func(a, n)
    assert 0 <= a1 < n, f"{a1} not in range [0, {n}) ({name})"
    one = (a1 * a) % n
    assert one == 1, f"{a1} * {a} = {one} != 1 mod {n} ({name})"


def test(func, name):
    for n in range(1, 22, 2):
        for a in range(1, n):
            if math.gcd(a, n) != 1:
                continue
            test_one(func, name, a, n)

    for _ in range(100):
        while True:
            n = secrets.randbits(1024) | 1
            a = secrets.randbelow(n)
            if math.gcd(a, n) == 1:
                break
        test_one(func, name, a, n)


if __name__ == "__main__":
    test(modinv_euclid, "euclid")
    test(modinv_binary, "binary")
    test(sict_mi, "sict_mi")
