//#include <assert.h> //not allowed

int func_F(int a, int b);

int func_G(int a);

int assert(int cond);


int main () {
  int a;
  int b = 8;
  a = func_F(a, b);
  int cond;
  cond = a<7;
  assert(cond);
  a = a + 1;
  a = func_F(a);
  return 0;
  }
  int func_F(a, b)
  {
    a++;
    a = func_G(a);
    return a;
  }

  int func_G(a)
  {
    a++;
    return a;
  }
