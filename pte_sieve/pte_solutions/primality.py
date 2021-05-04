# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# primality.py

from random import randrange 

def is_prime(n: int, t: int = 20):
    '''The Miller-Rabin pseudo-primality test.
    '''
    # Negative numbers are allowed and are made positive for test.
    if n < 0:
        n = -n
    if n == 1:
        return False
    if n == 2:
        return True
    if n & 1 == 0:
        return False
    s, r = 0, n - 1
    while s & 1 == 0:
        r >>= 1
        s += 1    
    # Now n-1 = 2^s * r
    for j in range(t):
        a = randrange(2, n - 1)
        assert (2 <= a <= n - 2)

        y = pow(a, r, n)
        if y in (1, n - 1):
            continue

        for _ in range(s - 1):
            y = pow(y, 2, n)
            if y == n - 1:
                break
        else:
            return False

    return True
