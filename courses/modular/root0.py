p = 29

squares = {x * x % p: x for x in range(p // 2)}

for i in (14, 6, 11):
    if i in squares:
        print(f"{i} = {squares[i]}^2")
