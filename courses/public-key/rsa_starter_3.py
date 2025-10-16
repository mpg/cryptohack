P = 857504083339712752489993810777
Q = 1029224947942998075080348647219

N = P * Q
phi_N = (P - 1) * (Q - 1)
print("phi(N) =", phi_N)

# Finding P and Q knowing only N is hard (factoring problem).
# However finding P and Q knowing N and phi(N) is trivial.
def recover_p_q(n, phi_n):
    p_plus_q = N - phi_n + 1 # (p-1)(q-1) = pq - (p+q) + 1
    # Finding two numbers knowing their product and sum
    # is a classical high-school exercise
    return numbers_from_sum_and_product(p_plus_q, n)

import math

def numbers_from_sum_and_product(add, mul):
    # Notice (X - a)(X - b) = X^2 - (a+b)X + ab
    # So the number we seek at the two roots of X^2 - add*X + mul
    delta = add**2 - 4 * 1 * mul
    x1 = (add - math.isqrt(delta)) // 2
    x2 = (add + math.isqrt(delta)) // 2
    return x1, x2

print(recover_p_q(N, phi_N))
print((P, Q))

import secrets

# Euler's theorem: for any m coprime with N, we have m^phi(N) == 1
m = secrets.randbelow(N)
assert math.gcd(m, N) == 1, "unlucky random number, try again"
print("m^phi(N) =", pow(m, phi_N, N))

# That's not true when m is a multiple of p or q
x = 42 * P
print("x^phi(N) =", pow(x, phi_N, N))
# However it is still true that x^(phi(N) + 1) == x
print("x^(phi(N) + 1) =", pow(x, phi_N + 1, N))
print("x              =", x)
# Actually for any k we still have x^(k*phi(N) + 1) == x
k = secrets.randbelow(phi_N)
print("x^(k*phi(N)+1) =", pow(x, k * phi_N + 1, N))
# The above identity holds for any x and any k and is proven
# in the original RSA paper:
# https://people.csail.mit.edu/rivest/Rsapaper.pdf#page=8
# The paper chooses e and d such that e * d = k * phi(N) + 1
# immediately yielding m^(ed) = m mod N for any m.
#
# However, he exponent in Euler's theorem is not minimal.
# The optimal exponent is known as Carmichael's function.
# For N = P * Q both primes, lambda(N) = lcm(P - 1, Q - 1)
# Then for any m coprime with N, we have m^lambda(N) == 1
lambda_N = phi_N // math.gcd(P - 1, Q - 1)
print("lambda(N) =", lambda_N)
print("m^lambda(N) =", pow(m, lambda_N, N))

# Again that doesn't work for x not coprime with N
print("x^lambda(N) =", pow(x, lambda_N, N))
# However it is still true that x^(lambda(N) + 1) == x
print("x^(lambda(N) + 1) =", pow(x, lambda_N + 1, N))
print("x                 =", x)
# Actually for any k we still have x^(k*lambda(N) + 1) == x
print("x^(k*lambda(N)+1) =", pow(x, k * phi_N + 1, N))
# This is what we actually use in NIST-compliant implementations of RSA,
# where we pick the minimal d such that e * d = k * lambda(N) + 1,
# that is, d = e^-1 mod lambda(N).
# We still have m^(ed) = m mod N for any m, but d is a bit smaller.
#
# Amazingly the proof from the original paper works completely
# unchanged, as the only property of phi(N) it uses is that
# it is a multiple of both p-1 and q-1. And so is LCM(p-1, q-1)...

