int func_F(int a, int b);

int main () {
  int y=0;
  int x=0;
  int z=0;
  int h;
  z = func_F(x, y);
  z = 7;
  z = func_F(5, 6);
  z++;
  return 0;
}

int func_F(a, b)
{
  a++;
  if (a<b){
    a = 1;}
  return a;
}
