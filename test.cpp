#include <iostream>
#include <math.h>

#define X 2

int helper(void * ptr);

int main(void)
{
  helper(NULL);
  std::cout << "Testing...\n";
  return 0;
}

int helper(void * ptr) {
  std::cout << "helping...\n";
  return 0;
}
 
int 
simple(void) {
  
}
