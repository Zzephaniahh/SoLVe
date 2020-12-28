int main (int argc, char **argv) {
  int i = 0;
  do
  {
  if (i > 7)
  {
  goto ERROR;
  }
  i = i + 3;
  }
  while (i < 5);
  if (i > 7)
  {
  goto ERROR;
  }

  return 0;
  ERROR:
  {
  __VERIFIER_error();
  }
  return 0;
}
