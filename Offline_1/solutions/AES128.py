import time
import numpy as np
from BitVector import BitVector
import sbox as sb
from consts import AES_modulus, Mixer, InvMixer
from logger import Logger
from bcolors import bcolors

# sizes
BITS_PER_BLOCK = 128
BYTES_PER_BLOCK = BITS_PER_BLOCK // 8
WORD_BYTES      = 4
WORDS_PER_BLOCK = BYTES_PER_BLOCK // WORD_BYTES
COLUMNS         = WORD_BYTES

logger = Logger(False)

# ------------------------------------------------------------------------------
# Key schedule utilities
# ------------------------------------------------------------------------------

def str_to_hex_bytes(s: str):
  """
  Convert ASCII string to list of hex strings.
  Each character is converted to its hex representation.
  """
  return [hex(ord(ch)) for ch in s]

def row_to_matrix_rowmajor(key_str: str):
  """
  Take a 16‐byte ASCII string, reshape into 4×4 row‐major hex matrix.
  Used for initial key expansion.
  """
  hexbytes = str_to_hex_bytes(key_str)
  mat = np.reshape(hexbytes, (WORDS_PER_BLOCK, COLUMNS))
  return mat.tolist()

def gf_round_constant(round_index: int):
  """
  Compute AES RCON for a given round index (1..10).
  RCON[1] = 0x01, RCON[i] = 2⋅RCON[i−1] in GF(2^8).
  Used in key expansion.
  """
  if round_index == 1:
    return 0x01
  prev = gf_round_constant(round_index - 1)
  # left shift then reduce by irreducible 0x11b if overflow
  return (prev << 1) ^ (0x11B & (-(prev >> 7)))

def rotate_sub_xor(word: list, round_index: int):
  """
  The g() operation in key expansion:
  - rotate 4‑byte word left by one byte,
  - apply S‑box to each byte,
  - XOR the first byte with RCON.
  """
  rotated = word[1:] + word[:1]
  substituted = [hex(sb.Sbox[int(b,16)]) for b in rotated]
  # XOR first byte with round constant
  rc = gf_round_constant(round_index)
  first = int(substituted[0],16) ^ rc
  substituted[0] = hex(first)
  return substituted

def xor_words(a: list, b: list):
  """
  XOR two 4‑byte words (lists of hex strings).
  Used in key expansion and round key addition.
  """
  return [hex(int(x,16) ^ int(y,16)) for x,y in zip(a,b)]

def derive_next_round_key(prev_words: list, round_idx: int):
  """
  Given 4 words (prev round), produce the next 4‐word round key.
  Implements AES key schedule core.
  """
  new_words = []
  # w0 = w_prev0 XOR g(w_prev3)
  g_out = rotate_sub_xor(prev_words[-1], round_idx)
  new_words.append(xor_words(prev_words[0], g_out))
  # w[i] = w_prev[i] XOR w[i−1]
  for i in range(1, WORDS_PER_BLOCK):
    new_words.append(xor_words(prev_words[i], new_words[i-1]))
  return new_words

def expand_key(master_key: str):
  """
  Expand ASCII master key to all 11 round keys (each 4×4 word matrix).
  Pads/truncates key to 16 bytes, then applies key schedule.
  """
  # ensure exactly 16 chars
  mk = master_key.ljust(BYTES_PER_BLOCK, '0')[:BYTES_PER_BLOCK]
  round_keys = [row_to_matrix_rowmajor(mk)]
  for r in range(1, 11):
    prev = round_keys[-1]
    next_words = derive_next_round_key(prev, r)
    round_keys.append(next_words)
  return round_keys

# ------------------------------------------------------------------------------
# State matrix transformations
# ------------------------------------------------------------------------------

def ascii_to_state(text: str):
  """
  Convert 16‐byte ASCII block to 4×4 state in column‐major order.
  Pads/truncates input, reshapes, and transposes to column-major.
  """
  # pad/truncate
  blk = text.ljust(BYTES_PER_BLOCK, '0')[:BYTES_PER_BLOCK]
  raw = str_to_hex_bytes(blk)
  mat = np.reshape(raw, (WORDS_PER_BLOCK, COLUMNS)).tolist()
  # transpose to column‐major
  return np.array(mat).T.tolist()

def hexstr_to_state(hexstr: str):
  """
  Convert 32‐char hex string into 4×4 state in column‐major order.
  Used for decryption input.
  """
  if len(hexstr) != BYTES_PER_BLOCK*2:
    raise ValueError("Ciphertext block must be 32 hex chars")
  # bytes[i:i+2]  # just for clarity
  arr = [hexstr[i:i+2] for i in range(0, len(hexstr), 2)]
  mat = np.reshape(arr, (WORDS_PER_BLOCK, COLUMNS))
  return mat.T.tolist()

def apply_round_key(state: list, round_words: list):
  """
  XOR the 4×4 state with the round key (given as list of 4 words row‐major).
  Transposes round key to column-major before XOR.
  """
  # transpose round_words into column major
  transposed = np.array(round_words).T.tolist()
  return [xor_words(state[col], transposed[col]) for col in range(WORDS_PER_BLOCK)]

def sub_bytes(state: list):
  """
  Apply S‑box to every byte in the state.
  Used in encryption rounds.
  """
  return [[hex(sb.Sbox[int(b,16)]) for b in row] for row in state]

def inv_sub_bytes(state: list):
  """
  Apply inverse S‑box to every byte in the state.
  Used in decryption rounds.
  """
  return [[hex(sb.InvSbox[int(b,16)]) for b in row] for row in state]

def shift_rows_left(state: list):
  """
  Cyclically shift row i left by i positions.
  Used in encryption rounds.
  """
  return [np.roll(state[row], -row).tolist() for row in range(WORDS_PER_BLOCK)]

def shift_rows_right(state: list):
  """
  Cyclically shift row i right by i positions.
  Used in decryption rounds.
  """
  return [np.roll(state[row], row).tolist() for row in range(WORDS_PER_BLOCK)]

def mix_columns(state: list):
  """
  Mix each column by multiplying with fixed matrix in GF(2^8).
  state is a list of WORDS_PER_BLOCK rows, each COLUMNS long; work column‐wise.
  Used in encryption rounds.
  """
  mat = np.array(state).T  # back to row‑major
  out = []
  for i in range(WORDS_PER_BLOCK):
    newrow = []
    for j in range(COLUMNS):
      acc = 0
      for k in range(WORDS_PER_BLOCK):
        m = Mixer[i][k]
        b = BitVector(intVal=int(mat[j][k],16))
        acc ^= m.gf_multiply_modular(b, AES_modulus, 8).int_val()
      newrow.append(hex(acc))
    out.append(newrow)
  return out

def inv_mix_columns(state: list):
  """
  Inverse mix columns transformation.
  Used in decryption rounds.
  """
  mat = np.array(state).T
  out = []
  for i in range(WORDS_PER_BLOCK):
    newrow = []
    for j in range(COLUMNS):
      acc = 0
      for k in range(WORDS_PER_BLOCK):
        m = InvMixer[i][k]
        b = BitVector(intVal=int(mat[j][k],16))
        acc ^= m.gf_multiply_modular(b, AES_modulus, 8).int_val()
      newrow.append(hex(acc))
    out.append(newrow)
  return out

# ------------------------------------------------------------------------------
# PKCS#7 padding
# ------------------------------------------------------------------------------

def pkcs7_pad(msg: str):
  """
  Pad the message to a multiple of 16 bytes using PKCS#7.
  If already a multiple, returns as is.
  """
  pad_len = BYTES_PER_BLOCK - (len(msg) % BYTES_PER_BLOCK)
  if pad_len == BYTES_PER_BLOCK:
    return msg
  return msg + chr(pad_len)*pad_len

def pkcs7_unpad(msg: str):
  """
  Remove PKCS#7 padding from the message.
  Checks for valid padding before removing.
  """
  last = ord(msg[-1])
  if last<1 or last>BYTES_PER_BLOCK:
    return msg
  if msg.endswith(chr(last)*last):
    return msg[:-last]
  return msg

# ------------------------------------------------------------------------------
# Core AES encrypt/decrypt block
# ------------------------------------------------------------------------------

def encrypt_block(plain16: str, keys: list):
  """
  Encrypt a single 16-byte block using AES-128.
  Applies initial round key, 9 main rounds, and final round.
  Returns 32-character hex string.
  """
  if len(plain16) != BYTES_PER_BLOCK:
    raise ValueError("Block size must be 16 bytes")
  state = ascii_to_state(plain16)
  # initial key
  state = apply_round_key(state, keys[0])
  # rounds 1..9
  for r in range(1,10):
    state = sub_bytes(state)
    state = shift_rows_left(state)
    state = mix_columns(state)
    state = apply_round_key(state, keys[r])
  # final round (no mix_columns)
  state = sub_bytes(state)
  state = shift_rows_left(state)
  state = apply_round_key(state, keys[10])
  # flatten out column‑major, produce 32 hex chars
  ct = ""
  for c in range(WORDS_PER_BLOCK):
    for r in range(COLUMNS):
      byte_hex = state[r][c]
      if byte_hex.startswith("0x"):
        byte_hex = byte_hex[2:]
      if len(byte_hex)==1:
        byte_hex = "0"+byte_hex
      ct += byte_hex
  return ct

def decrypt_block(ct32: str, keys: list):
  """
  Decrypt a single 32-character hex block using AES-128.
  Applies initial round key, 9 main rounds (inverse), and final round.
  Returns 16-byte ASCII string.
  """
  if len(ct32) != BYTES_PER_BLOCK*2:
    raise ValueError("Cipher block must be 32 hex chars")
  state = hexstr_to_state(ct32)
  state = apply_round_key(state, keys[10])
  for r in range(9,0,-1):
    state = shift_rows_right(state)
    state = inv_sub_bytes(state)
    state = apply_round_key(state, keys[r])
    state = inv_mix_columns(state)
  state = shift_rows_right(state)
  state = inv_sub_bytes(state)
  state = apply_round_key(state, keys[0])
  # read out ASCII
  hexout = ""
  for c in range(WORDS_PER_BLOCK):
    for r in range(COLUMNS):
      byte_hex = state[r][c][2:].zfill(2)
      hexout += byte_hex
  return bytearray.fromhex(hexout).decode('latin-1')

# ------------------------------------------------------------------------------
# High‐level AES encrypt/decrypt with padding & logging
# ------------------------------------------------------------------------------

def encrypt(plaintext: str, master_key: str):
  """
  Encrypts the plaintext using AES-128 with PKCS#7 padding.
  Logs plaintext, key, and ciphertext in both ASCII and hex.
  Returns ciphertext as hex string.
  """
  logger.log(f"{bcolors.OKCYAN}Plaintext (ASCII){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{plaintext}{bcolors.ENDC}")
  logger.log(f"{bcolors.OKCYAN}Plaintext (hex){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{plaintext.encode().hex()}{bcolors.ENDC}\n")

  logger.log(f"{bcolors.OKCYAN}Key (ASCII){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{master_key}{bcolors.ENDC}")
  logger.log(f"{bcolors.OKCYAN}Key (hex){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{master_key.encode().hex()}{bcolors.ENDC}\n")

  padded = pkcs7_pad(plaintext)
  t0 = time.time()
  round_keys = expand_key(master_key)
  key_time = time.time() - t0

  ciphertext = ""
  # Encrypt each 16-byte block
  for i in range(0,len(padded), BYTES_PER_BLOCK):
    ciphertext += encrypt_block(padded[i:i+BYTES_PER_BLOCK], round_keys)

  logger.log(f"{bcolors.OKCYAN}Ciphertext (hex){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{ciphertext}{bcolors.ENDC}")
  ascii_ct = BitVector(hexstring=ciphertext).get_bitvector_in_ascii()
  logger.log(f"{bcolors.OKCYAN}Ciphertext (ASCII){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{ascii_ct}{bcolors.ENDC}\n")

  global keySchedulingTime
  keySchedulingTime = key_time
  return ciphertext

def decrypt(ciphertext_hex: str, master_key: str):
  """
  Decrypts the ciphertext hex string using AES-128.
  Removes PKCS#7 padding and logs recovered plaintext.
  Returns plaintext string.
  """
  t1 = time.time()
  round_keys = expand_key(master_key)
  t1 = time.time() - t1

  full = ""
  blk_size = BYTES_PER_BLOCK*2
  # Decrypt each 32-character hex block
  for i in range(0,len(ciphertext_hex), blk_size):
    full += decrypt_block(ciphertext_hex[i:i+blk_size], round_keys)
  clear = pkcs7_unpad(full)

  logger.log(f"{bcolors.OKCYAN}Recovered plaintext (ASCII){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{clear}{bcolors.ENDC}")
  logger.log(f"{bcolors.OKCYAN}Recovered plaintext (hex){bcolors.ENDC}")
  logger.log(f"{bcolors.OKGREEN}{clear.encode().hex()}{bcolors.ENDC}\n")

  return clear