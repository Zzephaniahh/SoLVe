



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();

int main () {
  int i = 0;
  /* this is a comment */
  int v_in;
  v_in = __VERIFIER_nondet_int();

  do
  {
  if (i > 7) goto ERROR; // assertion failure
  i = i + 4 + 7 + (i + 11);
  }
  while (i < 5);
  if (i > 7) goto ERROR; // assertion failure


  return 0;
  ERROR: __VERIFIER_error();
  return 0;
}
