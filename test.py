l = [1,2,3,4,5]
n = 3.1
i = 0
stop = False
while i < len(l) and not stop:
    if l[i] < n:
        i+= 1
    else:
        l.insert(i,n)
        stop = True
print(l)