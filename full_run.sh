function has_param() {
    local terms="$1"
    shift

    for term in $terms; do
        for arg; do
            if [[ $arg == "$term" ]]; then
                echo true
            # else
            #     echo false
            fi
        done
    done
}

make
source_file=$1



./cilcfgformula $source_file > cil_cfg.txt

# python3 SoLVe.py cil_cfg.txt --local > locks_test.vmt
LOCAL=$(has_param "--local" "$@")
# echo $LOCAL
if "$LOCAL"; then
LOCAL=$2
echo  'GGGGGGGGGGGGG'
python3 SoLVe.py cil_cfg.txt --local > locks_test.vmt
else
  python3 SoLVe.py cil_cfg.txt > locks_test.vmt
fi
./avr_check.sh locks_test.vmt
