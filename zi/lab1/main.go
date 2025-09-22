package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
)

var input int8

func printAB(a, b int) {
	fmt.Printf("\na: %d, b:%d\n", a, b)
}

func fastExp(a, x, p int) int {
	resultat := 1

	if a == 0 || p <= 0 {
		panic("Wrong input")
	}

	a = a % p
	for x > 0 {
		if x%2 == 1 {
			resultat = (resultat * a) % p
		}
		a = (a * a) % p
		x = x / 2
	}
	return resultat
}

func simpleNum(n int) bool {
	for i := 0; i < 100; i++ {
		a := rand.Intn(n-3) + 2
		if fastExp(a, n-1, n) != 1 {
			return false
		}
	}
	return true
}

func evklid(a, b int) (int, int, int) {
	nod, x, y := a, 1, 0
	v1, v2, v3 := b, 0, 1

	for v1 != 0 {
		q := nod / v1
		t1 := nod % v1
		t2 := x - q*v2
		t3 := y - q*v3
		nod, x, y, v1, v2, v3 = v1, v2, v3, t1, t2, t3
	}

	return nod, x, y
}

func evklidExtended() (int, int, int) {
	fmt.Printf("Choose parametr: \n1. Keyboard input\n2. Random Generation\n3. Random generation (simple numbers)\n")
	fmt.Scanf("%d", &input)

	in := bufio.NewReader(os.Stdin)
	in.ReadString('\n')

	fmt.Printf("You choosed %d parametr\n\n...\n\n", input)

	var a, b int
	switch input {
	case 1:
		for {
			fmt.Println("Type a, then b:")
			n, err := fmt.Fscan(in, &a, &b)
			if n == 2 && err == nil {
				break
			}
			in.ReadString('\n')
			fmt.Println("Invalid input, try again")
		}
		printAB(a, b)
		return evklid(a, b)

	case 2:
		a = rand.Intn(1000000000)
		b = rand.Intn(1000000000)
		printAB(a, b)
		return evklid(a, b)

	case 3:
		a, b := func() (int, int) {
			var a, b int
			for {
				a = rand.Intn(10000000) + 100
				b = rand.Intn(10000000) + 100
				if simpleNum(a) && simpleNum(b) {
					return a, b
				}
			}
		}()
		printAB(a, b)
		return evklid(a, b)

	default:
		panic("Wrong symbol. Try again")
	}
}

func main() {
	fmt.Println(fastExp(11, 6, 23))
	fmt.Println(simpleNum(17))

	nod, x, y := evklidExtended()

	fmt.Printf("НОД: %d, x: %d, y: %d", nod, x, y)
}
