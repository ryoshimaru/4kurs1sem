import os
import random
from crypto_lib import mod_pow, fermat_test, extended_gcd


def mod_inverse(a, m):
    """Находит обратный элемент a по модулю m."""
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Обратное не существует")
    return x % m


def generate_parameters():
    """Генерирует параметры для шифра Эль-Гамаля."""
    while True:
        p = random.randint(256, 2000)
        if fermat_test(p):
            break
    g = random.randint(2, p - 2)
    x = random.randint(2, p - 2)  # закрытый ключ //cb
    y = mod_pow(g, x, p)          # открытый ключ //db
    return p, g, x, y


def elgamal_encrypt(input_path, output_path, p, g, y):
    """Шифрует файл по Эль-Гамалю."""
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        while byte := fin.read(1):
            m = byte[0]
            k = random.randint(2, p - 2)
            a = mod_pow(g, k, p) # a - открытый сессионный ключ 
            b = (m * mod_pow(y, k, p)) % p # шифрованное сообщение, e
            fout.write(a.to_bytes(4, 'little'))
            fout.write(b.to_bytes(4, 'little'))
    print(f"Файл '{output_path}' создан (зашифрован).")


def elgamal_decrypt(input_path, output_path, p, x):
    """Расшифровывает файл по Эль-Гамалю."""
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        while True:
            a_bytes = fin.read(4)
            b_bytes = fin.read(4)
            if not a_bytes or not b_bytes:
                break
            a = int.from_bytes(a_bytes, 'little')
            b = int.from_bytes(b_bytes, 'little')
            s = mod_pow(a, x, p) # 
            s_inv = mod_inverse(s, p)
            m = (b * s_inv) % p
            fout.write(bytes([m % 256]))
    print(f"Файл '{output_path}' создан (расшифрован).")


def main():
    print("=== Шифр Эль-Гамаля ===")

    # Шаг 1. Создаём исходный файл
    input_text = "Привет, это тестовое сообщение Эль-Гамаля!"
    with open("original.txt", "wb") as f:
        f.write(input_text.encode('utf-8'))
    print("Файл 'original.txt' создан.")

    # Шаг 2. Генерируем или вводим параметры
    choice = input("Ввести параметры вручную? (y/n): ").lower()
    if choice == 'y':
        while True:
            p = int(input("Введите простое число p (>255): "))
            if not fermat_test(p) or p <= 255:
                print("Недопустимое p")
                continue
            g = int(input(f"Введите g (1 < g < {p}): "))
            if not (1 < g < p):
                print("Недопустимое g")
                continue
            x = int(input(f"Введите закрытый ключ x (1 < x < {p-1}): "))
            if not (1 < x < p - 1):
                print("Недопустимое x")
                continue
            y = mod_pow(g, x, p)
            break
    else:
        p, g, x, y = generate_parameters()
        print(f"Сгенерированы параметры:\np = {p}\ng = {g}\nx = {x}\ny = {y}")

    # Шаг 3. Шифрование
    elgamal_encrypt("original.txt", "encrypted.dat", p, g, y)

    # Шаг 4. Расшифрование
    elgamal_decrypt("encrypted.dat", "decrypted.txt", p, x)

    # Шаг 5. Вывод результата
    with open("decrypted.txt", "rb") as f:
        result = f.read().decode('utf-8', errors='ignore')
    print("\nФинальное восстановленное сообщение:")
    print(result)


if __name__ == "__main__":
    main()
