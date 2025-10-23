import math
from utils import modinv

p = 857504083339712752489993810777
q = 1029224947942998075080348647219
e = 65537

n = p * q

phi_n = (p - 1) * (q - 1)
d = modinv(e, phi_n)
if __name__ == "__main__":
    print(d)

lambda_n = math.lcm(p - 1, q - 1)
d_min = modinv(e, lambda_n)
if __name__ == "__main__":
    print(d_min)

