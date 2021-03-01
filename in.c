



extern void __VERIFIER_error() __attribute__ ((__noreturn__));

extern int __VERIFIER_nondet_int();


int add(int x);

int main () {
  int i = 0;
  do
  {
  if (i > 7) goto ERROR; // assertion failure
  i = i+2;
  }
  while(i<5);
  return 0;
  ERROR: __VERIFIER_error();
  return 0;
}


// int add(int x)
// {
//   x = x + 1;
//   return x;
// }