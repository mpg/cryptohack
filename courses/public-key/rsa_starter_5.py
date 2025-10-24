# data from rsa_starter_4
p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537

# computations from rsa_starter_4
n = p * q
d = pow(e, -1, (p - 1) * (q - 1))

# new data
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
dp = pow(e, -1, p - 1)
dq = pow(e, -1, q - 1)
qp = pow(q, -1, p)

# We do this for each decryption
mp = pow(c % p, dp, p)
mq = pow(c % q, dq, q)
m = (mq + q * qp * (mp - mq)) % n
# Clearly m % q = mq, since m = mq + q * [...]
# Also m mod p = mq + (1 mod p) * (mp - mq) = mq + mp - mq = mp mod p
print(m)
