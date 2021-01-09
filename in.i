
int addf(int x, int k);



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();
int main () {
  int i = 0;
  do
  {
  if (i > 7) goto ERROR; // assertion failure
  i = i + 2;
  }
  while(i<4);
  //if (i > 7) goto ERROR; // assertion failure
  return 0;
  ERROR: __VERIFIER_error();
  return 0;
}



int addf(int x, int k) {
//  i = addf(i, j);

  k = 2;
  x = x + 1;
  return x;
}
