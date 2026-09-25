package bench

import (
	"fmt"
	"strconv"
	"testing"
)

var inputs = []int{-1, 0, 12, 123456, 1 << 30}
var formatSink string

func BenchmarkItoa(b *testing.B) {
	// 语义检查位于 B.Loop 开始前，不计入测量循环。
	for _, n := range inputs {
		if strconv.Itoa(n) != fmt.Sprint(n) {
			b.Fatalf("format differs for %d", n)
		}
	}
	b.ReportAllocs()
	i := 0
	for b.Loop() {
		formatSink = strconv.Itoa(inputs[i])
		i++
		if i == len(inputs) {
			i = 0
		}
	}
}

func BenchmarkSprint(b *testing.B) {
	for _, n := range inputs {
		if strconv.Itoa(n) != fmt.Sprint(n) {
			b.Fatalf("format differs for %d", n)
		}
	}
	b.ReportAllocs()
	i := 0
	for b.Loop() {
		formatSink = fmt.Sprint(inputs[i])
		i++
		if i == len(inputs) {
			i = 0
		}
	}
}
