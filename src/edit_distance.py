import numpy as np
from rcviz import rcviz
from dpviz import dpviz


@rcviz
def edit_distance(A, B):
    m = len(A)
    n = len(B)
    if m == 0:
        return n
    if n == 0:
        return m
    insert = 1 + edit_distance(A, B[:-1])
    delete = 1 + edit_distance(A[:-1], B)
    replace = (A[-1] != B[-1]) + edit_distance(A[:-1], B[:-1])
    return min(insert, delete, replace)


@dpviz
def edit_distance_iter(A, B):
    m = len(A)
    n = len(B)
    dp_table = np.zeros((m + 1, n + 1), dtype=int)

    for j in range(0, n + 1):
        dp_table[0][j] = j

    for i in range(1, m + 1):
        dp_table[i][0] = i
        for j in range(1, n + 1):
            insert = dp_table[i][j - 1] + 1
            delete = dp_table[i - 1][j] + 1
            if A[i - 1] == B[j - 1]:
                replace = dp_table[i - 1][j - 1]
            else:
                replace = dp_table[i - 1][j - 1] + 1
            dp_table[i][j] = min(insert, delete, replace)
    return dp_table[i][j]
