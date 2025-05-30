import socket
from AES128 import encrypt, decrypt
from diffiehellman import *
from diffiehellman import create_prime_with_factors, find_generator
from bcolors import bcolors
from rsa import *

def create_dh_params():
  """
  Generate Diffie-Hellman parameters:
  - 128-bit safe prime
  - generator for the prime
  - ephemeral DH secret
  - DH public value
  """
  print('Generating 128-bit safe prime...')
  prime, factors = create_prime_with_factors(128)
  print('Prime:', prime)
  print('Searching for generator...')
  generator = find_generator(prime, factors, 2, prime - 1)
  print('Generator:', generator)
  print('Generating ephemeral DH secret...')
  dh_secret = generatePrime(64)
  print('Ephemeral secret:', dh_secret)
  print('Computing DH public value...')
  pub_A = pow(generator, dh_secret, prime)
  return prime, generator, dh_secret, pub_A

def handle_client(conn):
  """
  Handle the secure key exchange and encrypted communication with a client.
  Implements RSA authentication, Diffie-Hellman key exchange, and AES-encrypted messaging.
  """
  # Receive client's RSA public key and modulus
  print('Receiving client RSA public key and modulus...')
  client_params = conn.recv(1024).decode().split()
  client_pub_key = int(client_params[0])
  client_modulus = int(client_params[1])
  print('Received client RSA public key and modulus!')
  print(f'e:{bcolors.OKGREEN} {client_pub_key}{bcolors.ENDC}')
  print(f'client_n:{bcolors.OKGREEN} {client_modulus}{bcolors.ENDC}')

  # Generate server's RSA key pair
  print('Generating server RSA key pair...')
  modulus, pub_key, priv_key = generateRsaKeys()
  print(f'Public key:{bcolors.OKGREEN} {pub_key}{bcolors.ENDC}')
  print(f'Private key:{bcolors.OKGREEN} {priv_key}{bcolors.ENDC}')
  print(f'n:{bcolors.OKGREEN} {modulus}{bcolors.ENDC}')

  # Send server's RSA public key and modulus to client
  print('Sending server RSA public key and modulus...')
  conn.send(f"{pub_key} {modulus}".encode())

  # Prepare Diffie-Hellman parameters
  print('Preparing DH parameters...')
  prime, generator, dh_secret, pub_A = create_dh_params()

  # Encrypt DH parameters with client's RSA public key
  print('Encrypting DH parameters with client\'s public key...')
  enc_prime = encryptWithRSA(prime, client_pub_key, client_modulus)
  enc_generator = encryptWithRSA(generator, client_pub_key, client_modulus)
  enc_pub_A = encryptWithRSA(pub_A, client_pub_key, client_modulus)

  # Sign the encrypted prime for authentication
  sig = hashForAuth(enc_prime)
  print(f'encryptedP: {bcolors.FAIL}{enc_prime}{bcolors.ENDC}')
  print(f'Hashed signature: {bcolors.FAIL}{sig}{bcolors.ENDC}')
  signed_sig = decryptWithRSA(sig, priv_key, modulus)

  # Send signature and encrypted DH parameters to client
  msg = f"{signed_sig} {enc_prime} {enc_generator} {enc_pub_A}"
  conn.send(msg.encode())

  # Wait for client's DH public value and signature
  print('Awaiting DH public value from client...')
  client_data = conn.recv(1024).decode().split()
  client_sig = int(client_data[0])
  enc_dh_pub = int(client_data[1])

  # Authenticate client using signature
  check_sig = encryptWithRSA(client_sig, client_pub_key, client_modulus)
  if check_sig != hashForAuth(enc_dh_pub):
    print(f'{bcolors.FAIL}Client authentication failed!{bcolors.ENDC}')
    conn.close()
    return
  print(f'{bcolors.OKGREEN}Client authentication successful!{bcolors.ENDC}')

  # Decrypt client's DH public value
  dh_pub = decryptWithRSA(enc_dh_pub, priv_key, modulus)
  print('Received client DH public value:', dh_pub)

  # Derive shared secret using DH key exchange
  print('Deriving shared secret...')
  shared_secret = pow(dh_pub, dh_secret, prime)
  print('Shared secret:', shared_secret)
  key_bytes = shared_secret.to_bytes(16, 'big')
  aes_key = key_bytes.decode('latin-1')

  # Receive AES-encrypted message from client and decrypt it
  print('Awaiting encrypted message from client...')
  encrypted_msg = conn.recv(1024)
  decrypted_msg = decrypt(encrypted_msg.decode(), aes_key)
  print(f'Received data:{bcolors.OKBLUE} {decrypted_msg}{bcolors.ENDC}')

  # Prompt server user to send a reply, encrypt it, and send to client
  reply = input(
    f'{bcolors.BOLD}{bcolors.OKCYAN}Write something to send to client: {bcolors.ENDC}')
  encrypted_reply = encrypt(reply, aes_key)
  conn.send(encrypted_reply.encode())
  print(f'{bcolors.OKGREEN}Data sent successfully!{bcolors.ENDC}')

def main():
  """
  Main server loop: listens for incoming client connections and handles them.
  """
  PORT = 12344
  server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_sock.bind(('localhost', PORT))
  server_sock.listen(5)
  while True:
    print('Waiting for client...')
    conn, addr = server_sock.accept()
    print('Connection established with', addr)
    handle_client(conn)
    conn.close()

if __name__ == "__main__":
  main()