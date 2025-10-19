import os
import random
from crypto_lib import mod_pow, fermat_test, extended_gcd

def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Обратное не существует")
    return x % m

def generate_parameters():
    while True:
        P = random.randint(256, 1000)
        if fermat_test(P):
            break
    phi = P - 1

    while True:
        Ca = random.randint(2, phi - 1)
        if extended_gcd(Ca, phi)[0] == 1:
            break
    Da = mod_inverse(Ca, phi)

    while True:
        Cb = random.randint(2, phi - 1)
        if extended_gcd(Cb, phi)[0] == 1:
            break
    Db = mod_inverse(Cb, phi)

    return P, Ca, Da, Cb, Db

def main():
    P = Ca = Da = Cb = Db = 0

    print("=== Метод Шамира ===")

    choice = input("Введите исходное сообщение вручную? (y/n): ").lower()
    if choice == 'y':
        input_text = input("Введите сообщение: ")
    else:
        input_text = "Привет, это тестовое сообщение Шамира!"
        print(f"Сгенерировано сообщение: {input_text}")

    with open("original.txt", "wb") as f:
        f.write(input_text.encode('utf-8'))
    print("Файл 'original.txt' создан.")

    choice = input("Ввести параметры вручную? (y/n): ").lower()
    phi = 0
    if choice == 'y':
        while True:
            P = int(input("Введите простое число P (> 255): "))
            if not fermat_test(P) or P <= 255:
                print("Недопустимое простое число")
                continue
            phi = P - 1
            Ca = int(input(f"Введите Ca (1 < Ca < {phi}): "))
            if Ca <= 1 or Ca >= phi or extended_gcd(Ca, phi)[0] != 1:
                print("Ca недопустимо")
                continue
            Da = mod_inverse(Ca, phi)
            Cb = int(input(f"Введите Cb (1 < Cb < {phi}): "))
            if Cb <= 1 or Cb >= phi or extended_gcd(Cb, phi)[0] != 1:
                print("Cb недопустимо")
                continue
            Db = mod_inverse(Cb, phi)
            break
    else:
        P, Ca, Da, Cb, Db = generate_parameters()
        phi = P - 1
        print(f"Сгенерированы параметры: P={P}, Ca={Ca}, Da={Da}, Cb={Cb}, Db={Db}")

    steps = [
        ("X1.txt", Ca),
        ("X2.txt", Cb),
        ("X3.txt", Da),
        ("final.txt", Db)
    ]

    prev_file = "original.txt"
    for idx, (filename, key) in enumerate(steps, start=1):
        with open(prev_file, 'rb') as fin, open(filename, 'wb') as fout:
            while byte := fin.read(1 if idx == 1 else 8):
                if idx == 1:
                    m = byte[0]
                    x = mod_pow(m, key, P)
                    fout.write(x.to_bytes(8, 'little'))
                else:
                    x_in = int.from_bytes(byte, 'little')
                    x_out = mod_pow(x_in, key, P)
                    if idx == 4:
                        fout.write(bytes([x_out % 256]))
                    else:
                        fout.write(x_out.to_bytes(8, 'little'))
        print(f"Шаг {idx} завершен: создан файл '{filename}'")
        prev_file = filename

    with open("final.txt", 'rb') as f:
        message = f.read().decode('utf-8', errors='ignore')
    print("\nФинальное восстановленное сообщение:")
    print(message)

if __name__ == "__main__":
    main()