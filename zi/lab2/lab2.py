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

def baby_step_giant_step(a, y, p): #y = a^x*mod p 
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

if __name__ == "__main__":
    print("\nЗадача дискретного логарифма (Baby-step Giant-step):")
    a, y, p = input_or_generate_dlog()
    x = baby_step_giant_step(a, y, p)
    print(f"Найденное x: {x}")

if x is not None:
    if mod_exp(a, x, p) == y:
        print("Проверка пройдена x решает уравнение")
    else:
        print("Ошибка x не подходит")
else:
    print("Решения нет")
    