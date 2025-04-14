#!/usr/bin/env python3
import sys

DEBUG = True

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# ==========================================
#  Funzioni di conversione da/verso esadecimale
# ==========================================
def hex_to_bin(hex_string):
    """Converte una stringa esadecimale in una stringa binaria, col padding corretto."""
    return bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)

def bin_to_hex(bin_string):
    """Converte una stringa binaria in una stringa esadecimale, con padding."""
    return hex(int(bin_string, 2))[2:].upper().zfill(len(bin_string)//4)

# ==========================================
#  Inversione dei bit in ogni byte
# ==========================================
def reverse_bits_in_bytes(bit_string):
    """Per ogni blocco di 8 bit (byte), inverte l’ordine dei bit."""
    result = []
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        result.append(byte[::-1])
    return ''.join(result)

# ==========================================
#  Funzione di permutazione
# ==========================================
def permute(bit_string, table):
    """Riorganizza la stringa di bit secondo la tabella data.
    La tabella contiene posizioni (1-indexed) che indicano l’ordine in output."""
    return ''.join(bit_string[i - 1] for i in table)

# ==========================================
#  Left Circular Shift
# ==========================================
def left_shift(bits, n):
    """Esegue una rotazione circolare a sinistra del bit-string di n posizioni."""
    return bits[n:] + bits[:n]

# ==========================================
#  Tabelle DES
# ==========================================
IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

FP_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

PC2_TABLE = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

EXPANSION_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

P_TABLE = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

# Le 8 S-Box DES (0-indexate)
S_BOX = {
    0: [
        [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
        [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
        [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
        [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]
    ],
    1: [
        [15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
        [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
        [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
        [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]
    ],
    2: [
        [10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
        [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
        [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
        [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]
    ],
    3: [
        [7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
        [13,8,11,7,6,15,0,3,4,1,2,12,5,10,14,9],
        [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
        [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]
    ],
    4: [
        [2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
        [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
        [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
        [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]
    ],
    5: [
        [12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
        [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
        [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
        [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]
    ],
    6: [
        [4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
        [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
        [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
        [7,13,12,11,9,1,15,2,0,6,10,4,5,8,3,14]
    ],
    7: [
        [14,2,11,4,7,13,1,5,0,15,10,3,9,8,12,6],
        [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
        [7,13,4,1,0,10,6,12,11,9,2,15,14,3,5,8],
        [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]
    ]
}

# ==========================================
#  Funzione S-Box (sbox_substitution)
# ==========================================
def sbox_substitution(xor_result):
    """Divide la stringa di 48 bit in 8 blocchi da 6 bit, applica le S-Box e restituisce 32 bit."""
    output = ""
    for i in range(0, 48, 6):
        chunk = xor_result[i:i+6]
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        sbox_index = i // 6
        s_val = S_BOX[sbox_index][row][col]
        out_bits = format(s_val, '04b')
        debug_print(f"S-Box {sbox_index+1} (blocco {chunk}): riga={row}, colonna={col}, uscita={out_bits}")
        output += out_bits
    return output

# ==========================================
#  Funzione f (DES f-function)
# ==========================================
def f_function(R, subkey):
    """Calcola la funzione f: espansione, XOR con la sottochiave, sostituzione S-Box, permutazione P."""
    expanded_R = permute(R, EXPANSION_TABLE)
    debug_print(f"R espanso (48 bit): {expanded_R} (length={len(expanded_R)})")
    # XOR con la sottochiave
    xor_result = ''.join('1' if expanded_R[i] != subkey[i] else '0' for i in range(48))
    debug_print(f"Risultato XOR (48 bit): {xor_result}")
    sbox_out = sbox_substitution(xor_result)
    debug_print(f"Output f_function dopo S-Box: {sbox_out} (length={len(sbox_out)})")
    final_output = permute(sbox_out, P_TABLE)
    debug_print(f"Output f_function dopo P_TABLE (32 bit): {final_output} (length={len(final_output)})")
    return final_output

# ==========================================
#  Generazione delle Sottochiavi
# ==========================================
def generate_subkeys(key_bin):
    """Genera 16 sottochiavi DES (48 bit ciascuna) a partire dalla chiave a 64 bit."""
    key56 = permute(key_bin, PC1_TABLE)
    debug_print(f"Chiave dopo PC1 (56 bit): {key56} (length={len(key56)})")
    C = key56[:28]
    D = key56[28:]
    subkeys = []
    shift_schedule = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    for i in range(16):
        C = left_shift(C, shift_schedule[i])
        D = left_shift(D, shift_schedule[i])
        combined = C + D
        subkey = permute(combined, PC2_TABLE)
        subkeys.append(subkey)
        debug_print(f"Sottochiave round {i+1}: {subkey} (length={len(subkey)})")
    return subkeys

# ==========================================
#  Funzione DES per l’encryption
# ==========================================
def des_encrypt(plaintext_hex, key_hex):
    # Conversione esadecimale a binario
    plaintext_bin = hex_to_bin(plaintext_hex)
    key_bin = hex_to_bin(key_hex)
    debug_print(f"hex_to_bin({plaintext_hex}) = {plaintext_bin}")
    debug_print(f"hex_to_bin({key_hex}) = {key_bin}")
    debug_print(f"Plaintext (binario): {plaintext_bin} (length={len(plaintext_bin)})")
    debug_print(f"Chiave (binario): {key_bin} (length={len(key_bin)})")

    # Inversione dei bit in ogni byte del plaintext
    plaintext_rev = reverse_bits_in_bytes(plaintext_bin)
    debug_print(f"reverse_bits_in_bytes({plaintext_bin}) = {plaintext_rev}")
    debug_print(f"Plaintext dopo inversione byte: {plaintext_rev} (length={len(plaintext_rev)})")

    # Applicazione della Initial Permutation (IP)
    ip = permute(plaintext_rev, IP_TABLE)
    debug_print(f"Dopo IP (64 bit): {ip} (length={len(ip)})")

    # Generazione delle 16 sottochiavi DES
    subkeys = generate_subkeys(key_bin)

    # Divisione in L (sinistra) e R (destra), 32 bit ciascuno
    L = ip[:32]
    R = ip[32:]
    debug_print(f"L iniziale: {L} (length={len(L)})")
    debug_print(f"R iniziale: {R} (length={len(R)})")

    # Ciclo dei 16 round DES
    for round_no in range(16):
        f_out = f_function(R, subkeys[round_no])
        new_R = ''.join('1' if L[i] != f_out[i] else '0' for i in range(32))
        L, R = R, new_R
        debug_print(f"Round {round_no+1}:")
        debug_print(f"    L = {L}")
        debug_print(f"    R = {R}")

    # Preoutput: concatenazione di R e L (NOTA: swap finale)
    preoutput = R + L
    debug_print(f"Preoutput (R || L) prima di FP: {preoutput} (length={len(preoutput)})")

    # Applicazione della Final Permutation (FP)
    fp = permute(preoutput, FP_TABLE)
    debug_print(f"Output dopo FP (ciphertext binario): {fp} (length={len(fp)})")

    # Inversione dei bit in ogni byte del ciphertext
    final_output = reverse_bits_in_bytes(fp)
    debug_print(f"reverse_bits_in_bytes({fp}) = {final_output}")
    debug_print(f"Ciphertext dopo inversione byte finale: {final_output} (length={len(final_output)})")

    return bin_to_hex(final_output)

# ==========================================
#  Funzione main
# ==========================================
def main():
    # Test vector DES:
    plaintext = "0123456789ABCDEF"
    key = "0000000000000000"
    expected = "95F8A5E5DD31D900"
    result = des_encrypt(plaintext, key)
    print("Test Vector DES")
    print(f"Plaintext:           {plaintext}")
    print(f"Key:                 {key}")
    print(f"Expected Ciphertext: {expected}")
    print(f"Calculated Ciphertext: {result}")
    print(f"Test {'PASSED' if result == expected else 'FAILED'}")

if __name__ == '__main__':
    main()
