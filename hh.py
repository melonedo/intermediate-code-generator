a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
n = 2
for b, c in [a[i:i + n] for i in range(1, len(a), n)]:
    print(b, c)


a = {}
a.update({"a": "b"})
print(a)