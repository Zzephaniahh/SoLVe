
int addf(int x, int k);



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();
int main () {
  int i = 0;
  int j = 0;
  do
  {
  if (i > 7) goto ERROR; // assertion failure
  i = addf(i, j);
  //i = i + 2;
  }
  while(i<5);
  return 0;
  ERROR: __VERIFIER_error();
  return 0;
}


int addf(int x, int k) {

  k = 2;
  x = x + 1;
  return x;
}
