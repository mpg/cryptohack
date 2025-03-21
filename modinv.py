import math
import secrets
import egcd


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


def test_one(func, name, a, n):
    a1 = func(a, n)
    assert 0 <= a < n, f"{a1} not in range [0, {n}] ({name})"
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
