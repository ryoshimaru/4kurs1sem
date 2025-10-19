package main

import (
	"bufio"
	"fmt"
	"os"
	"regexp"
	"strings"
)

type Token struct {
	Type  string
	Value string
}

type Lexer struct {
	input   string // входная строка
	tokens  []Token
	current int
}

func NewLexer(input string) *Lexer {
	l := &Lexer{input: strings.TrimSpace(input)}
	l.tokenize()
	return l
}

func (l *Lexer) tokenize() {
	tokenSpecs := []struct {
		typ   string
		regex *regexp.Regexp
	}{
		{"NUMBER", regexp.MustCompile(`^\d+`)},
		{"ID", regexp.MustCompile(`^[a-zA-Z][a-zA-Z0-9]*`)},
		{"PLUS", regexp.MustCompile(`^\+`)},
		{"MINUS", regexp.MustCompile(`^-`)},
		{"MUL", regexp.MustCompile(`^\*`)},
		{"DIV", regexp.MustCompile(`^/`)},
		{"LPAREN", regexp.MustCompile(`^\(`)},
		{"RPAREN", regexp.MustCompile(`^\)`)},
	}

	l.input = regexp.MustCompile(`\s+`).ReplaceAllString(l.input, "")

	pos := 0
	for pos < len(l.input) {
		matched := false
		for _, spec := range tokenSpecs {
			loc := spec.regex.FindStringIndex(l.input[pos:])
			if loc != nil && loc[0] == 0 {
				value := l.input[pos : pos+loc[1]]
				l.tokens = append(l.tokens, Token{Type: spec.typ, Value: value})
				pos += loc[1]
				matched = true
				break
			}
		}
		if !matched {
			panic(fmt.Sprintf("Ошибка! Неизвестный токен на позиции %d: %s", pos, l.input[pos:]))
		}
	}
	l.tokens = append(l.tokens, Token{Type: "EOF", Value: ""})
}

func (l *Lexer) getNextToken() Token {
	if l.current >= len(l.tokens) {
		return Token{Type: "EOF", Value: ""}
	}
	tok := l.tokens[l.current]
	l.current++
	return tok
}

type Node struct {
	Label    string
	Value    string
	Children []*Node
}

type Parser struct {
	lexer *Lexer
	curr  Token
}

func NewParser(lexer *Lexer) *Parser {
	p := &Parser{lexer: lexer}
	p.curr = p.lexer.getNextToken()
	return p
}

func (p *Parser) match(expected string) {
	if p.curr.Type == expected {
		p.curr = p.lexer.getNextToken()
	} else {
		expectedStr := ""
		switch expected {
		case "NUMBER":
			expectedStr = "number"
		case "ID":
			expectedStr = "id"
		case "LPAREN":
			expectedStr = "("
		case "RPAREN":
			expectedStr = ")"
		default:
			expectedStr = expected
		}
		errMsg := fmt.Sprintf("Ошибка! Ожидалось: %s, но получено: %s", expectedStr, p.curr.Type)
		if p.curr.Type == "EOF" {
			errMsg = fmt.Sprintf("Ошибка! Ожидалось: '%s'", expectedStr)
		}
		panic(errMsg)
	}
}

func (p *Parser) parseS() *Node {
	node := &Node{Label: "S"}
	t := p.parseT()
	node.Children = append(node.Children, t)
	e := p.parseE()
	node.Children = append(node.Children, e)
	return node
}

func (p *Parser) parseE() *Node {
	node := &Node{Label: "E"}
	switch p.curr.Type {
	case "PLUS":
		p.match("PLUS")
		opNode := &Node{Label: "+"}
		t := p.parseT()
		e := p.parseE()
		opNode.Children = append(opNode.Children, t, e)
		return opNode
	case "MINUS":
		p.match("MINUS")
		opNode := &Node{Label: "-"}
		t := p.parseT()
		e := p.parseE()
		opNode.Children = append(opNode.Children, t, e)
		return opNode
	default:
		return node
	}
}

func (p *Parser) parseT() *Node {
	node := &Node{Label: "T"}
	f := p.parseF()
	node.Children = append(node.Children, f)
	tPrime := p.parseTPrime()
	node.Children = append(node.Children, tPrime)
	return node
}

func (p *Parser) parseTPrime() *Node {
	node := &Node{Label: "T'"}
	switch p.curr.Type {
	case "MUL":
		p.match("MUL")
		opNode := &Node{Label: "*"}
		f := p.parseF()
		tPrime := p.parseTPrime()
		opNode.Children = append(opNode.Children, f, tPrime)
		return opNode
	case "DIV":
		p.match("DIV")
		opNode := &Node{Label: "/"}
		f := p.parseF()
		tPrime := p.parseTPrime()
		opNode.Children = append(opNode.Children, f, tPrime)
		return opNode
	default:
		return node
	}
}

func (p *Parser) parseF() *Node {
	node := &Node{Label: "F"}
	switch p.curr.Type {
	case "LPAREN":
		p.match("LPAREN")
		s := p.parseS()
		p.match("RPAREN")
		node.Children = append(node.Children, &Node{Label: "("}, s, &Node{Label: ")"})
	case "NUMBER":
		node = &Node{Label: "NUMBER", Value: p.curr.Value}
		p.match("NUMBER")
	case "ID":
		node = &Node{Label: "ID", Value: p.curr.Value}
		p.match("ID")
	default:
		panic("Ошибка! Ожидалось: number, id или '('")
	}
	return node
}

func nodeCaption(n *Node) string {
	if n.Value != "" {
		return fmt.Sprintf("%s: %s", n.Label, n.Value)
	}
	return n.Label
}

func renderTree(n *Node) string {
	var sb strings.Builder
	sb.WriteString(nodeCaption(n) + "\n")
	for i, ch := range n.Children {
		isLast := i == len(n.Children)-1
		printFancy(&sb, ch, "", isLast)
	}
	return sb.String()
}

func printFancy(sb *strings.Builder, n *Node, prefix string, isLast bool) {
	branch := "├── "
	nextPrefix := prefix + "│   "
	if isLast {
		branch = "└── "
		nextPrefix = prefix + "    "
	}
	sb.WriteString(prefix + branch + nodeCaption(n) + "\n")
	for i, ch := range n.Children {
		printFancy(sb, ch, nextPrefix, i == len(n.Children)-1)
	}
}

func formatTokens(ts []Token) string {
	var b strings.Builder
	for _, t := range ts {
		if t.Type == "EOF" {
			continue
		}
		if t.Value != "" && (t.Type == "NUMBER" || t.Type == "ID") {
			fmt.Fprintf(&b, "[%s:%s] ", t.Type, t.Value)
		} else {
			sym := t.Value
			if sym == "" {
				sym = t.Type
			}
			fmt.Fprintf(&b, "[%s] ", sym)
		}
	}
	return strings.TrimSpace(b.String())
}

func main() {
	fmt.Println("Введите арифметическое выражение:")
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	input := scanner.Text()

	lexer := NewLexer(input)

	fmt.Println("Токены:")
	fmt.Println(" ", formatTokens(lexer.tokens))

	parser := NewParser(lexer)

	var tree *Node
	errMsg := ""
	success := true
	func() {
		defer func() {
			if r := recover(); r != nil {
				errMsg = fmt.Sprint(r)
				success = false
			}
		}()
		tree = parser.parseS()
		if parser.curr.Type != "EOF" {
			panic("Ошибка! Лишние символы в конце строки")
		}
	}()

	if success {
		fmt.Println("\nВыражение корректно ✅")
		fmt.Println("\nСинтаксическое дерево:")
		pretty := renderTree(tree)
		fmt.Print(pretty)

		err := os.WriteFile("tree.txt", []byte(pretty), 0644)
		if err != nil {
			fmt.Printf("\n⚠️ Не удалось сохранить дерево в файл: %v\n", err)
		} else {
			fmt.Println("\nДерево сохранено в tree.txt")
		}
	} else {
		fmt.Println("\nВыражение некорректно ❌")
		fmt.Println(errMsg)
	}
}
