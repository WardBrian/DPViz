import numpy as np
from rcviz import rcviz
from dpviz import dpviz


@rcviz
def lis(A):
    return lis_smaller(A, float('inf'))


@rcviz
def lis_smaller(A, x):
    if (not A):
        return 0
    m = lis_smaller(A[:-1], x)
    if (A[-1] < x):
        m = max(m, 1 + lis_smaller(A[:-1], A[-1]))
    return m


@dpviz
def lis_iter(A):
    n = len(A)
    A.append(float('Inf'))
    dp_table = np.zeros((n, n + 1), dtype=int)
    for j in range(1, n + 2):
        dp_table[0][j - 1] = 0
    for i in range(1, n + 1):
        for j in range(i + 1, n + 2):
            if A[i - 1] >= A[j - 1]:
                dp_table[i - 1][j - 1] = dp_table[i - 2][j - 1]
            else:
                dp_table[i - 1][j - 1] = max(dp_table[i - 2][j - 1], 1 + dp_table[i - 2][i - 1])
    return dp_table[n - 1][n]
