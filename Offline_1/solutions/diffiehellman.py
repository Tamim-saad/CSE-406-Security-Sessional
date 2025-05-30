from primeutils import *

def fast_mod_exp(base, exponent, modulus):
  """Efficient modular exponentiation using the square-and-multiply method."""
  result = 1
  # Loop until all bits of exponent are processed
  while exponent:
    if exponent & 1:
      # If current bit is 1, multiply result by base modulo modulus
      result = int(result * base % modulus)
      exponent -= 1
    else:
      # Square the base modulo modulus and shift exponent right by 1 bit
      base = int(base * base % modulus)
      exponent >>= 1
  return result

def find_generator(prime, prime_factors, lower, upper):
  """
  Find a generator for the given prime and its factors.
  A generator g must satisfy g^((p-1)/q) != 1 mod p for all prime factors q of p-1.
  """
  phi = prime - 1
  # Try candidates in the given range
  for candidate in range(lower, upper + 1):
    is_generator = True
    # Check if candidate is a generator by testing all prime factors
    for factor in prime_factors:
      if fast_mod_exp(candidate, phi // factor, prime) == 1:
        is_generator = False
        break
    if is_generator:
      return candidate
  return -1  # No generator found in the range

def create_prime_with_factors(bitlen: int) -> tuple:
  """
  Generate a safe prime and its factors.
  A safe prime is of the form p = 2q + 1, where both p and q are prime.
  Returns: (prime, [factors])
  """
  q = generatePrime(bitlen - 1)  # Generate a (bitlen-1)-bit prime q
  while True:
    p = (q << 1) + 1  # Compute p = 2q + 1
    # Test if p is prime using Miller-Rabin with 2 rounds
    if millerRabinPrimalityTest(p, 2):
      return p, [2, q]  # Return safe prime and its factors
    q = generatePrime(bitlen - 1)  # Try another q if p is not prime