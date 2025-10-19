import random
import math

def mod_pow(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp = exp // 2
    return result

def fermat_test(n, k=10):
    if n <= 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    for _ in range(k):
        a = random.randint(2, n - 2)
        if mod_pow(a, n - 1, n) != 1:
            return False
    return True

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def generate_prime_numbers(min_val=2, max_val=3628800, k=10):
    def find_prime(min_v, max_v, k_test):
        while True:
            candidate = random.randint(min_v, max_v)
            if fermat_test(candidate, k_test):
                return candidate
    
    a = find_prime(min_val, max_val, k)
    b = find_prime(min_val, max_val, k)
    return a, b

def baby_step_giant_step(a, y, p):
    if y == 1:
        return 0
    if a == 0:
        return 1 if y == 0 else None
    
    m = int(math.isqrt(p)) + 1
    
    baby_steps = {}
    current = y % p
    baby_steps[current] = 0
    
    for j in range(1, m):
        current = (current * a) % p
        if current not in baby_steps:
            baby_steps[current] = j
    
    a_power_m = mod_pow(a, m, p)
    giant_step = 1
    
    for i in range(1, m + 1):
        giant_step = (giant_step * a_power_m) % p
        if giant_step in baby_steps:
            j = baby_steps[giant_step]
            x = i * m - j
            if mod_pow(a, x, p) == y % p:
                return x
    
    return None

def generate_safe_prime(min_val=2, max_val=3628800, k=10):
    max_q = (max_val - 1) // 2 
    min_q = max(2, (min_val - 1) // 2)
    
    while True:
        q = random.randint(min_q, max_q)
        if fermat_test(q, k): 
            p = 2 * q + 1
            if fermat_test(p, k): 
                return p, q

def is_primitive_root(g, p):
    phi = p - 1
    if mod_pow(g, phi, p) != 1:
        return False
    
    factors = []
    d = 2
    n = phi
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    
    for factor in set(factors):
        if mod_pow(g, phi // factor, p) == 1:
            return False
    return True

def find_primitive_root(p):
    while True:
        g = random.randint(2, p-2)
        if is_primitive_root(g, p):
            return g

def generate_dlog_parameters(min_val=2, max_val=3628800):
    p, q = generate_safe_prime(min_val, max_val)  
    a = random.randint(2, p-2)
    x = random.randint(1, p-2)
    y = mod_pow(a, x, p)
    return a, y, p, x