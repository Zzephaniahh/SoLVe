#make
source_file=$1

./cilcfgformula $source_file > cil_cfg.txt

python3 SoLVe.py cil_cfg.txt > locks_test.vmt

./avr_check.sh locks_test.vmt
