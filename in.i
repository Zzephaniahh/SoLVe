int func_F(int a, int b);
int func_G(int k);

int main () {
  int y=0;
  int x=0;
  int z=0;
  int h;
  z = func_F(x, y);
  z = 7;
  return 0;
}

int func_F(a, b)
{
  a++;
  if (a<b){
    a = 1;}
  //a = func_G(a);
  return a;
}

int func_G(k)
{
  return k++;
}
