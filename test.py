import numpy as np
from time import time

def print2(newlist):
    [[print(x,end="") for x in y] for y in newlist]
    print()

newlist = np.array([['H','e','l','l','o',','],['T','h','e','r','e','.']],dtype='U1')
print2(newlist)
newlist[0][4] = "."
print2(newlist)
newlist = np.append(newlist,['G','e','n','r','a','l'])
print2(newlist)
print(type(newlist))