from rsa import *
from bcolors import bcolors

def main():
  # Generate RSA keys: modulus (n), public exponent (e), and private exponent (d)
  modulus, pub_exp, priv_exp = generateRsaKeys()
  print(f"Public key: {bcolors.OKGREEN}{pub_exp}{bcolors.ENDC}")
  print(f"Private key: {bcolors.OKGREEN}{priv_exp}{bcolors.ENDC}")
  print(f"n: {bcolors.OKGREEN}{modulus}{bcolors.ENDC}")

  # Prompt user for integer input to encrypt
  try:
    plain_val = int(input("Enter an integer to encrypt: "))
  except Exception:
    # Handle invalid input
    print(f"{bcolors.FAIL}Invalid input!{bcolors.ENDC}")
    return

  # Encrypt the input value using RSA public key
  encrypted_val = encryptWithRSA(plain_val, pub_exp, modulus)
  print(f"Ciphertext: {bcolors.OKGREEN}{encrypted_val}{bcolors.ENDC}")

  # Decrypt the ciphertext using RSA private key
  decrypted_val = decryptWithRSA(encrypted_val, priv_exp, modulus)
  print(f"Plaintext: {bcolors.OKGREEN}{decrypted_val}{bcolors.ENDC}")

# Entry point of the script
if __name__ == "__main__":
  main()