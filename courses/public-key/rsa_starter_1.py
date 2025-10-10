N = 22663
B = 101
E = 17
#E = 33
#E = 64
#E = 127
#E = N - 1
#E = N - 2

print(pow(B, E, N))


def rtl_bin(b, e, n):
    bit_val = b
    result = 1
    while e != 0:
        if e & 1 != 0:
            result = (result * bit_val) % n

        e >>= 1
        bit_val = (bit_val**2) % n

    return result

print(rtl_bin(B, E, N))


def ltr_bin(b, e, n):
    result = 1
    for i in range(e.bit_length() - 1, -1, -1):
        result = (result**2) % n
        if (e >> i) & 1 != 0:
            result = (result * b) % n

    return result

print(ltr_bin(B, E, N))


def ltr_quat(b, e, n):
    # pre-compute small powers of b
    cur = 1
    pre = []
    for _ in range(4):
        pre.append(cur)
        cur = (cur * b) % n

    # loop two bits at a time
    result = 1
    for i in range((e.bit_length() // 2) * 2, -1, -2):
        result = (result**4) % n
        bitpair = (e >> i) & 3
        result = (result * pre[bitpair]) % n

    return result

print(ltr_quat(B, E, N))
