reset
set title "Latency"
set term png truecolor
set output "latency.png"
set xlabel "File Format"
set ylabel "Average Latency (in seconds)"
set grid
set boxwidth 0.95 relative
set style fill transparent solid 0.5 noborder
set style data histogram 
set style histogram cluster

plot "results.dat" using 2:xtic(1) lc rgb"red" title "Single Connection", "resultsF.dat" using 2:xtic(1) lc rgb"blue" title "Forking"