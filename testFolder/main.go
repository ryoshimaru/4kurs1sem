package main

import "fmt"

type Count int

func (c *Count) Increment() {
	c++
}

func main() {
	var count Count
	count.Increment()
	fmt.Print(count)
}
