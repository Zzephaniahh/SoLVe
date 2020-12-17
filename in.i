





int main () {
  int i = 0;
  /* this is a comment */

  //if (i > 7)
  do
  {
  if (i > 7) goto ERROR; // assertion failure
  i = i + 3;
  }
  while (i < 5);
  if (i > 7) goto ERROR; // assertion failure


  return 0;
  ERROR: __VERIFIER_error();
  return 0;
}
