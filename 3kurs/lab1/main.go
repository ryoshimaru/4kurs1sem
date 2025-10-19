// main.go
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"math/big"
	"os"
	"strconv"
	"strings"
)

type Frac struct {
	// num/den, den > 0, gcd(|num|, den) = 1
	num *big.Int
	den *big.Int
}

func NewFracInt(v int64) Frac {
	return Frac{big.NewInt(v), big.NewInt(1)}
}
func NewFrac(num, den *big.Int) Frac {
	f := Frac{new(big.Int).Set(num), new(big.Int).Set(den)}
	normalize(&f)
	return f
}
func NewFracFromString(s string) (Frac, error) {
	// поддержка форматов: "a", "a/b"
	if strings.Contains(s, "/") {
		parts := strings.SplitN(s, "/", 2)
		n, ok1 := new(big.Int).SetString(strings.TrimSpace(parts[0]), 10)
		d, ok2 := new(big.Int).SetString(strings.TrimSpace(parts[1]), 10)
		if !ok1 || !ok2 {
			return Frac{}, errors.New("bad fraction: " + s)
		}
		return NewFrac(n, d), nil
	}
	// целое
	if i, err := strconv.ParseInt(strings.TrimSpace(s), 10, 64); err == nil {
		return NewFracInt(i), nil
	}
	// big-int
	if bi, ok := new(big.Int).SetString(strings.TrimSpace(s), 10); ok {
		return NewFrac(bi, big.NewInt(1)), nil
	}
	return Frac{}, errors.New("bad number: " + s)
}

func zero() Frac { return Frac{big.NewInt(0), big.NewInt(1)} }
func one() Frac  { return Frac{big.NewInt(1), big.NewInt(1)} }

func normalize(a *Frac) {
	if a.den.Sign() == 0 {
		panic("denominator is zero")
	}
	// перенесем знак в числитель
	if a.den.Sign() < 0 {
		a.den.Neg(a.den)
		a.num.Neg(a.num)
	}
	// сократим
	g := new(big.Int).GCD(nil, nil, abs(a.num), a.den)
	if g.Cmp(big.NewInt(1)) != 0 {
		a.num.Div(a.num, g)
		a.den.Div(a.den, g)
	}
}

func abs(x *big.Int) *big.Int {
	if x.Sign() < 0 {
		return new(big.Int).Neg(x)
	}
	return new(big.Int).Set(x)
}

func (a Frac) IsZero() bool { return a.num.Sign() == 0 }
func (a Frac) Neg() Frac    { return Frac{new(big.Int).Neg(a.num), new(big.Int).Set(a.den)} }

func (a Frac) Add(b Frac) Frac {
	num := new(big.Int).Add(new(big.Int).Mul(a.num, b.den), new(big.Int).Mul(b.num, a.den))
	den := new(big.Int).Mul(a.den, b.den)
	return NewFrac(num, den)
}
func (a Frac) Sub(b Frac) Frac { return a.Add(b.Neg()) }
func (a Frac) Mul(b Frac) Frac {
	num := new(big.Int).Mul(a.num, b.num)
	den := new(big.Int).Mul(a.den, b.den)
	return NewFrac(num, den)
}
func (a Frac) Div(b Frac) Frac {
	if b.num.Sign() == 0 {
		panic("division by zero")
	}
	num := new(big.Int).Mul(a.num, b.den)
	den := new(big.Int).Mul(a.den, b.num)
	return NewFrac(num, den)
}
func (a Frac) CmpAbs(b Frac) int {
	// сравнение |a| и |b|
	left := new(big.Int).Mul(abs(a.num), b.den)
	right := new(big.Int).Mul(abs(b.num), a.den)
	return left.Cmp(right)
}
func (a Frac) String() string {
	if a.den.Cmp(big.NewInt(1)) == 0 {
		return a.num.String()
	}
	return a.num.String() + "/" + a.den.String()
}

func readAugMatrix(r io.Reader) (m, n int, A [][]Frac) {
	in := bufio.NewScanner(r)
	in.Split(bufio.ScanLines)

	var header []string
	for in.Scan() {
		line := strings.TrimSpace(in.Text())
		if line == "" {
			continue
		}
		header = fields(line)
		break
	}
	if len(header) < 2 {
		panic("ожидались m n в первой строке")
	}
	var err error
	m, err = strconv.Atoi(header[0])
	if err != nil {
		panic("m не int")
	}
	n, err = strconv.Atoi(header[1])
	if err != nil {
		panic("n не int")
	}

	A = make([][]Frac, m)
	row := 0
	for in.Scan() && row < m {
		line := strings.TrimSpace(in.Text())
		if line == "" {
			continue
		}
		toks := fields(line)
		if len(toks) != n+1 {
			panic(fmt.Sprintf("в строке %d ожидалось %d значений, получено %d", row+1, n+1, len(toks)))
		}
		A[row] = make([]Frac, n+1)
		for j := 0; j < n+1; j++ {
			f, e := NewFracFromString(toks[j])
			if e != nil {
				panic(e)
			}
			A[row][j] = f
		}
		row++
	}
	if row != m {
		panic("недостаточно строк матрицы")
	}
	return
}

func fields(s string) []string {
	// допускаем разделители: пробелы и табы
	return strings.Fields(s)
}

func printMatrix(step string, A [][]Frac, n int) {
	fmt.Println(step)
	m := len(A)
	// найдём ширину столбцов для аккуратного вывода
	width := make([]int, n+1)
	for i := 0; i < m; i++ {
		for j := 0; j < n+1; j++ {
			l := len(A[i][j].String())
			if l > width[j] {
				width[j] = l
			}
		}
	}
	for i := 0; i < m; i++ {
		fmt.Print("| ")
		for j := 0; j < n; j++ {
			s := A[i][j].String()
			fmt.Printf("%*s ", width[j], s)
		}
		fmt.Print("| ")
		fmt.Printf("%*s", width[n], A[i][n].String())
		fmt.Println(" |")
	}
	fmt.Println()
}

type RREFResult struct {
	R        [][]Frac
	pivCols  []int
	rankA    int
	rankAb   int
	unique   bool
	infinite bool
	none     bool
}

func gaussJordanWithSteps(A [][]Frac, n int) RREFResult {
	m := len(A)
	R := make([][]Frac, m)
	for i := 0; i < m; i++ {
		R[i] = make([]Frac, n+1)
		copy(R[i], A[i])
	}
	printMatrix("Стартовая расширенная матрица [A|b]:", R, n)

	row := 0
	var pivCols []int
	stepNo := 1

	for col := 0; col < n && row < m; col++ {
		//тут мы сравниваем pivot (ищем максимальный элемент в столбце по модулю для перестановки)
		pivot := -1
		for r := row; r < m; r++ {
			if !R[r][col].IsZero() {
				if pivot == -1 || R[r][col].CmpAbs(R[pivot][col]) > 0 {
					pivot = r
				}
			}
		}
		if pivot == -1 {
			continue
		}

		if pivot != row {
			R[row], R[pivot] = R[pivot], R[row]
			printMatrix(fmt.Sprintf("Шаг %d: перестановка строк r%d <-> r%d", stepNo, row+1, pivot+1), R, n)
			stepNo++
		}
		// делим на ведущий элемент, чтобы осталась единица
		lead := R[row][col]
		for j := col; j <= n; j++ {
			R[row][j] = R[row][j].Div(lead)
		}
		printMatrix(fmt.Sprintf("Шаг %d: нормировка строки r%d (делим на ведущий элемент)", stepNo, row+1), R, n)
		stepNo++

		// зануляем все остальные элементы в колонке col
		for r := 0; r < m; r++ {
			if r == row {
				continue
			}
			if !R[r][col].IsZero() {
				f := R[r][col]
				for j := col; j <= n; j++ {
					R[r][j] = R[r][j].Sub(f.Mul(R[row][j]))
				}
			}
		}
		printMatrix(fmt.Sprintf("Шаг %d: обнуление столбца %d (кроме ведущей строки)", stepNo, col+1), R, n)
		stepNo++

		pivCols = append(pivCols, col)
		row++
	}

	rankA := 0
	for i := 0; i < m; i++ {
		allZero := true
		for j := 0; j < n; j++ {
			if !R[i][j].IsZero() {
				allZero = false
				break
			}
		}
		if !allZero {
			rankA++
		}
	}
	rankAb := 0
	for i := 0; i < m; i++ {
		allZero := true
		for j := 0; j < n+1; j++ {
			if !R[i][j].IsZero() {
				allZero = false
				break
			}
		}
		if !allZero {
			rankAb++
		}
	}

	res := RREFResult{
		R:       R,
		pivCols: pivCols,
		rankA:   rankA,
		rankAb:  rankAb,
	}

	switch {
	case hasInconsistentRow(R, n):
		res.none = true
	case rankA == n:
		res.unique = true
	case rankA < n:
		res.infinite = true
	}
	return res
}

func hasInconsistentRow(R [][]Frac, n int) bool {
	for i := 0; i < len(R); i++ {
		allZero := true
		for j := 0; j < n; j++ {
			if !R[i][j].IsZero() {
				allZero = false
				break
			}
		}
		if allZero && !R[i][n].IsZero() {
			return true
		}
	}
	return false
}

func uniqueSolution(res RREFResult, n int) []Frac {
	x := make([]Frac, n)
	// В RREF в ведущих столбцах стоят единицы и нули в остальных строках
	// Пройдём по строкам, найдём ведущие 1 и выпишем b
	for i := 0; i < len(res.R); i++ {
		pivotCol := -1
		for j := 0; j < n; j++ {
			if res.R[i][j].String() == "1" {
				// в строке это первая ненулевая?
				onlyLeading := true
				for k := 0; k < j; k++ {
					if !res.R[i][k].IsZero() {
						onlyLeading = false
						break
					}
				}
				if onlyLeading {
					pivotCol = j
					break
				}
			}
		}
		if pivotCol >= 0 && pivotCol < n {
			x[pivotCol] = res.R[i][n]
		}
	}
	return x
}

type GeneralSolution struct {
	particular []Frac
	freeIdx    []int
	basis      [][]Frac
}

func generalSolution(res RREFResult, n int) GeneralSolution {
	m := len(res.R)
	isPivot := make([]bool, n)
	for _, c := range res.pivCols {
		isPivot[c] = true
	}
	var freeIdx []int
	for j := 0; j < n; j++ {
		if !isPivot[j] {
			freeIdx = append(freeIdx, j)
		}
	}

	part := make([]Frac, n)
	for i := 0; i < m; i++ {
		lead := -1
		for j := 0; j < n; j++ {
			if res.R[i][j].String() == "1" {
				allZeroLeft := true
				for k := 0; k < j; k++ {
					if !res.R[i][k].IsZero() {
						allZeroLeft = false
						break
					}
				}
				if allZeroLeft {
					lead = j
					break
				}
			}
		}
		if lead != -1 {
			part[lead] = res.R[i][n]
		}
	}

	var basis [][]Frac
	for _, f := range freeIdx {
		v := make([]Frac, n)
		for _, g := range freeIdx {
			if g == f {
				v[g] = one()
			} else {
				v[g] = zero()
			}
		}
		for i := 0; i < m; i++ {
			lead := -1
			for j := 0; j < n; j++ {
				if res.R[i][j].String() == "1" {
					// ведущая 1?
					allZeroLeft := true
					for k := 0; k < j; k++ {
						if !res.R[i][k].IsZero() {
							allZeroLeft = false
							break
						}
					}
					if allZeroLeft {
						lead = j
						break
					}
				}
			}
			if lead != -1 {
				sum := zero()
				// по свободным
				for _, g := range freeIdx {
					if !res.R[i][g].IsZero() {
						sum = sum.Add(res.R[i][g].Mul(v[g]))
					}
				}
				v[lead] = sum.Neg()
			}
		}
		basis = append(basis, v)
	}

	return GeneralSolution{
		particular: part,
		freeIdx:    freeIdx,
		basis:      basis,
	}
}

func main() {
	var reader io.Reader
	if len(os.Args) > 1 {
		f, err := os.Open(os.Args[1])
		if err != nil {
			fmt.Fprintln(os.Stderr, "не удалось открыть файл:", err)
			os.Exit(1)
		}
		defer f.Close()
		reader = f
	} else {
		reader = os.Stdin
	}

	defer func() {
		if r := recover(); r != nil {
			fmt.Fprintln(os.Stderr, "ошибка:", r)
			os.Exit(1)
		}
	}()

	_, n, A := readAugMatrix(reader)

	res := gaussJordanWithSteps(A, n)

	fmt.Printf("rank(A) = %d, rank([A|b]) = %d, неизвестных n = %d\n\n", res.rankA, res.rankAb, n)

	switch {
	case res.none:
		fmt.Println("Система несовместна: решений нет.")
	case res.unique:
		fmt.Println("Система совместна и определённа: единственное решение.")
		x := uniqueSolution(res, n)
		for i := 0; i < n; i++ {
			fmt.Printf("x_%d = %s\n", i+1, x[i].String())
		}
	case res.infinite:
		fmt.Println("Система совместна и неопределённа: бесконечно много решений.")
		gs := generalSolution(res, n)
		fmt.Println("\nЧастное решение (при всех свободных = 0):")
		for i := 0; i < n; i++ {
			fmt.Printf("x_%d = %s\n", i+1, gs.particular[i].String())
		}
		fmt.Print("\nСвободные переменные: ")
		for i, idx := range gs.freeIdx {
			if i > 0 {
				fmt.Print(", ")
			}
			fmt.Printf("x_%d = t_%d", idx+1, i+1)
		}
		if len(gs.freeIdx) == 0 {
			fmt.Print("—")
		}
		fmt.Println()

		for k := range gs.basis {
			fmt.Printf("Направляющий вектор при t_%d:\n", k+1)
			for i := 0; i < n; i++ {
				fmt.Printf("  x_%d компонент = %s\n", i+1, gs.basis[k][i].String())
			}
		}
	default:
		fmt.Println("Неожиданное состояние.")
	}
}
