AVR_PATH=/home/zeph/avr
SOLVE_PATH=/home/zeph/SoLVe
vmt_file=$1
cd $AVR_PATH

python3 avr.py $SOLVE_PATH/$vmt_file --witness --smt2
