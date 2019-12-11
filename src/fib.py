import numpy as np
from rcviz import rcviz
from dpviz import dpviz


@rcviz
def fib(n):
    if (n == 0):
        return 0
    if (n == 1):
        return 1
    return fib(n - 1) + fib(n - 2)


@dpviz
def fib_iter(n):
    dp_table = np.zeros((n + 1, ), dtype=int)
    dp_table[0] = 0
    dp_table[1] = 1
    for i in range(2, n + 1):
        dp_table[i] = dp_table[i - 1] + dp_table[i - 2]
    return dp_table[n]
