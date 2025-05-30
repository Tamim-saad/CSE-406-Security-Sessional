import AES128
from bcolors import bcolors
import time

# enable AES128’s internal logging
AES128.logger.setIsLogging(True)

def main():
    master_key = input(f'{bcolors.BOLD}{bcolors.OKCYAN}Write the key: {bcolors.ENDC}')
    plaintext  = input(f'{bcolors.BOLD}{bcolors.OKCYAN}Write the plaintext: {bcolors.ENDC}')

    start_enc = time.time()
    cipherText = AES128.encrypt(plaintext, master_key)
    encryptionTime = time.time() - start_enc

    start_dec = time.time()
    AES128.decrypt(cipherText, master_key)
    decryptionTime = time.time() - start_dec

    print(f"Key Scheduling Time: {bcolors.OKGREEN}" +
          f"{AES128.keySchedulingTime:.6f}" + f"{bcolors.ENDC} seconds")
    print(f"Encryption Time: {bcolors.OKGREEN}" +
          f"{encryptionTime:.6f}" + f"{bcolors.ENDC} seconds")
    print(f"Decryption Time: {bcolors.OKGREEN}" +
          f"{decryptionTime:.6f}" + f"{bcolors.ENDC} seconds")

if __name__ == "__main__":
    main()