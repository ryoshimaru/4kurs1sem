package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"math/big"
	"os"
	"sort"
	"strconv"
	"strings"
)

type Frac struct {
	num *big.Int
	den *big.Int
}

func NewFracInt(v int64) Frac { return Frac{big.NewInt(v), big.NewInt(1)} }

func NewFrac(num, den *big.Int) Frac {
	f := Frac{new(big.Int).Set(num), new(big.Int).Set(den)}
	normalize(&f)
	return f
}

func NewFracFromString(s string) (Frac, error) {
	s = strings.TrimSpace(s)
	if s == "" {
		return Frac{}, errors.New("empty token")
	}
	if strings.Contains(s, "/") {
		parts := strings.SplitN(s, "/", 2)
		n, ok1 := new(big.Int).SetString(strings.TrimSpace(parts[0]), 10)
		d, ok2 := new(big.Int).SetString(strings.TrimSpace(parts[1]), 10)
		if !ok1 || !ok2 {
			return Frac{}, errors.New("bad fraction: " + s)
		}
		return NewFrac(n, d), nil
	}
	// try int64 first
	if i, err := strconv.ParseInt(s, 10, 64); err == nil {
		return NewFracInt(i), nil
	}
	// try big.Int
	if bi, ok := new(big.Int).SetString(s, 10); ok {
		return NewFrac(bi, big.NewInt(1)), nil
	}
	return Frac{}, errors.New("bad number: " + s)
}

func zero() Frac { return Frac{big.NewInt(0), big.NewInt(1)} }

func normalize(a *Frac) {
	if a.den.Sign() == 0 {
		panic("denominator is zero")
	}
	if a.den.Sign() < 0 {
		a.den.Neg(a.den)
		a.num.Neg(a.num)
	}
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

// ===== Pretty print =====

func printMatrix(step string, A [][]Frac, n int) {
	fmt.Println(step)
	m := len(A)
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
		lead := R[row][col]
		for j := col; j <= n; j++ {
			R[row][j] = R[row][j].Div(lead)
		}
		printMatrix(fmt.Sprintf("Шаг %d: нормировка строки r%d (делим на ведущий элемент)", stepNo, row+1), R, n)
		stepNo++

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

func uniqueSolution(res RREFResult, n int) []Frac {
	x := make([]Frac, n)
	for i := 0; i < len(res.R); i++ {
		pivotCol := -1
		for j := 0; j < n; j++ {
			// detect leading 1 that is leftmost in the row
			if res.R[i][j].String() == "1" {
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

func combinations(elements []int, k int) [][]int {
	var res [][]int
	var cur []int
	var dfs func(start int)
	dfs = func(start int) {
		if len(cur) == k {
			tmp := make([]int, k)
			copy(tmp, cur)
			res = append(res, tmp)
			return
		}
		for i := start; i < len(elements); i++ {
			cur = append(cur, elements[i])
			dfs(i + 1)
			cur = cur[:len(cur)-1]
		}
	}
	dfs(0)
	return res
}

func isIndependent(orig [][]Frac, basis []int) bool {
	m := len(orig)
	nc := len(basis)
	// build temporary m x nc matrix with selected columns (exclude RHS)
	tmp := make([][]Frac, m)
	for i := 0; i < m; i++ {
		tmp[i] = make([]Frac, nc)
		for j := 0; j < nc; j++ {
			tmp[i][j] = orig[i][basis[j]]
		}
	}

	rank := 0
	for col := 0; col < nc; col++ {
		if rank >= m {
			break
		}
		pivot := -1
		for r := rank; r < m; r++ {
			if !tmp[r][col].IsZero() {
				pivot = r
				break
			}
		}
		if pivot == -1 {
			return false
		}
		if pivot != rank {
			tmp[rank], tmp[pivot] = tmp[pivot], tmp[rank]
		}
		piv := tmp[rank][col]
		for r := 0; r < m; r++ {
			if r == rank {
				continue
			}
			if !tmp[r][col].IsZero() {
				f := tmp[r][col].Div(piv)
				for c := col; c < nc; c++ {
					tmp[r][c] = tmp[r][c].Sub(f.Mul(tmp[rank][c]))
				}
			}
		}
		rank++
	}
	return true
}

func getBasisSolution(orig [][]Frac, basis []int, nvars int) ([]Frac, error) {
	m := len(orig)
	nb := len(basis)
	// build augmented system A_B | b : m x (nb+1)
	sys := make([][]Frac, m)
	for i := 0; i < m; i++ {
		sys[i] = make([]Frac, nb+1)
		for j := 0; j < nb; j++ {
			sys[i][j] = orig[i][basis[j]]
		}
		sys[i][nb] = orig[i][len(orig[i])-1] // RHS
	}
	// Gauss–Jordan on this reduced system
	row := 0
	for col := 0; col < nb && row < m; col++ {
		// find pivot (first non-zero from row..m-1)
		pivot := -1
		for r := row; r < m; r++ {
			if !sys[r][col].IsZero() {
				pivot = r
				break
			}
		}
		if pivot == -1 {
			// dependent columns
			return nil, errors.New("columns are dependent")
		}
		if pivot != row {
			sys[row], sys[pivot] = sys[pivot], sys[row]
		}
		lead := sys[row][col]
		for j := col; j <= nb; j++ {
			sys[row][j] = sys[row][j].Div(lead)
		}
		for r := 0; r < m; r++ {
			if r == row {
				continue
			}
			if !sys[r][col].IsZero() {
				f := sys[r][col]
				for j := col; j <= nb; j++ {
					sys[r][j] = sys[r][j].Sub(f.Mul(sys[row][j]))
				}
			}
		}
		row++
	}
	// read solution for basis vars
	x := make([]Frac, nvars)
	for i := 0; i < nvars; i++ {
		x[i] = zero()
	}
	for i := 0; i < nb && i < m; i++ {
		x[basis[i]] = sys[i][nb]
	}
	return x, nil
}

func readMatrixLines(r io.Reader) ([][]Frac, error) {
	sc := bufio.NewScanner(r)
	var A [][]Frac
	var width int = -1
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		toks := strings.Fields(line)
		if width == -1 {
			width = len(toks)
		} else if len(toks) != width {
			return nil, errors.New("rows have different lengths")
		}
		row := make([]Frac, width)
		for j := 0; j < width; j++ {
			f, err := NewFracFromString(toks[j])
			if err != nil {
				return nil, err
			}
			row[j] = f
		}
		A = append(A, row)
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	if len(A) == 0 {
		return nil, errors.New("empty matrix")
	}
	// sanity: last column is RHS
	if width < 2 {
		return nil, errors.New("need at least one variable and RHS")
	}
	return A, nil
}

func printCompact(A [][]Frac) {
	for i := 0; i < len(A); i++ {
		var parts []string
		for j := 0; j < len(A[i]); j++ {
			parts = append(parts, A[i][j].String())
		}
		fmt.Println(strings.Join(parts, " "))
	}
	fmt.Println()
}

// ===== Main =====

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
		// default to matrix.txt if present; else stdin
		if f, err := os.Open("matrix.txt"); err == nil {
			defer f.Close()
			reader = f
		} else {
			reader = os.Stdin
		}
	}

	A, err := readMatrixLines(reader)
	if err != nil {
		fmt.Fprintln(os.Stderr, "ошибка чтения матрицы:", err)
		os.Exit(1)
	}
	m := len(A)
	n := len(A[0]) - 1

	fmt.Println("Исходная матрица:")
	printCompact(A)

	defer func() {
		if r := recover(); r != nil {
			fmt.Fprintln(os.Stderr, "ошибка:", r)
			os.Exit(1)
		}
	}()

	// Keep original for basis computations
	orig := make([][]Frac, m)
	for i := 0; i < m; i++ {
		orig[i] = make([]Frac, n+1)
		copy(orig[i], A[i])
	}

	res := gaussJordanWithSteps(A, n)

	fmt.Printf("rank(A) = %d, rank([A|b]) = %d, неизвестных n = %d\n\n", res.rankA, res.rankAb, n)

	if res.none {
		fmt.Println("Система несовместна: решений нет.")
		return
	}

	if res.unique {
		fmt.Println("Система совместна и определённа: единственное решение.")
		x := uniqueSolution(res, n)
		for i := 0; i < n; i++ {
			fmt.Printf("x_%d = %s\n", i+1, x[i].String())
		}
		fmt.Println()
		return
	}

	// Otherwise: enumerate all basic solutions (Lab2 requirement)
	fmt.Println("Система совместна и неопределённа: бесконечно много решений.")
	rank := res.rankA

	// Build all indices 0..n-1 and enumerate all combinations of size rank
	allIdx := make([]int, n)
	for i := 0; i < n; i++ {
		allIdx[i] = i
	}
	sort.Ints(allIdx)
	combs := combinations(allIdx, rank)

	fmt.Println("\nБазисные решения:")
	seen := 0
	for _, basis := range combs {
		if !isIndependent(orig, basis) {
			continue
		}
		sol, err := getBasisSolution(orig, basis, n)
		if err != nil {
			continue
		}
		fmt.Print("Базисные переменные: ")
		for i, v := range basis {
			if i > 0 {
				fmt.Print(", ")
			}
			fmt.Printf("x_%d", v+1)
		}
		fmt.Println()
		for i := 0; i < n; i++ {
			fmt.Printf("x_%d = %s\n", i+1, sol[i].String())
		}
		fmt.Println()
		seen++
	}
	if seen == 0 {
		fmt.Println("(не найдено ни одного независимого набора столбцов — проверьте входные данные)")
	}
}
