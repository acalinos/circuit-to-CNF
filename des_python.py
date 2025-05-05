# Funzioni di utilità per conversione tra esadecimale e binario
def hex_to_bin(hexstr):
    """Converte una stringa esadecimale in una stringa binaria con padding opportuno."""
    return bin(int(hexstr, 16))[2:].zfill(len(hexstr) * 4)

def bin_to_hex(binstr):
    """Converte una stringa di bit in una stringa esadecimale con padding opportuno."""
    return hex(int(binstr, 2))[2:].upper().zfill(len(binstr) // 4)

def xor(a, b):
    """Esegue l’operazione XOR tra due stringhe di bit della stessa lunghezza."""
    return "".join('1' if x != y else '0' for x, y in zip(a, b))

def permute(block, table):
    """
    Permuta il blocco di bit secondo la tabella.
    La tabella è una lista di interi (1-indexed).
    """
    return "".join(block[i - 1] for i in table)

def left_shift(bits, n):
    """Effettua la rotazione a sinistra di una stringa di bit di n posizioni."""
    return bits[n:] + bits[:n]

############################################
# Tabelle DES standard
############################################

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

EXPANSION = [
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

# Permutazione chiave: PC1 (elimino i bit di parità)
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# Permutazione chiave: PC2 (riduce da 56 a 48 bit)
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Tabelle S-Box: otto S-Box, ciascuna con 4 righe e 16 colonne
S_BOX = [
    [  # S1
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    [  # S2
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    [  # S3
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    [  # S4
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    [  # S5
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [  # S6
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    [  # S7
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    [  # S8
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ]
]

############################################
# IMPLEMENTAZIONE DI DES "PURO" (SENZA CIRCUITI)
############################################

def generate_subkeys(key_bin):
    """
    Genera 16 sottochiavi (48 bit ciascuna) a partire dalla chiave a 64 bit.
    
    Passaggi:
      1. Applica la permutazione PC1 per ottenere 56 bit.
      2. Divide il risultato in due metà da 28 bit (C e D).
      3. Esegue 16 rotazioni a sinistra (secondo SHIFT_SCHEDULE) su C e D.
      4. Per ogni round, concatena C e D e applica PC2 per ottenere una sottochiave da 48 bit.
    
    Ritorna una lista di 16 stringhe binarie.
    """
    # Applica PC1 per ridurre la chiave da 64 a 56 bit
    key56 = permute(key_bin, PC1)
    # Divide in due metà
    C = key56[:28]
    D = key56[28:]
    subkeys = []
    for shift in SHIFT_SCHEDULE:
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        # Concatena C e D (56 bit) e applica PC2 per ottenere 48 bit
        combined = C + D
        subkey = permute(combined, PC2)
        subkeys.append(subkey)
    return subkeys

def f_function(R, subkey):
    """
    Funzione di round f.
    
    1. Espande R (32 bit) a 48 bit usando la tabella EXPANSION.
    2. Esegue l'XOR con la sottochiave (48 bit).
    3. Suddivide il risultato in 8 blocchi da 6 bit e, per ciascun blocco, utilizza la corrispondente S-Box per ottenere 4 bit.
    4. Concatena i 32 bit ottenuti e applica la permutazione P_TABLE.
    
    Ritorna una stringa binaria a 32 bit.
    """
    # Espansione: da 32 a 48 bit
    expanded_R = permute(R, EXPANSION)
    # XOR con la sottochiave
    xor_result = xor(expanded_R, subkey)
    # S-box substitution: dividi in 8 blocchi da 6 bit
    sbox_result = ""
    for i in range(8):
        block = xor_result[i*6:(i+1)*6]
        # Calcola riga: unisce il primo e l'ultimo bit
        row = int(block[0] + block[5], 2)
        # Calcola colonna: i 4 bit centrali
        col = int(block[1:5], 2)
        s_val = S_BOX[i][row][col]
        # Converte s_val in 4 bit binari
        sbox_result += bin(s_val)[2:].zfill(4)
    # Applica la permutazione P
    final_result = permute(sbox_result, P_TABLE)
    return final_result

def des_encrypt(plaintext_hex, key_hex):
    """
    Esegue l'encryption DES su un blocco di 64 bit.
    
    Parametri:
      - plaintext_hex: stringa esadecimale di 16 caratteri (64 bit).
      - key_hex: stringa esadecimale di 16 caratteri (64 bit).
    
    Ritorna:
      - ciphertext_hex: stringa esadecimale di 16 caratteri con il ciphertext.
    """
    # Conversione in binario a 64 bit
    plaintext_bin = hex_to_bin(plaintext_hex)
    key_bin = hex_to_bin(key_hex)
    
    # Applica la permutazione iniziale (IP)
    permuted = permute(plaintext_bin, IP)
    L = permuted[:32]
    R = permuted[32:]
    
    # Genera le 16 sottochiavi (48 bit ciascuna)
    subkeys = generate_subkeys(key_bin)
    
    # Esegue 16 round
    for i in range(16):
        temp = R
        # Calcola f(R, subkey)
        f_out = f_function(R, subkeys[i])
        # Nuovo R è dato da L XOR f(R, subkey)
        R = xor(L, f_out)
        L = temp
    # Dopo 16 round, il preoutput è la concatenazione di R e L (swap finale)
    preoutput = R + L
    # Applica la permutazione finale (FP)
    cipher_bin = permute(preoutput, FP)
    
    # Converte il blocco binario a esadecimale e ritorna il ciphertext
    ciphertext_hex = bin_to_hex(cipher_bin)
    return ciphertext_hex

############################################
# ESECUZIONE DI UN TEST DI DES
############################################

def main():
    # Test vector standard DES
    plaintext = "0123456789ABCDEF"
    # Chiave tutto a 0 (64 bit)
    key = "0000000000000000"
    expected_ciphertext = "95F8A5E5DD31D900"
    
    ciphertext = des_encrypt(plaintext, key)
    print("Test Vector DES")
    print("Plaintext:         ", plaintext)
    print("Key:               ", key)
    print("Expected Ciphertext:", expected_ciphertext)
    print("Calculated Ciphertext:", ciphertext)
    print("Test", "PASSED" if ciphertext == expected_ciphertext else "FAILED")

if __name__ == "__main__":
    main()
