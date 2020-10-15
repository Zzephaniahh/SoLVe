int func_F(int a, int b);

int main () {
  int y=0;
  int x=0;
  int z;
  z = func_F(x, y);
  return 0;
}

int func_F(a, b)
{
  a++;
  if (a<b){
    a = 1;}
  return a;
}
