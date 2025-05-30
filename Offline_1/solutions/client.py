import socket
from AES128 import encrypt, decrypt
from diffiehellman import *
from bcolors import bcolors
from rsa import *

def establish_connection(address, port):
  """
  Establishes a TCP connection to the server at the given address and port.
  """
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((address, port))
  print('Connected to server!')
  return sock

def rsa_key_exchange(sock):
  """
  Generates RSA key pair, sends public key and modulus to server,
  and receives server's public key and modulus.
  """
  print('Generating RSA key pair...')
  modulus, pub_key, priv_key = generateRsaKeys()
  print('RSA keys generated!')
  print(f'Public key:{bcolors.OKGREEN} {pub_key}{bcolors.ENDC}')
  print(f'Private key:{bcolors.OKGREEN} {priv_key}{bcolors.ENDC}')
  print(f'n:{bcolors.OKGREEN} {modulus}{bcolors.ENDC}')

  # Send own public key and modulus to server
  print('Transmitting public key and modulus...')
  sock.send(f"{pub_key} {modulus}".encode())

  # Receive server's public key and modulus
  print('Awaiting server\'s public key and modulus...')
  srv_params = sock.recv(1024).decode().split()
  srv_pub_key = int(srv_params[0])
  srv_modulus = int(srv_params[1])
  print('Received server\'s public key and modulus!')
  print(f'server_e:{bcolors.OKGREEN} {srv_pub_key}{bcolors.ENDC}')
  print(f'server_n:{bcolors.OKGREEN} {srv_modulus}{bcolors.ENDC}')
  return pub_key, priv_key, modulus, srv_pub_key, srv_modulus

def authenticate_and_decrypt(sock, priv_key, modulus, srv_pub_key, srv_modulus):
  """
  Receives signed and encrypted Diffie-Hellman parameters from server,
  authenticates the server, and decrypts the parameters.
  """
  print('Receiving signed and encrypted DH parameters...')
  payload = sock.recv(1024).decode().split()
  sig = int(payload[0])
  enc_p = int(payload[1])
  enc_g = int(payload[2])
  enc_A = int(payload[3])
  print('Received encrypted DH parameters!')

  # Server authentication: verify signature
  sig_check = encryptWithRSA(sig, srv_pub_key, srv_modulus)
  expected_hash = hashForAuth(enc_p)
  if sig_check != expected_hash:
    print(f'{bcolors.FAIL}Server authentication failed!{bcolors.ENDC}')
    exit(1)
  print(f'{bcolors.OKCYAN}Server authentication successful!{bcolors.ENDC}')

  # Decrypt DH parameters using own private key
  print('Decrypting DH parameters...')
  prime = decryptWithRSA(enc_p, priv_key, modulus)
  generator = decryptWithRSA(enc_g, priv_key, modulus)
  pub_A = decryptWithRSA(enc_A, priv_key, modulus)
  print(f'p:{bcolors.OKGREEN} {prime}{bcolors.ENDC}')
  print(f'g:{bcolors.OKGREEN} {generator}{bcolors.ENDC}')
  print(f'A:{bcolors.OKGREEN} {pub_A}{bcolors.ENDC}')
  return prime, generator, pub_A

def send_dh_public(sock, generator, prime, srv_pub_key, srv_modulus, priv_key, modulus):
  """
  Generates ephemeral Diffie-Hellman secret, computes public value,
  encrypts and signs it, and sends to server.
  """
  print('Generating ephemeral DH secret...')
  dh_secret = generatePrime(64)
  print('Ephemeral secret:', dh_secret)
  print('Computing DH public value...')
  dh_pub = pow(generator, dh_secret, prime)
  print('DH public value:', dh_pub)

  # Encrypt DH public value with server's public key
  enc_dh_pub = encryptWithRSA(dh_pub, srv_pub_key, srv_modulus)
  # Sign the encrypted DH public value
  sig = hashForAuth(enc_dh_pub)
  signed_sig = decryptWithRSA(sig, priv_key, modulus)
  # Send signed signature and encrypted DH public value to server
  msg = f"{signed_sig} {enc_dh_pub}"
  sock.send(msg.encode())
  return dh_secret, dh_pub

def derive_aes_key(pub_A, dh_secret, prime):
  """
  Derives the shared secret using server's DH public value and own secret,
  then formats it as an AES key.
  """
  print('Deriving shared secret...')
  shared_secret = pow(pub_A, dh_secret, prime)
  print('Shared secret:', shared_secret)
  # Convert shared secret to 16 bytes for AES key
  key_bytes = shared_secret.to_bytes(16, 'big')
  aes_key = key_bytes.decode('latin-1')
  return aes_key

def secure_message_exchange(sock, aes_key):
  """
  Handles secure message exchange with the server using AES encryption.
  """
  user_input = input(
    f'{bcolors.BOLD}{bcolors.OKCYAN}Write something to send to server: {bcolors.ENDC}')
  # Encrypt message with AES key
  encrypted_msg = encrypt(user_input, aes_key)
  sock.send(encrypted_msg.encode())
  print(f'{bcolors.OKGREEN}Data sent successfully!{bcolors.ENDC}')
  print('Awaiting server reply...')
  # Receive and decrypt server's reply
  reply = sock.recv(1024)
  decrypted_reply = decrypt(reply.decode(), aes_key)
  print(f'Received data:{bcolors.OKBLUE} {decrypted_reply}{bcolors.ENDC}')

def main():
  """
  Main function to coordinate the secure client-server communication.
  """
  PORT = 12344
  ADDRESS = 'localhost'
  # Step 1: Establish connection
  sock = establish_connection(ADDRESS, PORT)
  # Step 2: RSA key exchange
  pub_key, priv_key, modulus, srv_pub_key, srv_modulus = rsa_key_exchange(sock)
  # Step 3: Authenticate server and decrypt DH parameters
  prime, generator, pub_A = authenticate_and_decrypt(sock, priv_key, modulus, srv_pub_key, srv_modulus)
  # Step 4: Send own DH public value
  dh_secret, dh_pub = send_dh_public(sock, generator, prime, srv_pub_key, srv_modulus, priv_key, modulus)
  # Step 5: Derive AES key from shared secret
  aes_key = derive_aes_key(pub_A, dh_secret, prime)
  # Step 6: Secure message exchange
  secure_message_exchange(sock, aes_key)
  sock.close()

if __name__ == "__main__":
  main()