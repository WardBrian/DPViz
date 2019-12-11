import numpy as np
from rcviz import rcviz
from dpviz import dpviz


@rcviz
def binom(n, k):
    if k == 0 or k == n:
        return 1
    return binom(n - 1, k - 1) + binom(n - 1, k)


@dpviz
def binom_iter(n, k):
    dp_table = np.zeros((n + 1, k + 1), dtype=int)
    for j in range(0, k + 1):
        dp_table[j][j] = 1
    for i in range(0, n + 1):
        dp_table[i][0] = 1
    for i in range(1, n + 1):
        for j in range(1, min(i, k + 1)):
            dp_table[i][j] = dp_table[i - 1][j - 1] + dp_table[i - 1][j]
    return dp_table[n][k]
