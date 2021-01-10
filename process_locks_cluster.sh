for filename in cluster_test/*.c; do
  { timeout -s SIGKILL 0.2s  time ./full_run.sh "$filename" ; } 2> "$filename"_out_global.txt
done

for filename in cluster_test/*.c; do
  { timeout -s SIGKILL 0.2s  time ./full_run.sh "$filename" --local; } 2> "$filename"_out_local.txt
done

