from enum import Enum
from typing import List, Optional
import re
from itertools import combinations


class RationalNumber:
    NULL = None
    UNITY = None
    NEGATIVE_UNITY = None

    def __init__(self, top: str | int | float, bottom: int = 1):
        self.top, self.bottom = self.parse_fraction(top, bottom)
        self.reduce()

    def parse_fraction(self, top: str | int | float, bottom: int = 1) -> tuple[int, int]:
        if isinstance(top, str):
            parts = top.split('/')
            top_val = int(parts[0])
            bottom_val = 1 if len(parts) == 1 else int(parts[1])
        else:
            top_val = int(top)
            bottom_val = int(bottom)
        return top_val, bottom_val

    def normalize_sign(self) -> None:
        if self.bottom < 0:
            self.top = -self.top
            self.bottom = -self.bottom

    def reduce(self) -> None:
        gcd = self.find_gcd(abs(self.top), abs(self.bottom))
        self.top //= gcd
        self.bottom //= gcd
        self.normalize_sign()

    def find_gcd(self, a: int, b: int) -> int:
        return a if b == 0 else self.find_gcd(b, a % b)

    def check_division_by_zero(self, other: 'RationalNumber', operation: str) -> None:
        if operation == 'quotient' and other.top == 0:
            raise ValueError("Деление на ноль")

    def get_operation_result(self, other: 'RationalNumber', operation: str) -> tuple[int, int]:
        operations = {
            'sum': (self.top * other.bottom + other.top * self.bottom, self.bottom * other.bottom),
            'difference': (self.top * other.bottom - other.top * self.bottom, self.bottom * other.bottom),
            'product': (self.top * other.top, self.bottom * other.bottom),
            'quotient': (self.top * other.bottom, self.bottom * other.top)
        }
        return operations[operation]

    def compute_fraction(self, other: 'RationalNumber', operation: str) -> 'RationalNumber':
        self.check_division_by_zero(other, operation)
        top, bottom = self.get_operation_result(other, operation)
        return RationalNumber(top, bottom)

    def sum(self, other: 'RationalNumber') -> 'RationalNumber':
        return self.compute_fraction(other, 'sum')

    def difference(self, other: 'RationalNumber') -> 'RationalNumber':
        return self.compute_fraction(other, 'difference')

    def product(self, other: 'RationalNumber') -> 'RationalNumber':
        return self.compute_fraction(other, 'product')

    def quotient(self, other: 'RationalNumber') -> 'RationalNumber':
        return self.compute_fraction(other, 'quotient')

    def invert(self) -> 'RationalNumber':
        return RationalNumber(-self.top, self.bottom)

    def absolute(self) -> 'RationalNumber':
        return RationalNumber(abs(self.top), self.bottom)

    def order(self, other: 'RationalNumber') -> int:
        diff = self.difference(other)
        if diff.top == 0:
            return 0
        return 1 if diff.top > 0 else -1

    def is_equal(self, other: 'RationalNumber') -> bool:
        return self.top * other.bottom == other.top * self.bottom

    def format_fraction(self) -> str:
        return str(self.top) if self.bottom == 1 else f"{self.top}/{self.bottom}"

    def __str__(self) -> str:
        return self.format_fraction()

    def to_float(self) -> float:
        return self.top / self.bottom

    @property
    def top(self) -> int:
        return self._top

    @top.setter
    def top(self, value: int) -> None:
        self._top = value

    @property
    def bottom(self) -> int:
        return self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom = value


RationalNumber.NULL = RationalNumber(0)
RationalNumber.UNITY = RationalNumber(1)
RationalNumber.NEGATIVE_UNITY = RationalNumber(-1)


class RestrictionType(Enum):
    BELOW = 'BELOW'
    ABOVE = 'ABOVE'
    EQUALS = 'EQUALS'


class Limit:
    def __init__(self, kind: RestrictionType = RestrictionType.BELOW, factors: List[RationalNumber] = [], right_side: RationalNumber = RationalNumber(0)):
        self.kind = kind
        self.factors = factors
        self.right_side = right_side


class Goal:
    def __init__(self, maximize: bool = False, factors: List[RationalNumber] = [], offset: RationalNumber = RationalNumber(0)):
        self.maximize = maximize
        self.factors = factors
        self.offset = offset


class LinearProblem:
    def __init__(self, goal: Optional[Goal] = None, restrictions: Optional[List[Limit]] = None):
        self.goal = goal or Goal(False, [])
        self.restrictions = restrictions or []


class CanonicalForm:
    def __init__(self):
        self.maximize = False
        self.goal_factors: List[RationalNumber] = []
        self.goal_offset = RationalNumber(0)
        self.restriction_matrix: List[List[RationalNumber]] = []
        self.right_sides: List[RationalNumber] = []
        self.base_indices: List[int] = []
        self.aux_vars = 0


class LinearTable:
    def populate_matrix(self, z_row: List[RationalNumber], gauss_matrix: List[List[RationalNumber]]) -> None:
        self.matrix.append(z_row)
        for row in gauss_matrix:
            self.matrix.append(row[:])

    def __init__(self, canonical_form: CanonicalForm):
        self.maximize = canonical_form.maximize
        self.aux_vars = canonical_form.aux_vars
        self.matrix = []
        self.base_indices = []

        gauss_matrix = self.initialize_matrix(canonical_form)
        try:
            self.base_indices = MatrixSolver.find_optimal_base(gauss_matrix)
        except ValueError as e:
            raise ValueError(f"Нет допустимого решения: {str(e)}")

        z_row = self.build_z_row(canonical_form)
        self.populate_matrix(z_row, gauss_matrix)
        self.extend_matrix_rows(self.matrix)
        self.apply_base_transformations()

    def initialize_matrix(self, canonical_form: CanonicalForm) -> List[List[RationalNumber]]:
        gauss_matrix = [row[:] for row in canonical_form.restriction_matrix]
        for i in range(len(gauss_matrix)):
            gauss_matrix[i].append(canonical_form.right_sides[i])
        return gauss_matrix

    def build_z_row(self, canonical_form: CanonicalForm) -> List[RationalNumber]:
        z_row = [factor.invert() for factor in canonical_form.goal_factors]
        z_row.append(canonical_form.goal_offset)
        return z_row

    def extend_matrix_rows(self, matrix: List[List[RationalNumber]]) -> None:
        width = len(matrix[0])
        for row in matrix:
            while len(row) < width:
                row.append(RationalNumber.NULL)

    def apply_base_transformations(self) -> None:
        for i, base_col in enumerate(self.base_indices):
            if base_col < len(self.matrix[0]) - 1:
                if not self.transform(i + 1, base_col):
                    raise ValueError("Не удалось создать таблицу: нет допустимых базисов")

    def normalize_pivot_row(self, pivot_row: int, pivot_col: int) -> bool:
        pivot_element = self.matrix[pivot_row][pivot_col]
        if pivot_element.is_equal(RationalNumber.NULL):
            return False
        for j in range(len(self.matrix[pivot_row])):
            self.matrix[pivot_row][j] = self.matrix[pivot_row][j].quotient(pivot_element)
        return True

    def update_other_rows(self, pivot_row: int, pivot_col: int) -> None:
        for i in range(len(self.matrix)):
            if i != pivot_row:
                factor = self.matrix[i][pivot_col]
                for j in range(len(self.matrix[i])):
                    self.matrix[i][j] = self.matrix[i][j].difference(
                        factor.product(self.matrix[pivot_row][j])
                    )

    def transform(self, pivot_row: int, pivot_col: int) -> bool:
        try:
            if not self.normalize_pivot_row(pivot_row, pivot_col):
                return False
            self.update_other_rows(pivot_row, pivot_col)
            return True
        except ValueError as e:
            print(f"Ошибка: {str(e)}")
            return False

    def __str__(self) -> str:
        return "\n".join("\t".join(cell.__str__() for cell in row) for row in self.matrix)


class LinearOptimizer:
    def perform_iteration(self, table: LinearTable, step: int) -> Optional[bool]:
        print(f"\nИтерация {step}:")
        TableFormatter.display_table(table)

        if self.is_optimized(table):
            return True

        incoming_col = self.choose_incoming_variable(table)
        if incoming_col == -1:
            print("Функция не ограничена")
            return False

        outgoing_row = self.choose_outgoing_variable(table, incoming_col)
        if outgoing_row == -1:
            print("Функция не ограничена")
            return False

        self.transform(table, outgoing_row, incoming_col)
        return None

    def display_final_result(self, table: LinearTable) -> None:
        if self.is_optimized(table):
            print("\nТаблица оптимальных решений:")
            TableFormatter.display_table(table)
            self.explore_alternatives(table)
        else:
            print("\nНе удалось найти оптимального решения.")

    def optimize(self, table: LinearTable) -> None:
        step = 0
        while True:
            step += 1
            result = self.perform_iteration(table, step)
            if result is not None:
                break
        self.display_final_result(table)

    def is_optimized(self, table: LinearTable) -> bool:
        z_row = table.matrix[0]
        return all(z_row[i].order(RationalNumber.NULL) >= 0 for i in range(len(z_row) - 1))

    def choose_incoming_variable(self, table: LinearTable) -> int:
        z_row = table.matrix[0]
        incoming_col = -1
        min_val = RationalNumber.NULL
        for i in range(len(z_row) - 1):
            if z_row[i].order(min_val) < 0:
                min_val = z_row[i]
                incoming_col = i
        return incoming_col

    def choose_outgoing_variable(self, table: LinearTable, incoming_col: int) -> int:
        outgoing_row = -1
        min_ratio: Optional[RationalNumber] = None
        for i in range(1, len(table.matrix)):
            row = table.matrix[i]
            a = row[incoming_col]
            b = row[-1]
            if a.order(RationalNumber.NULL) > 0:
                ratio = b.quotient(a)
                if min_ratio is None or ratio.order(min_ratio) < 0:
                    min_ratio = ratio
                    outgoing_row = i
        return outgoing_row

    def transform(self, table: LinearTable, pivot_row: int, pivot_col: int) -> None:
        pivot_row_values = table.matrix[pivot_row]
        pivot_element = pivot_row_values[pivot_col]

        for j in range(len(pivot_row_values)):
            pivot_row_values[j] = pivot_row_values[j].quotient(pivot_element)

        table.base_indices[pivot_row - 1] = pivot_col

        for i in range(len(table.matrix)):
            if i != pivot_row:
                current_row = table.matrix[i]
                factor = current_row[pivot_col]
                for j in range(len(current_row)):
                    if j == pivot_col:
                        current_row[j] = RationalNumber.NULL
                        continue
                    current_row[j] = current_row[j].difference(
                        factor.product(pivot_row_values[j])
                    )

    def explore_alternatives(self, table: LinearTable) -> None:
        z_row = table.matrix[0]
        num_vars = len(z_row) - 1
        has_alternative = False
        for i in range(num_vars):
            if i not in table.base_indices and z_row[i].is_equal(RationalNumber.NULL):
                has_alternative = True
                self.display_parametric(table, i)
                break
        if not has_alternative:
            self.display_basic(table)

    def display_basic(self, table: LinearTable) -> None:
        num_vars = len(table.matrix[0]) - 1
        solution = [RationalNumber.NULL] * num_vars
        for i in range(1, len(table.matrix)):
            var_index = table.base_indices[i - 1]
            solution[var_index] = table.matrix[i][-1]
        z_value = table.matrix[0][-1]
        print("\нОтвет:")
        print(
            f"Оптимальное значение: Z{'max' if table.maximize else 'min'}({', '.join(str(x) for x in solution[:num_vars - table.aux_vars])}) = {z_value}"
        )

    def format_parametric_solution(self, point_a: List[RationalNumber], point_b: List[RationalNumber], num_vars: int, aux_vars: int) -> List[str]:
        solution_str = []
        for i in range(num_vars - aux_vars):
            part2 = point_a[i].difference(point_b[i])
            is_positive = part2.order(RationalNumber.NULL) >= 0
            solution_str.append(f"{point_b[i]}{' + ' if is_positive else ' - '}" + f"{part2.absolute()} * l")
        return solution_str

    def display_parametric(self, table: LinearTable, free_col: int) -> None:
        num_vars = len(table.matrix[0]) - 1
        point_a = self.get_solution(table)
        outgoing_row = self.choose_outgoing_variable(table, free_col)
        if outgoing_row == -1:
            print("Альтернативное оптимальное решение неограниченно.")
            return
        self.transform(table, outgoing_row, free_col)
        print("Альтернативное решение:")
        TableFormatter.display_table(table)
        point_b = self.get_solution(table)
        z_value = table.matrix[0][-1]
        print("\nОтвет:")
        solution_str = self.format_parametric_solution(point_a, point_b, num_vars, table.aux_vars)
        print(f"Оптимальное значение: Zmin({', '.join(solution_str)}) = -{z_value}")

    def get_solution(self, table: LinearTable) -> List[RationalNumber]:
        num_vars = len(table.matrix[0]) - 1
        solution = [RationalNumber.NULL] * num_vars
        for i in range(1, len(table.matrix)):
            var_index = table.base_indices[i - 1]
            solution[var_index] = table.matrix[i][-1]
        return solution


class MatrixSolver:
    logging_enabled = True

    @classmethod
    def log(cls, msg: str = "") -> None:
        if cls.logging_enabled:
            print(msg)

    @classmethod
    def binomial_coefficient(cls, n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        k = min(k, n - k)
        numerator = 1
        denominator = 1
        for i in range(k):
            numerator *= (n - i)
            denominator *= (i + 1)
        return numerator // denominator

    @classmethod
    def transform_for_base(cls, matrix: List[List[RationalNumber]], base: List[int]) -> List[List[RationalNumber]]:
        matrix_copy = cls.duplicate_matrix(matrix)
        for i in range(len(matrix)):
            base_col = base[i]
            pivot = matrix_copy[i][base_col]
            if pivot.is_equal(RationalNumber.NULL):
                cls.log("Нулевой поворот, пропуск базиса")
                cls.display_matrix(matrix_copy)
                raise ValueError("Нулевой поворот")
            for j in range(len(matrix_copy[i])):
                matrix_copy[i][j] = matrix_copy[i][j].quotient(pivot)
            for k in range(len(matrix)):
                if k != i:
                    factor = matrix_copy[k][base_col]
                    for j in range(len(matrix_copy[k])):
                        matrix_copy[k][j] = matrix_copy[k][j].difference(
                            factor.product(matrix_copy[i][j])
                        )
        return matrix_copy

    @classmethod
    def find_optimal_base(cls, matrix: List[List[RationalNumber]]) -> List[int]:
        rows = len(matrix)
        cols = len(matrix[0]) - 1
        cls.log(f"\nФормула количества комбинаций: C({cols}, {rows}) = {cols}! / ({rows}! * ({cols}-{rows})!)")
        all_combinations = cls.get_subsets(cols, rows)
        cls.log(f"Все возможные комбинации: {len(all_combinations)}")

        best_base = None
        min_negative_rhs = float('inf')
        max_zeros = -1

        for base in all_combinations:
            cls.log(f"\nПроверка базиса: {base}")
            negative_count = 0
            zero_count = 0
            try:
                matrix_copy = cls.transform_for_base(matrix, base)
                for i in range(rows):
                    rhs = matrix_copy[i][cols]
                    if rhs.order(RationalNumber.NULL) < 0:
                        negative_count += 1
                    elif rhs.is_equal(RationalNumber.NULL):
                        zero_count += 1

                cls.log(f"Результат проверки базиса {base}:")
                cls.log(f"Отрицательных правых частей: {negative_count}")
                cls.display_matrix(matrix_copy)

                if negative_count == 0:
                    cls.log(f"Базис подходит: {base} (нет отрицательных правых частей)")
                    return base
                elif negative_count < min_negative_rhs or (negative_count == min_negative_rhs and zero_count > max_zeros):
                    best_base = list(base)
                    min_negative_rhs = negative_count
                    max_zeros = zero_count
                else:
                    cls.log(f"Базис не лучше текущего лучшего: {base}")
            except ValueError as e:
                cls.log(f"Ошибка при проверке базиса {base}: {str(e)}")
                continue

        if best_base is not None:
            cls.log(f"\nЛучший найденный базис: {best_base} (не идеальный, но с минимальными отрицательными: {min_negative_rhs}, нули: {max_zeros})")
            return best_base
        else:
            cls.log("\nНи один базис не подошел")
            cls.display_matrix(matrix)
            raise ValueError("Базис не найден")

    @classmethod
    def display_matrix(cls, matrix: List[List[RationalNumber]]) -> None:
        if not matrix:
            cls.log("| |")
            cls.log(" - ")
            return

        col_widths = [0] * len(matrix[0])
        for row in matrix:
            for j, cell in enumerate(row):
                col_widths[j] = max(col_widths[j], len(str(cell)))

        top_border = "┌" + "─".join("─" * (width + 2) for width in col_widths) + "┐"
        cls.log(top_border)

        for row in matrix:
            cells = [f" {str(cell):<{width}} " for cell, width in zip(row, col_widths)]
            cls.log("│" + "│".join(cells) + "│")

        bottom_border = "└" + "─".join("─" * (width + 2) for width in col_widths) + "┘"
        cls.log(bottom_border)

    @classmethod
    def gauss_jordan(cls, matrix: List[List[RationalNumber]]) -> None:
        row_count = len(matrix)
        col_count = len(matrix[0])

        cls.log("Стартовая матрица:\n")
        cls.display_matrix(matrix)

        n = 0
        for m in range(col_count - 1):
            if n >= row_count:
                break
            pivot_row = n
            for i in range(n + 1, row_count):
                if matrix[i][m].absolute().order(matrix[pivot_row][m].absolute()) > 0:
                    pivot_row = i
            if matrix[pivot_row][m].is_equal(RationalNumber.NULL):
                continue

            matrix[n], matrix[pivot_row] = matrix[pivot_row], matrix[n]
            cls.log(f"\nЗамена местами строк {cls.get_roman(n + 1)} и {cls.get_roman(pivot_row + 1)}\n")
            cls.display_matrix(matrix)

            pivot = matrix[n][m]
            for j in range(col_count):
                matrix[n][j] = matrix[n][j].quotient(pivot)
            cls.log(f"\nПосле нормализации строки {cls.get_roman(n + 1)}:\n")
            cls.display_matrix(matrix)

            for i in range(row_count):
                if i != n:
                    factor = matrix[i][m]
                    for j in range(col_count):
                        matrix[i][j] = matrix[i][j].difference(factor.product(matrix[n][j]))
                    cls.log(f"\n{cls.get_roman(i + 1)} - ({factor}) * {cls.get_roman(n + 1)}\n")
                    cls.display_matrix(matrix)

            n += 1

        cls.log("\nРезультат:\n")
        cls.display_matrix(matrix)

    @classmethod
    def get_subsets(cls, n: int, m: int) -> List[List[int]]:
        return [list(combo) for combo in combinations(range(n), m)]

    @classmethod
    def duplicate_matrix(cls, matrix: List[List[RationalNumber]]) -> List[List[RationalNumber]]:
        return [[RationalNumber(cell.top, cell.bottom) for cell in row] for row in matrix]

    @classmethod
    def get_roman(cls, number: int) -> str:
        return f"({number})"


class ProblemReader:
    @staticmethod
    def read_problem(file_path: str) -> 'LinearProblem':
        problem = LinearProblem()
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            if line.startswith('Z :'):
                problem.goal = ProblemReader.read_goal(line)
            else:
                problem.restrictions.append(ProblemReader.read_restriction(line))
        return problem

    @staticmethod
    def read_goal(line: str) -> 'Goal':
        line = line[3:].strip()
        maximize = 'max' in line
        expr = re.sub(r'->\s*(max|min)', '', line).strip()
        goal = Goal(maximize=maximize)
        ProblemReader.read_terms(expr, goal.factors, goal.offset)
        return goal

    @staticmethod
    def read_restriction(line: str) -> 'Limit':
        restriction = Limit()
        if '<=' in line:
            operator = '<='
            restriction.kind = RestrictionType.BELOW
        elif '>=' in line:
            operator = '>='
            restriction.kind = RestrictionType.ABOVE
        elif '=' in line:
            operator = '='
            restriction.kind = RestrictionType.EQUALS
        else:
            raise ValueError(f"Недопустимое ограничение: {line}")

        parts = line.split(operator)
        if len(parts) != 2:
            raise ValueError(f"Недопустимый формат ограничения: {line}")
        left_part = parts[0].strip()
        right_part = parts[1].strip()

        restriction.factors = []
        ProblemReader.read_terms(left_part, restriction.factors, RationalNumber.NULL)
        try:
            restriction.right_side = RationalNumber(right_part)
        except ValueError:
            raise ValueError(f"Недопустимая правая часть в ограничении: {right_part}")
        return restriction

    @staticmethod
    def read_terms(expr: str, factors: List[RationalNumber], offset: RationalNumber) -> None:
        factors.clear()
        terms = re.findall(r'([+-]?\s*\d*\.?\d*\s*x\d+|[+-]?\s*\d+\.?\d*|[+-]?\s*x\d+)', expr)
        max_var_index = 0
        for term in terms:
            term = term.strip()
            if not term:
                continue
            if 'x' in term:
                match = re.match(r'([+-]?\s*\d*\.?\d*)?\s*x(\d+)', term)
                if not match:
                    raise ValueError(f"Недопустимый термин: {term}")
                factor_str = match.group(1).strip() if match.group(1) else ''
                var_index = int(match.group(2)) - 1

                if factor_str in ('', '+'):
                    factor = '1'
                elif factor_str == '-':
                    factor = '-1'
                else:
                    factor = factor_str.replace(' ', '')
                if factor.startswith('+'):
                    factor = factor[1:]
                factor_value = RationalNumber(factor)
                while len(factors) <= var_index:
                    factors.append(RationalNumber.NULL)
                factors[var_index] = factor_value
                max_var_index = max(max_var_index, var_index)
            else:
                try:
                    offset.sum(RationalNumber(term.replace(' ', '')))
                except ValueError:
                    raise ValueError(f"Недопустимый постоянный термин: {term}")

        while len(factors) <= max_var_index:
            factors.append(RationalNumber.NULL)


class FormTransformer:
    @staticmethod
    def transform(problem: 'LinearProblem') -> 'CanonicalForm':
        canonical_form = CanonicalForm()
        canonical_form.maximize = True if not problem.goal.maximize else problem.goal.maximize  # min -> max, max остается max
        canonical_form.goal_offset = problem.goal.offset
        original_var_count = FormTransformer.count_original_vars(problem)

        canonical_form.goal_factors = (problem.goal.factors if problem.goal.maximize else [factor.invert() for factor in problem.goal.factors])

        aux_counter = 0
        canonical_form.base_indices = []

        for restriction in problem.restrictions:
            row = restriction.factors[:]
            while len(row) < original_var_count:
                row.append(RationalNumber.NULL)
            if restriction.kind == RestrictionType.BELOW:
                FormTransformer.add_positive_aux(row, aux_counter)
                canonical_form.base_indices.append(original_var_count + aux_counter)
                aux_counter += 1
            elif restriction.kind == RestrictionType.ABOVE:
                FormTransformer.add_negative_aux(row, aux_counter)
                aux_counter += 1
            elif restriction.kind == RestrictionType.EQUALS:
                pass
            canonical_form.restriction_matrix.append(row)
            canonical_form.right_sides.append(restriction.right_side)

        for i in range(len(canonical_form.right_sides)):
            if canonical_form.right_sides[i].order(RationalNumber.NULL) < 0:
                canonical_form.restriction_matrix[i] = [factor.invert() for factor in canonical_form.restriction_matrix[i]]
                canonical_form.right_sides[i] = canonical_form.right_sides[i].invert()

        total_vars = original_var_count + aux_counter
        canonical_form.aux_vars = aux_counter

        for row in canonical_form.restriction_matrix:
            while len(row) < total_vars:
                row.append(RationalNumber.NULL)
        while len(canonical_form.goal_factors) < total_vars:
            canonical_form.goal_factors.append(RationalNumber.NULL)

        print("\nКаноническая форма:")
        terms = []
        first_term = True
        for i, factor in enumerate(canonical_form.goal_factors):
            if not factor.is_equal(RationalNumber.NULL):
                if first_term:
                    terms.append(f"{factor}x{i + 1}")
                    first_term = False
                else:
                    sign = '+' if factor.order(RationalNumber.NULL) > 0 else '-'
                    terms.append(f" {sign} {factor.absolute()}x{i + 1}")
        goal_str = "".join(terms).strip()
        if not canonical_form.goal_offset.is_equal(RationalNumber.NULL):
            sign = '+' if canonical_form.goal_offset.order(RationalNumber.NULL) > 0 else '-'
            goal_str += f" {sign} {canonical_form.goal_offset.absolute()}"
        print("Уравнение Z:")
        print(f"Z = {goal_str} -> {'max' if canonical_form.maximize else 'min'}")


        restriction_lines = []
        for i, row in enumerate(canonical_form.restriction_matrix):
            terms = []
            first_term = True
            for j, factor in enumerate(row):
                if not factor.is_equal(RationalNumber.NULL):
                    if first_term:
                        terms.append(f"{factor}x{j + 1}")
                        first_term = False
                    else:
                        sign = '+' if factor.order(RationalNumber.NULL) > 0 else '-'
                        terms.append(f" {sign} {factor.absolute()}x{j + 1}")
            restriction_line = "".join(terms).strip() + f" = {canonical_form.right_sides[i]}"
            restriction_lines.append(restriction_line)

        print("Ограничения:")
        print("{")
        for line in restriction_lines:
            print(f" {line}")
        print("}")

        initial_matrix = [row[:] for row in canonical_form.restriction_matrix]
        for i in range(len(initial_matrix)):
            initial_matrix[i].append(canonical_form.right_sides[i])

        print("\nИсходная матрица:")
        MatrixSolver.display_matrix(initial_matrix)

        print("\nВыполнение исключения по Гауссу-Джордану:")
        MatrixSolver.gauss_jordan(initial_matrix)

        print("\nМатрица после преобразований методом Гаусса-Жордана:")
        MatrixSolver.display_matrix(initial_matrix)

        return canonical_form

    @staticmethod
    def add_positive_aux(row: List[RationalNumber], aux_index: int) -> None:
        for _ in range(aux_index):
            row.append(RationalNumber.NULL)
        row.append(RationalNumber.UNITY)

    @staticmethod
    def add_negative_aux(row: List[RationalNumber], aux_index: int) -> None:
        for _ in range(aux_index):
            row.append(RationalNumber.NULL)
        row.append(RationalNumber.NEGATIVE_UNITY)

    @staticmethod
    def count_original_vars(problem: 'LinearProblem') -> int:
        max_vars = len(problem.goal.factors)
        for restriction in problem.restrictions:
            max_vars = max(max_vars, len(restriction.factors))
        return max_vars


class TableFormatter:
    @staticmethod
    def format_problem(problem: 'LinearProblem') -> None:
        pass

    @staticmethod
    def display_table(table: 'LinearTable') -> None:
        width = len(table.matrix[0])
        headers = [f"x{i + 1}" for i in range(width - 1)] + ["1"]
        rows = []

        basis_vars = []
        basis_vars.append("Z")
        rows.append(table.matrix[0])

        for i in range(1, len(table.matrix)):
            basis_var = f"x{table.base_indices[i - 1] + 1}" if i - 1 < len(table.base_indices) else '-'
            basis_vars.append(basis_var)
            rows.append(table.matrix[i])

        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]
        col_widths = [max(w, len(h)) for w, h in zip(col_widths, headers)]
        basis_col_width = max(len(basis_var) for basis_var in basis_vars + ["Базис"])

        top_border = "┌" + "─" * (basis_col_width + 2) + "┬" + "─".join("─" * (w + 2) for w in col_widths) + "┐"
        print(top_border)

        header_cells = [f" {'Базис':<{basis_col_width}} "] + [f" {h:<{w}} " for h, w in zip(headers, col_widths)]
        print("│" + "│".join(header_cells) + "│")

        separator = "├" + "─" * (basis_col_width + 2) + "┼" + "─".join("─" * (w + 2) for w in col_widths) + "┤"
        print(separator)

        for basis_var, row in zip(basis_vars, rows):
            cells = [f" {basis_var:<{basis_col_width}} "] + [f" {str(cell):<{w}} " for cell, w in zip(row, col_widths)]
            print("│" + "│".join(cells) + "│")

        bottom_border = "└" + "─" * (basis_col_width + 2) + "┴" + "─".join("─" * (w + 2) for w in col_widths) + "┘"
        print(bottom_border)

    @staticmethod
    def get_symbol(kind: 'RestrictionType') -> str:
        return {
            RestrictionType.BELOW: '<=',
            RestrictionType.ABOVE: '>=',
            RestrictionType.EQUALS: '='
        }[kind]


def load_problem(file_path: str) -> 'LinearProblem':
    return ProblemReader.read_problem(file_path)


def main():
    while True:
        try:
            file_name = input("Введите название текстового файла с задачей: ")
            problem = load_problem(file_name)
            break
        except FileNotFoundError:
            print(f"Ошибка: Файл '{file_name}' не найден. Пожалуйста, введите корректное название файла.")
        except Exception as e:
            print(f"Ошибка при обработке файла: {str(e)}")
            break

    try:
        TableFormatter.format_problem(problem)
        canonical_form = FormTransformer.transform(problem)
        table = LinearTable(canonical_form)

        print("\nПервоначальная таблица:")
        TableFormatter.display_table(table)

        optimizer = LinearOptimizer()
        optimizer.optimize(table)
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    main()
