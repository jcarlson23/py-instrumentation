#include <iostream>
#include <math.h>

#define DPRINTF(fmt, ...) \
	do { fprintf(stdout,"%s:%d:%s(): " fmt,__FILE__,__LINE__,__func__,__VA_ARGS__); } while(0)
#define X 2

int main(void)
{
  std::cout << "Testing...\n";
  return 0;
}
