import time
from primeutils import generatePrime
from diffiehellman import *
from bcolors import bcolors
import tabulate

# Measure the time taken for each step of the Diffie-Hellman key exchange for a given bit length
def measure_times(bits: int):
  t0 = time.time()
  # Generate a prime number and its factors
  p, factors = create_prime_with_factors(bits)
  t1 = time.time()
  # Find a generator for the prime
  g = find_generator(p, factors, 2, p - 1)
  t2 = time.time()
  # Generate a private key
  priv_a = generatePrime(bits // 2)
  t3 = time.time()
  # Compute the public key
  pub_A = fast_mod_exp(g, priv_a, p)
  t4 = time.time()
  # Compute the shared key
  shared_key = fast_mod_exp(pub_A, priv_a, p)
  t5 = time.time()
  # Return the time taken for each step
  return t1-t0, t2-t1, t3-t2, t4-t3, t5-t4

# Compute the average time for each step over multiple iterations
def average_times(bits: int, iterations: int):
  avg_p = avg_g = avg_a = avg_A = avg_key = 0
  for _ in range(iterations):
    t_p, t_g, t_a, t_A, t_key = measure_times(bits)
    avg_p += t_p
    avg_g += t_g
    avg_a += t_a
    avg_A += t_A
    avg_key += t_key
  # Return the average times for each step
  return [
    bits,
    avg_p / iterations,
    avg_g / iterations,
    avg_a / iterations,
    avg_A / iterations,
    avg_key / iterations
  ]

# --- Interactive Diffie-Hellman demonstration ---

# Prompt user for bit length of the prime
print(f'{bcolors.BOLD}{bcolors.OKCYAN}Enter bit length for prime (k):{bcolors.ENDC}')
bitlen = int(input())

# Generate prime and its factors
prime, factors = create_prime_with_factors(bitlen)
# Find a generator for the prime
generator = find_generator(prime, factors, 2, prime - 1)
# Generate private keys for Alice and Bob
secret_a = generatePrime(bitlen // 2)
secret_b = generatePrime(bitlen // 2)
# Compute public keys for Alice and Bob
public_A = fast_mod_exp(generator, secret_a, prime)
public_B = fast_mod_exp(generator, secret_b, prime)
# Compute shared keys from both perspectives
shared_A = fast_mod_exp(public_B, secret_a, prime)
shared_B = fast_mod_exp(public_A, secret_b, prime)

# Display all generated values
print(f'Prime (p): {bcolors.OKGREEN}{prime}{bcolors.ENDC}')
print(f'Generator (g): {bcolors.OKGREEN}{generator}{bcolors.ENDC}')
print(f'Private a: {bcolors.OKGREEN}{secret_a}{bcolors.ENDC}')
print(f'Private b: {bcolors.OKGREEN}{secret_b}{bcolors.ENDC}')
print(f'Public A: {bcolors.OKGREEN}{public_A}{bcolors.ENDC}')
print(f'Public B: {bcolors.OKGREEN}{public_B}{bcolors.ENDC}')
print()
print(f'Shared key (A^b): {bcolors.OKGREEN}{shared_A}{bcolors.ENDC}')
print(f'Shared key (B^a): {bcolors.OKGREEN}{shared_B}{bcolors.ENDC}')
print()

# Check if both shared keys match
if shared_A == shared_B:
  print(f'{bcolors.OKGREEN}{bcolors.BOLD}Shared keys match!{bcolors.ENDC}')
else:
  print(f'{bcolors.WARNING}{bcolors.BOLD}Shared keys do not match!{bcolors.ENDC}')

# --- Timing report for different bit lengths ---

print('Generating timing report...\n')
print(f'{bcolors.BOLD}{bcolors.OKCYAN}\t\tComputation Times{bcolors.ENDC}')
results = []
# Test for different bit lengths and collect timing data
for k in [128, 192, 256]:
  results.append(average_times(k, 5))
# Display timing results in a table
print(tabulate.tabulate(results, headers=['k', 'Prime', 'Generator', 'a', 'A', 'Shared Key'], tablefmt='psql'))