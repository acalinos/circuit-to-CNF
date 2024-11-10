import circuit_to_cnf

# Definizione della funzione di permutazione, che prende in input 
# una lista di bit, 32 o 64
# e una lista che indica come riorganizzarli
def permutation(bits, mapping):
    permuted = [None] * len(mapping)
    for i, bit in enumerate(mapping):
        permuted[i] = bits[bit - 1]
    return permuted

# Definizione della S-box
SBOX_TABLE = [
    # Esempio S-box 4x16 (6-bit input, 4-bit output)
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],  # Row 0
    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],  # Row 1
    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],  # Row 2
    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]   # Row 3
]

def sbox_lookup(bits):
    # Selezione del primo e del sesto bit
    row = (bits[0] << 1) | bits[5]
    # Selezione dei bit dal secondo al quinto
    col = (bits[1] << 3) | (bits[2] << 2) | (bits[3] << 1) | bits[4]
    # Restituzione del valore della S-box
    return SBOX_TABLE[row][col]

# Definizione della funzione F
def function_f(r_half, sub_key):
    # Espansione da 32 bit a 48 bit
    expanded_r = espansione(r_half)  

    # XOR con la sub-chiave
    mixed_bits = [r_bit ^ k_bit for r_bit, k_bit in zip(expanded_r, sub_key)]
    
    # Applicazione delle S-box
    substituted_bits = []
    for i in range(0, 48, 6):
        block = mixed_bits[i:i+6]
        substituted_bits += sbox_lookup(block)

    # Permutazione finale
    return permutation(substituted_bits, PERMUTATION_TABLE)

def espansione(half):
    
