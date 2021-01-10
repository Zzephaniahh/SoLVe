#for filename in locks/*.c; do
  #{ timeout -s SIGKILL 50m  time ./full_run.sh "$filename" ; } 2> "$filename"_out.txt
filename=locks/test_locks_11_true-unreach-call_true-valid-memsafety_false-termination.c
 { timeout -s SIGKILL 50m  time ./full_run.sh "$filename" ; } #2> "$filename"_out.txt
#done

