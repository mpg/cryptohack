import secrets

bil = 64

def bitlimbs(x):
    return (x.bit_length() + bil - 1) // bil * bil

def sict_gcd(p, a):
    assert p >= a >= 0
    assert p & 1 != 0 or a & 1 != 0

    u, v = a, p
    for i in range(2 * p.bit_length()):
        s, z = u & 1, v & 1
        t1 = (s ^ z) * v + (2 * s * z - 1) * u
        t2 = (s * v + (2 - 2 * s - z) * u) >> 1

        if t2 >= t1:
            u, v = t1, t2
        else:
            u, v = t2, t1
        
        if u == 0:
            return bitlimbs(a) + bitlimbs(p) - i

    return 0

m = 1000
while m != 1:
    n = secrets.randbits(128) | 1
    d = sict_gcd(n, 2**(bil-1))
    if d < m:
        m = d
        print(d)

print(hex(n)[2:])
