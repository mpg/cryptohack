from rsa_starter_4 import p, q, n, e, d
from utils import modinv

assert n == 882564595536224140639625987659416029426239230804614613279163
assert e == 65537

c = 77578995801157823671636298847186723593814843845525223303932

print(pow(c, d, n))

# Can also be done using the CRT, which is faster as you're working on smaller
# numbers. Specifically pow(..., n) is cubic in bitlen(n), so it we do it twice
# on numbers with half as many bits, we're still winning by a factor 4 roughly.
#
# Note that the computation here somewhat mirrors the proof of the RSA property
# which also uses the CRT.

# We do this once at key generation time then store it:
# See https://datatracker.ietf.org/doc/html/rfc8017#appendix-A.1.2
dp = modinv(e, p - 1)
dq = modinv(e, q - 1)
qp = modinv(q, p)

# We do this for each decryption
mp = pow(c % p, dp, p)
mq = pow(c % q, dq, q)
m = (mq + q * qp * (mp - mq)) % n
# Clearly m % q = mq, since m = mq + q * [...]
# Also m mod p = mq + (1 mod p) * (mp - mq) = mq + mp - mq = mp mod p
print(m)
