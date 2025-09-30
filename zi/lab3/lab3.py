import random
import math

def mod_exp(a, x, p):
    result = 1
    a = a % p
    while x > 0:
        if x % 2 == 1:
            result = (result * a) % p
        a = (a * a) % p
        x //= 2
    return result

def extended_gcd(a, b):
    u1, u2, u3 = a, 1, 0
    v1, v2, v3 = b, 0, 1
    while v1 != 0:
        q = u1 // v1
        t1, t2, t3 = u1 % v1, u2 - q * v2, u3 - q * v3
        u1, u2, u3 = v1, v2, v3
        v1, v2, v3 = t1, t2, t3
    return u1, u2, u3

def mod_inverse(a, p):
    gcd, x, _ = extended_gcd(a, p)
    if gcd != 1:
        return None
    return x % p

def baby_step_giant_step(a, y, p):
    if p <= 1:
        raise ValueError("Модуль p должен быть больше 1 и простым числом")
    if a <= 0:
        raise ValueError("Основание a должно быть положительным")
    if y <= 0 or y >= p:
        raise ValueError("y должно быть положительным и меньше p")

    m = math.isqrt(p - 1) + 1

    table = {}
    value = 1
    table[0] = y
    for j in range(m):
        table[value] = j
        value = (value * a) % p

    inv_am = mod_inverse(a, p)
    if inv_am is None:
        raise ValueError("Обратный элемент не существует, a и p должны быть взаимно простыми")
    inv_am = mod_exp(inv_am, m, p)

    value = y
    for i in range(m):
        if value in table:
            return i * m + table[value]
        value = (value * inv_am) % p

    return None

def input_or_generate_dlog():
    choice = input("Ввести a, y, p вручную? (y/n): ").lower()
    if choice == "y":
        a = int(input("Введите основание a: "))
        y = int(input("Введите значение y: "))
        p = int(input("Введите простое число p: "))
    else:
        while True:
            p = random.randint(2, 10**6)
            a = random.randint(2, p - 1)
            if math.gcd(a, p) == 1:
                break
        m = math.isqrt(p - 1) + 1
        x = random.randint(1, m * m - 1)
        y = mod_exp(a, x, p)
        print(f"Сгенерировано: a={a}, x={x}, p={p}, y={y}")
    return a, y, p


def _miller_rabin(n, k=8):
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_exp(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True

def _generate_prime(low=2**16, high=2**20):
    while True:
        cand = random.randrange(low | 1, high, 2)  
        if _miller_rabin(cand):
            return cand


def _primitive_root(p):
    phi = p - 1
    factors = set()
    x = phi
    d = 2
    while d * d <= x:
        if x % d == 0:
            factors.add(d)
            while x % d == 0:
                x //= d
        d += 1
    if x > 1:
        factors.add(x)

    for g in range(2, p):
        ok = True
        for q in factors:
            if mod_exp(g, phi // q, p) == 1:
                ok = False
                break
        if ok:
            return g
    raise RuntimeError("Не найден примитивный корень")

def diffie_hellman():
    print("\nСхема Диффи-Хеллмана:")
    mode = input("Ввести p, g, X_A, X_B вручную? (y/n): ").strip().lower()

    if mode == 'y':
        p = int(input("Введите p (простое): ").strip())
        g = int(input("Введите g (примитивный корень по модулю p): ").strip())
        XA = int(input("Введите X_A (секрет A, 1..p-2): ").strip())
        XB = int(input("Введите X_B (секрет B, 1..p-2): ").strip())
    else:
        p = _generate_prime()            
        g = _primitive_root(p)           
        XA = random.randint(1, p - 2)    
        XB = random.randint(1, p - 2)
        print(f"Сгенерировано: p={p}, g={g}, X_A={XA}, X_B={XB}")

    YA = mod_exp(g, XA, p)  
    YB = mod_exp(g, XB, p)  
    ZA = mod_exp(YB, XA, p)  
    ZB = mod_exp(YA, XB, p) 

    print(f"Открытый ключ A (Y_A) = {YA}")
    print(f"Открытый ключ B (Y_B) = {YB}")
    print(f"Общий ключ, вычисленный A: {ZA}")
    print(f"Общий ключ, вычисленный B: {ZB}")
    print(f"Ключи совпадают: {ZA == ZB}")

if __name__ == "__main__":
    print("\nЗадача дискретного логарифма (Baby-step Giant-step):")
    a, y, p = input_or_generate_dlog()
    x = baby_step_giant_step(a, y, p)
    print(f"Найденное x: {x}")

    if x is not None:
        if mod_exp(a, x, p) == y:
            print("Проверка пройдена: x решает уравнение")
        else:
            print("Ошибка: x не подходит")
    else:
        print("Решения нет")

    diffie_hellman()
