import math
import secrets


# This is the way I do the extended Euclidean algorithm by hand:
# compute the GCD the normal way, then "climb back" the ladder of divisions.
# To me it's the most intuitive way, that I can always remember.
# Invoke with show=True to print details on stdout.
def euclid_intuitive(a, b, show=False):
    assert a >= 0 and b >= 0

    # Ensure a >= b
    if b > a:
        g, u, v = euclid_intuitive(b, a, show)
        return g, v, u

    # Rule out special cases
    if b == 0:
        return a, 1, 1
    if a % b == 0:
        return b, 0, 1

    # This is the same as the non-extended algorithm of euclid_gcd() in gcd.py
    # except we remember all the divisions we're doing
    lines = []
    while True:
        q, r = divmod(a, b)
        if r == 0:
            break

        lines.append((a, b, q, r))
        if show:
            print(f"{a} = {b} * {q} + {r}")

        a, b = b, r

    # Start with the last remainder, which is the GCD
    an, bn, qn, rn = lines.pop()
    g, u, v = rn, 1, 0 - qn
    if show:
        print(f"The GCD is {g} and we have {g} = {an} * {u} + {bn} * {v}")

    # Now go back up the chain
    for ai, bi, qi, ri in reversed(lines):
        if show:
            print(f"Substituting {ri} = {ai} - {bi} * {qi} we get ", end="")
        # We currently have g = a_{i+1} * u + b_{i+1} * v
        # From the previous loop's last line, a_{i+1} = b_i and b_{i+1} = r_i
        # So we have g = b_i * u + r_i * v
        #              = b_i * u + (a_i - b_i * q_i) * v
        #              = a_i * v + b_i * (u - q_i * v)
        # giving us our update formula:
        u, v = v, u - qi * v
        if show:
            print(f"{g} = {ai} * {u} + {bi} * {v}")

    return g, u, v


# This is "normal" version the extended Euclidean algorithm.
# Same structure as euclid_gcd() from gcd.py.
def euclid_direct(a, b):
    assert a >= 0 and b >= 0

    # Ensure a >= b
    if b > a:
        g, u, v = euclid_direct(b, a)
        return g, v, u

    # Invariants:
    # GCD(ai, bi) = GCD(a, b)
    # ai = a * u + b * v
    # bi = a * s + b * t
    ai, u, v = a, 1, 0
    bi, s, t = b, 0, 1
    while bi != 0:
        q, r = divmod(ai, bi)
        # r = ai - q * bi
        #   = (a*u + b*v) - q * (a*s + b*t)
        #   = a * (u - q*s) + b * (v - q*t)
        rs, rt = u - q * s, v - q * t
        # The basic alg does a, b = b, r; extend that with coefficients
        ai, u, v = bi, s, t
        bi, s, t = r, rs, rt

    return ai, u, v


def test_one(func, name, a, b):
    exp = math.gcd(a, b)
    got, u, v = func(a, b)
    assert got == exp, f"{name}({a}, {b}) = {got} != {exp}"
    assert a * u + b * v == got, f"{a} * {u} + {b} * {v} != {got} ({name})"


def test(func, name):
    for a in range(10):
        for b in range(10):
            test_one(func, name, a, b)

    for _ in range(100):
        a = secrets.randbits(256)
        b = secrets.randbits(256)
        test_one(func, name, a, b)


test(euclid_intuitive, "euclid_intuitive")
test(euclid_direct, "euclid_direct")

g, u, v = euclid_intuitive(26513, 32321, show=True)
assert g == 1
print("Flag:", min(u, v))
