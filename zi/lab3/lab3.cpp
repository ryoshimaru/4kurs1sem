#include <iostream>
#include <random>
#include <cmath>
#include <map>
#include <algorithm>
#include <climits>
#include <cstdlib>
#include <string>
#include <vector>

#ifdef _WIN32
    #define CLEAR "cls"
#else
    #define CLEAR "clear"
#endif

std::random_device rd;
std::mt19937 gen(rd());

void clear_console() {
    std::system(CLEAR);
}

long long mod_pow(long long base, long long exp, long long mod) {
    if (mod == 1) return 0;
    long long result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1)
            result = (result * base) % mod;
        exp = exp >> 1;
        base = (base * base) % mod;
    }
    return result;
}

bool fermat_test(long long n, int k = 100) {
    if (n <= 1) return false;
    if (n == 2 || n == 3) return true;
    if (n % 2 == 0) return false;

    std::uniform_int_distribution<long long> dis(2, n - 2);
    for (int i = 0; i < k; ++i) {
        long long a = dis(gen);
        if (mod_pow(a, n - 1, n) != 1)
            return false;
    }
    return true;
}   

std::tuple<long long, long long, long long> extended_gcd(long long a, long long b) {
    long long x0 = 1, y0 = 0;
    long long x1 = 0, y1 = 1;

    while (b != 0) {
        long long q = a / b;
        long long r = a % b;

        long long x2 = x0 - q * x1;
        long long y2 = y0 - q * y1;

        x0 = x1; y0 = y1;
        x1 = x2; y1 = y2;

        a = b;
        b = r;
    }

    return std::make_tuple(a, x0, y0);
}

long long baby_step_giant_step(long long a, long long y, long long p) {
    if (y == 1) return 0;
    if (a == 0) return (y == 0) ? 1 : -1;

    long long m = static_cast<long long>(std::sqrt(p)) + 1;
    long long k = (p + m - 1) / m;
    while (m * k <= p) {
        m++;
        k = (p + m - 1) / m;
    }

    std::map<long long, long long> baby_steps;
    long long current = y % p;
    baby_steps[current] = 0;

    for (long long j = 1; j < m; ++j) {
        current = (current * a) % p;
        if (baby_steps.find(current) == baby_steps.end()) {
            baby_steps[current] = j;
        }
    }

    long long a_power_m = mod_pow(a, m, p);
    long long giant_step = 1;

    for (long long i = 1; i <= k; ++i) {
        giant_step = (giant_step * a_power_m) % p;
        if (baby_steps.find(giant_step) != baby_steps.end()) {
            long long j = baby_steps[giant_step];
            long long x = i * m - j;
            if (x >= 0 && mod_pow(a, x, p) == y % p) {
                return x;
            }
        }
    }
    return -1;
}

std::pair<long long, long long> generate_random_numbers(long long min_val = 1, long long max_val = 3628800) {
    std::uniform_int_distribution<long long> dis(min_val, max_val);
    return {dis(gen), dis(gen)};
}

std::pair<long long, long long> generate_prime_numbers(long long min_val = 2, long long max_val = 3628800, int k = 10) {
    auto find_prime = [&](long long min_v, long long max_v, int k_test) -> long long {
        std::uniform_int_distribution<long long> dis(min_v, max_v);
        while (true) {
            long long candidate = dis(gen);
            if (fermat_test(candidate, k_test)) {
                return candidate;
            }
        }
    };
    long long a = find_prime(min_val, max_val, k);
    long long b = find_prime(min_val, max_val, k);
    return {a, b};
}

std::pair<long long, long long> generate_safe_prime(long long min_val = 2, long long max_val = 3628800, int k = 10) {
    auto find_safe_prime = [&](long long min_v, long long max_v, int k_test) -> std::pair<long long, long long> {
        long long max_q = (max_v - 1) / 2;
        long long min_q = std::max(2LL, (min_v - 1) / 2);
        if (min_q > max_q) min_q = max_q;

        std::uniform_int_distribution<long long> dis_q(min_q, max_q);
        while (true) {
            long long q = dis_q(gen);
            if (fermat_test(q, k_test)) {
                long long p = 2 * q + 1;
                if (p <= max_v && fermat_test(p, k_test)) {
                    return {p, q};
                }
            }
        }
    };
    return find_safe_prime(min_val, max_val, k);
}

std::tuple<long long, long long, long long, long long> generate_dlog_parameters(long long min_val = 2, long long max_val = 3628800) {
    auto [p, q] = generate_safe_prime(min_val, max_val);
    std::uniform_int_distribution<long long> dis_a(2, p - 2);
    std::uniform_int_distribution<long long> dis_x(1, p - 2);
    long long a = dis_a(gen);
    long long x = dis_x(gen);
    long long y = mod_pow(a, x, p);
    return {a, y, p, x};
}

bool is_primitive_root_custom(long long g, long long p) {
    long long phi = p - 1;
    if (mod_pow(g, phi, p) != 1) return false;
    long long q = phi / 2;
    if (mod_pow(g, 2, p) == 1 || mod_pow(g, q, p) == 1) return false;
    return true;
}

long long find_primitive_root(long long p) {
    std::uniform_int_distribution<long long> dis(2, p - 2);
    while (true) {
        long long g = dis(gen);
        if (is_primitive_root_custom(g, p)) {
            return g;
        }
    }
}

int main() {
    std::string choice;
    while (true) {
        clear_console();
        std::cout << "Криптографическая библиотека\n";
        std::cout << "1. Тест простоты Ферма\n";
        std::cout << "2. Быстрое возведение в степень по модулю\n";
        std::cout << "3. Обобщённый алгоритм Евклида\n";
        std::cout << "4. Решение задачи дискретного логарифма (Шаг младенца, шаг великана)\n";
        std::cout << "5. Схема Диффи-Хеллмана\n";
        std::cout << "0. Для завершения программы\n";
        std::cout << "Выберите опцию (1-5 или '0'): ";
        std::getline(std::cin, choice);

        if (choice == "0") {
            clear_console();
            std::cout << "Программа завершена\n";
            break;
        }

        if (choice == "1") {
            clear_console();
            std::cout << "Тест простоты Ферма\n";
            std::cout << "Вариант ввода числа:\n";
            std::cout << "1. Ввод с клавиатуры\n";
            std::cout << "2. Генерация случайного числа\n";
            std::cout << "Выберите: ";
            std::string sub_choice;
            std::getline(std::cin, sub_choice);
            long long n;
            if (sub_choice == "1") {
                std::cout << "Введите число n: ";
                std::cin >> n;
                std::cin.ignore();
            } else {
                std::uniform_int_distribution<long long> dis(2, 3628800);
                n = dis(gen);
                std::cout << "Сгенерировано число: " << n << "\n";
            }
            bool is_prime = fermat_test(n);
            std::cout << "Число " << n << " " << (is_prime ? "вероятно простое" : "не простое") << "\n";
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }

        else if (choice == "2") {
            clear_console();
            std::cout << "Быстрое возведение в степень по модулю: y = a^x mod p\n";
            std::cout << "Вариант ввода:\n";
            std::cout << "1. Ввод a, x, p с клавиатуры\n";
            std::cout << "2. Генерация a, x, p случайным образом\n";
            std::cout << "3. Генерация a, p простыми числами\n";
            std::cout << "Выберите: ";
            std::string sub_choice;
            std::getline(std::cin, sub_choice);
            long long a, x, p;
            if (sub_choice == "1") {
                std::cout << "Введите a: "; std::cin >> a;
                std::cout << "Введите x: "; std::cin >> x;
                std::cout << "Введите p: "; std::cin >> p;
                std::cin.ignore();
            } else if (sub_choice == "2") {
                std::uniform_int_distribution<long long> dis_a(1, 3628800);
                std::uniform_int_distribution<long long> dis_x(1, 1000);
                std::uniform_int_distribution<long long> dis_p(2, 3628800);
                a = dis_a(gen); x = dis_x(gen); p = dis_p(gen);
                std::cout << "Сгенерировано: a=" << a << ", x=" << x << ", p=" << p << "\n";
            } else {
                auto [pa, pp] = generate_prime_numbers(2, 3628800);
                a = pa; p = pp;
                std::uniform_int_distribution<long long> dis_x(1, 1000);
                x = dis_x(gen);
                std::cout << "Сгенерировано простые a=" << a << ", p=" << p << ", случайный x=" << x << "\n";
            }
            long long y = mod_pow(a, x, p);
            std::cout << "y = " << y << "\n";
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }

        else if (choice == "3") {
            clear_console();
            std::cout << "Обобщённый алгоритм Евклида: gcd(a, b), x, y где a*x + b*y = gcd\n";
            std::cout << "Вариант ввода a, b:\n";
            std::cout << "1. Ввод с клавиатуры\n";
            std::cout << "2. Генерация случайных a, b\n";
            std::cout << "3. Генерация простых a, b\n";
            std::cout << "Выберите: ";
            std::string sub_choice;
            std::getline(std::cin, sub_choice);
            long long a, b;
            if (sub_choice == "1") {
                std::cout << "Введите a: "; std::cin >> a;
                std::cout << "Введите b: "; std::cin >> b;
                std::cin.ignore();
            } else if (sub_choice == "2") {
                auto [ra, rb] = generate_random_numbers(1, 3628800);
                a = ra; b = rb;
                std::cout << "Сгенерировано: a=" << a << ", b=" << b << "\n";
            } else {
                auto [pa, pb] = generate_prime_numbers(2, 3628800);
                a = pa; b = pb;
                std::cout << "Сгенерировано простые: a=" << a << ", b=" << b << "\n";
            }
            auto [gcd, x, y] = extended_gcd(a, b);
            std::cout << "gcd(" << a << ", " << b << ") = " << gcd << "\n";
            std::cout << "x = " << x << ", y = " << y << "\n";
            std::cout << "Проверка: " << a << "*" << x << " + " << b << "*" << y << " = " << (a * x + b * y) << "\n";
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }

        else if (choice == "4") {
            clear_console();
            std::cout << "Решение задачи дискретного логарифма: y = a^x mod p\n";
            std::cout << "Вариант ввода a, y, p:\n";
            std::cout << "1. Ввод с клавиатуры\n";
            std::cout << "2. Генерация случайных a, y, p (p безопасное простое)\n";
            std::cout << "Выберите: ";
            std::string sub_choice;
            std::getline(std::cin, sub_choice);
            long long a, y, p, true_x = -1;
            if (sub_choice == "1") {
                std::cout << "Введите a: "; std::cin >> a;
                std::cout << "Введите y: "; std::cin >> y;
                std::cout << "Введите p (должно быть безопасным простым): "; std::cin >> p;
                std::cin.ignore();
                long long q = (p - 1) / 2;
                if (!(fermat_test(p) && fermat_test(q))) {
                    std::cout << "Предупреждение: p не является безопасным простым числом.\n";
                }
            } else {
                auto [gen_a, gen_y, gen_p, gen_x] = generate_dlog_parameters(2, 3628800);
                a = gen_a; y = gen_y; p = gen_p; true_x = gen_x;
                std::cout << "Сгенерировано: a=" << a << ", y=" << y << ", p=" << p << "\n";
                std::cout << "(Истинное x для проверки: " << true_x << ")\n";
            }
            long long x = baby_step_giant_step(a, y, p);
            if (x != -1) {
                std::cout << "Найдено x = " << x << "\n";
                long long verify = mod_pow(a, x, p);
                std::cout << "Проверка: a^x mod p = " << verify << ", должно быть равно y=" << y << "\n";
                if (true_x != -1) {
                    std::cout << "Сравнение с истинным x: " << true_x << ", совпадение: " << (x == true_x ? "да" : "нет") << "\n";
                }
            } else {
                std::cout << "Решение не найдено.\n";
            }
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }

        else if (choice == "5") {
            clear_console();
            std::cout << "Схема Диффи-Хеллмана: построение общего ключа\n";
            std::cout << "Вариант ввода:\n";
            std::cout << "1. Ввод p, g, Xa, Xb с клавиатуры\n";
            std::cout << "2. Генерация параметров\n";
            std::cout << "Выберите: ";
            std::string sub_choice;
            std::getline(std::cin, sub_choice);
            long long p, g, Xa, Xb;
            if (sub_choice == "1") {
                while (true) {
                    try {
                        std::cout << "Введите p (безопасное простое): ";
                        std::cin >> p;
                        long long q = (p - 1) / 2;
                        if (!(fermat_test(p) && fermat_test(q))) {
                            std::cout << "Ошибка: p не является безопасным простым числом (p = 2q + 1, где q — простое).\n";
                            std::cin.ignore();
                            std::cout << "Нажмите Enter для продолжения...";
                            std::cin.get();
                            continue;
                        }
                        break;
                    } catch (...) {
                        std::cout << "Ошибка: введите целое число для p.\n";
                        std::cin.ignore();
                        std::cout << "Нажмите Enter для продолжения...";
                        std::cin.get();
                        continue;
                    }
                }
                while (true) {
                    try {
                        std::cout << "Введите g (генератор): ";
                        std::cin >> g;
                        if (!is_primitive_root_custom(g, p)) {
                            std::cout << "Ошибка: g не является примитивным корнем. Пожалуйста, введите другое g.\n";
                            continue;
                        }
                        break;
                    } catch (...) {
                        std::cout << "Ошибка: введите целое число для g.\n";
                        continue;
                    }
                }
                while (true) {
                    try {
                        std::cout << "Введите Xa (секрет A): ";
                        std::cin >> Xa;
                        if (Xa < 1 || Xa >= p - 1) {
                            std::cout << "Ошибка: Xa должно быть в диапазоне [1, " << p - 2 << "].\n";
                            continue;
                        }
                        break;
                    } catch (...) {
                        std::cout << "Ошибка: введите целое число для Xa.\n";
                        continue;
                    }
                }
                while (true) {
                    try {
                        std::cout << "Введите Xb (секрет B): ";
                        std::cin >> Xb;
                        if (Xb < 1 || Xb >= p - 1) {
                            std::cout << "Ошибка: Xb должно быть в диапазоне [1, " << p - 2 << "].\n";
                            continue;
                        }
                        break;
                    } catch (...) {
                        std::cout << "Ошибка: введите целое число для Xb.\n";
                        continue;
                    }
                }
                std::cin.ignore();
            } else {
                auto [gen_p, gen_q] = generate_safe_prime(100, 3628800);
                p = gen_p;
                g = find_primitive_root(p);
                std::uniform_int_distribution<long long> dis_secret(1, p - 2);
                Xa = dis_secret(gen);
                Xb = dis_secret(gen);
                std::cout << "Сгенерировано: p=" << p << ", q=" << (p - 1) / 2 << ", g=" << g << ", Xa=" << Xa << ", Xb=" << Xb << "\n";
            }
            long long Ya = mod_pow(g, Xa, p);
            long long Yb = mod_pow(g, Xb, p);
            long long Ka = mod_pow(Yb, Xa, p);
            long long Kb = mod_pow(Ya, Xb, p);
            std::cout << "Открытый ключ A (Ya): " << Ya << "\n";
            std::cout << "Открытый ключ B (Yb): " << Yb << "\n";
            std::cout << "Общий ключ, вычисленный A: " << Ka << "\n";
            std::cout << "Общий ключ, вычисленный B: " << Kb << "\n";
            std::cout << "Ключи совпадают: " << (Ka == Kb ? "да" : "нет") << "\n";
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }

        else {
            clear_console();
            std::cout << "Неверный выбор\n";
            std::cout << "Нажмите Enter для продолжения...";
            std::cin.get();
        }
    }
    return 0;
}