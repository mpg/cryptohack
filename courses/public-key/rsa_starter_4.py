import math

p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537

n = p * q

phi_n = (p - 1) * (q - 1)
d = pow(e, -1, phi_n)
print(d)

lambda_n = math.lcm(p - 1, q - 1)
d_min = pow(e, -1, lambda_n)
print(d_min)

