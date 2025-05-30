from primeutils import *
import random
import math
import hashlib

def _modinv_extended(a: int, b: int) -> tuple:
  """
  Extended Euclidean Algorithm.
  Returns (x, y, gcd) such that x*a + y*b = gcd.
  """
  # Initialize coefficients and remainders
  prev_x, x = 1, 0
  prev_r, r = a, b
  # Loop until remainder is zero
  while r != 0:
    quotient = prev_r // r
    prev_r, r = r, prev_r - quotient * r
    prev_x, x = x, prev_x - quotient * x
  # Compute y using the final values
  if b != 0:
    y = (prev_r - prev_x * a) // b
  else:
    y = 0
  return prev_x, y, prev_r

def rsa_encrypt(msg: int, pub_exp: int, modulus: int) -> int:
  """
  Encrypts an integer message using RSA public key.
  Args:
    msg: The integer message to encrypt.
    pub_exp: The public exponent.
    modulus: The RSA modulus.
  Returns:
    The encrypted integer ciphertext.
  """
  # Perform modular exponentiation for encryption
  return pow(msg, pub_exp, modulus)

def rsa_decrypt(cipher: int, priv_exp: int, modulus: int) -> int:
  """
  Decrypts an integer ciphertext using RSA private key.
  Args:
    cipher: The integer ciphertext to decrypt.
    priv_exp: The private exponent.
    modulus: The RSA modulus.
  Returns:
    The decrypted integer message.
  """
  # Perform modular exponentiation for decryption
  return pow(cipher, priv_exp, modulus)

def rsa_hash_for_auth(data) -> int:
  """
  Returns SHA-1 hash of the input as an integer.
  Args:
    data: The data to hash.
  Returns:
    Integer representation of SHA-1 hash.
  """
  # Convert data to bytes and hash using SHA-1
  data_bytes = str(data).encode()
  return int(hashlib.sha1(data_bytes).hexdigest(), 16)

def create_rsa_keypair():
  """
  Generates RSA modulus, public exponent, and private exponent.
  Returns:
    (modulus, public_exp, private_exp)
  """
  # Generate two large random primes
  p = generatePrime()
  q = generatePrime()
  # Compute modulus n = p * q
  modulus = p * q
  # Compute Carmichael's totient function lambda(n)
  lambda_n = math.lcm(p - 1, q - 1)
  # Randomly select public exponent e such that gcd(e, lambda_n) == 1
  pub_exp = random.getrandbits(16)
  while math.gcd(pub_exp, lambda_n) != 1:
    pub_exp = random.getrandbits(16)
  # Compute private exponent d using modular inverse
  priv_exp, _, _ = _modinv_extended(pub_exp, lambda_n)
  return modulus, pub_exp, priv_exp

# Aliases for compatibility with old code
generateRsaKeys = create_rsa_keypair
encryptWithRSA = rsa_encrypt
decryptWithRSA = rsa_decrypt
hashForAuth = rsa_hash_for_auth