all: project01.pdf

project01.pdf: throughput.png latency.png
	pdflatex project01
	pdflatex project01

throughput.png: throughput.plt throughput.dat throughputF.dat
	gnuplot throughput.plt

latency.png: latency.plt results.dat resultsF.dat
	gnuplot latency.plt

clean:
	rm -f homework06.[!tex]* *.png
