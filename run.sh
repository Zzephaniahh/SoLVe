make

source_file=$1

./cilcfgformula $source_file > cil_cfg.txt


# python3 SoLVe.py #test.txt


# sed -i '/__/d' test.txt
# sed -i '/char/d' test.txt
# sed -i '/long/d' test.txt
# sed -i '/float/d' test.txt
# sed -i '/void/d' test.txt
# sed -i '/double/d' test.txt
# sed -i '/Bool/d' test.txt
# sed -i '/unsigned/d' test.txt
# sed -i '/short/d' test.txt
# sed -i '/(int  )/d' test.txt # RM ME -- HACKY
