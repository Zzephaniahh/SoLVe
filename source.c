



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();

int main () {
  int i = 20;
  if (i > 0) goto ERROR; // assertion failure
  return 0;
  ERROR: __VERIFIER_error();

}
