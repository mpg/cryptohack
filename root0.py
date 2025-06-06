p = 29

squares = set(x * x % p for x in range(p))

for s in sorted(squares):
    print(s)

assert len(squares) == (p + 1) / 2
