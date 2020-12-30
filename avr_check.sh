AVR_PATH=/home/zephaniah/Documents/avr
SOLVE_PATH=/home/zephaniah/Documents/Zephaniahs_Research/SoLVe
vmt_file=$1
cd $AVR_PATH

python3 avr.py $SOLVE_PATH/$vmt_file --witness --smt2
