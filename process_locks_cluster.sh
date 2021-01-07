for filename in cluster_test/*.c; do
  { timeout -s SIGKILL 0.2s  time ./full_run.sh "$filename" ; } 2> "$filename"_out.txt
done
/home/zeph/SoLVe
/home/zeph/avr
