reset
set title "Throughput"
set term png truecolor
set logscale y
set yrange [1:1000000]
set output "throughput.png"
set xlabel "File Size"
set ylabel "Average Throughput (in KB/S)"
set grid
set boxwidth 0.95 relative
set style fill transparent solid 0.5 noborder
set style data histogram 
set style histogram cluster

plot "throughput.dat" using 2:xtic(1) lc rgb"purple" title "Single Connection", "throughputF.dat" using 2:xtic(1) lc rgb"green" title "Forking"