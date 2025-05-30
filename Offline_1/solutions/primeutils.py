import random

def millerRabinPrimalityTest(n, a=2):
  """
  Uses the Miller-Robin Primality Test to check if a number is prime.
  
  args:
    n: The number to check for primality.
    a: The base to use for the test.
  """
  # factor out powers of 2 from n-1
  m = n - 1
  k = 0
  while m % 2 == 0:
    m >>= 1
    k += 1

  t = pow(a, m, n)

  if t == 1 or t == -1:
    return True

  for i in range(k - 1):
    t = pow(t, 2, n)
    if t == 1:
      return False
    if t == -1:
      return True

  return False


def generatePrime(bits = 128):
  """
  Generates a prime number which is atleast as large as the given number of bits.
  
  args:
    bits: The number of bits of the prime number.
  """
  while True:
    n = random.getrandbits(bits)
    if millerRabinPrimalityTest(n, 2):
      return n
