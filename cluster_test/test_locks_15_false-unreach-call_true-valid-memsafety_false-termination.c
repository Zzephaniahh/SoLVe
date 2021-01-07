



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();
int main () {
  int i = 0;
  do
  {
  i = i + 2;
  if (i > 7) goto ERROR; // assertion failure
  }
  while(i<5);
  if (i > 7) goto ERROR; // assertion failure
  return 0;
  ERROR: __VERIFIER_error();
  return 0;

}
