n = 510143758735509025530880200653196460532653147

f = n.factor(algorithm="qsieve")
print(f)
t = timeit('n.factor(algorithm="qsieve")', number=1, repeat=1)
print(t)

f = n.factor()
print(f)
t = timeit('n.factor()', number=1, repeat=1)
print(t)
