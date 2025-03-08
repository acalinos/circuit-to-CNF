import circuitgraph as cg
from ExtendedCircuitgraph import manual_tseitin_cnf, simulate_circuit

# Permutazione generica
def apply_permutation(circuit, input_wires, perm_table, prefix):
    """
    Applica una permutazione a un insieme di bit.
    """
    output_wires = []
    for i, pos in enumerate(perm_table):
        out_wire = f"{prefix}_p{i}"
        circuit.add(out_wire, 'buf', fanin=[input_wires[pos - 1]])
        output_wires.append(out_wire)
    return output_wires

# Tabella delle permutazioni fisse
IP_TABLE = [58, 50, 42, 34, 26, 18, 10, 2,
            60, 52, 44, 36, 28, 20, 12, 4,
            62, 54, 46, 38, 30, 22, 14, 6,
            64, 56, 48, 40, 32, 24, 16, 8,
            57, 49, 41, 33, 25, 17,  9, 1,
            59, 51, 43, 35, 27, 19, 11, 3,
            61, 53, 45, 37, 29, 21, 13, 5,
            63, 55, 47, 39, 31, 23, 15, 7]

# Initial Permutation (IP)
def initial_permutation(circuit, input_wires):
    return apply_permutation(circuit, input_wires, IP_TABLE, "IP")

# Espansione E (da 32 a 48 bit)
EXPANSION_TABLE = [32,  1,  2,  3,  4,  5,
                    4,  5,  6,  7,  8,  9,
                    8,  9, 10, 11, 12, 13,
                   12, 13, 14, 15, 16, 17,
                   16, 17, 18, 19, 20, 21,
                   20, 21, 22, 23, 24, 25,
                   24, 25, 26, 27, 28, 29,
                   28, 29, 30, 31, 32,  1]

def expansion_permutation(circuit, input_wires):
    return apply_permutation(circuit, input_wires, EXPANSION_TABLE, "E")

# Permutazione P
P_TABLE = [16,  7, 20, 21,
           29, 12, 28, 17,
            1, 15, 23, 26,
            5, 18, 31, 10,
            2,  8, 24, 14,
           32, 27,  3,  9,
           19, 13, 30,  6,
           22, 11,  4, 25]

def p_permutation(circuit, input_wires):
    """
    Implementa la permutazione P utilizzata dopo le S-Box.
    """
    return apply_permutation(circuit, input_wires, P_TABLE, "P")

# Final Permutation (IP^-1)
FP_TABLE = [40, 8, 48, 16, 56, 24, 64, 32,
            39, 7, 47, 15, 55, 23, 63, 31,
            38, 6, 46, 14, 54, 22, 62, 30,
            37, 5, 45, 13, 53, 21, 61, 29,
            36, 4, 44, 12, 52, 20, 60, 28,
            35, 3, 43, 11, 51, 19, 59, 27,
            34, 2, 42, 10, 50, 18, 58, 26,
            33, 1, 41, 9, 49, 17, 57, 25]

def final_permutation(circuit, input_wires):
    """
    Implementa la permutazione finale (inversa della permutazione iniziale).
    """
    return apply_permutation(circuit, input_wires, FP_TABLE, "FP")

# S-Box tables
SBOX_TABLES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

def sbox(sbox_number):
    """
    Genera il circuito logico di una S-Box specifica.
    """
    circuit = cg.Circuit()
    
    sbox_idx = sbox_number - 1  # Indice 0-based per accedere alle tabelle
    sbox_table = SBOX_TABLES[sbox_idx]
    
    # Input wires (6 bits)
    input_wires = [f'sbox{sbox_number}_in{i}' for i in range(6)]
    for wire in input_wires:
        circuit.add(wire, 'input')
    
    # Output wires (4 bits)
    output_wires = [f'sbox{sbox_number}_out{i}' for i in range(4)]
    # We'll add these at the end with proper connections
    
    # Dictionary to keep track of OR gates for each output
    or_nodes = {}
    
    # Implementazione tramite LUT (Look-Up Table)
    for i in range(64):
        # Converti i in binario a 6 bit
        bin_i = format(i, '06b')
        
        # Calcola riga e colonna per la S-Box
        row = int(bin_i[0] + bin_i[5], 2)  # Bit esterno e interno formano la riga
        col = int(bin_i[1:5], 2)           # 4 bit centrali formano la colonna
        
        # Ottieni il valore dalla tabella S-Box
        sbox_value = sbox_table[row][col]
        # Converti il valore in binario a 4 bit
        bin_value = format(sbox_value, '04b')
        
        # Crea un and-gate per ogni combinazione di input
        and_terms = []
        for j, bit in enumerate(bin_i):
            term = input_wires[j] if bit == '1' else f'not_{input_wires[j]}'
            if f'not_{input_wires[j]}' == term:
                if term not in circuit.nodes():
                    circuit.add(term, 'not', fanin=[input_wires[j]])
            and_terms.append(term)
        
        # Crea l'and-gate per questa combinazione
        comb_node = f'comb_{sbox_number}_{i}'
        circuit.add(comb_node, 'and', fanin=and_terms)
        
        # Collega l'output dell'and-gate agli output appropriati
        for j, bit in enumerate(bin_value):
            if bit == '1':
                # Create or retrieve existing OR gate for this output
                or_node = f'or_{sbox_number}_out{j}'
                if or_node not in or_nodes:
                    # Initialize with this AND term
                    or_nodes[or_node] = [comb_node]
                else:
                    # Add this AND term to existing ones
                    or_nodes[or_node].append(comb_node)
    
    # Create the OR gates with all their inputs and connect to outputs
    for j in range(4):
        output_name = output_wires[j]
        or_node = f'or_{sbox_number}_out{j}'
        
        # If this output has any 1's in the truth table
        if or_node in or_nodes:
            # Create the OR gate with all its inputs
            circuit.add(or_node, 'or', fanin=or_nodes[or_node])
            # Create the output buffer connected to the OR gate
            circuit.add(output_name, 'buf', fanin=[or_node])
        else:
            # If this output is always 0, connect it to a constant 0
            circuit.add('const_0', 'const0')
            circuit.add(output_name, 'buf', fanin=['const_0'])
        
        # Mark as output
        circuit.set_output(output_name)
    
    return circuit

def f_function(circuit, right_half, subkey):
    """
    Implementa la funzione F del DES.
    
    Args:
        circuit: Circuito cg esistente
        right_half: Lista dei 32 wire del lato destro
        subkey: Lista dei 48 wire della sottochiave
        
    Returns:
        Lista dei 32 wire di output della funzione F
    """
    # Espansione da 32 a 48 bit
    expanded = expansion_permutation(circuit, right_half)
    
    # XOR con la sottochiave
    xor_outputs = []
    for i in range(48):
        xor_wire = f"xor_E_K_{i}"
        circuit.add(xor_wire, 'xor', fanin=[expanded[i], subkey[i]])
        xor_outputs.append(xor_wire)
    
    # Dividi gli input in 8 gruppi da 6 bit per le S-box
    sbox_inputs = [xor_outputs[i:i+6] for i in range(0, 48, 6)]
    sbox_outputs = []
    
    # Applica le 8 S-box
    for i in range(8):
        # Per ogni S-box, prendi i 6 bit corrispondenti e produci 4 bit di output
        s_box = sbox(i + 1)
        
        # Aggiungi il circuito S-box al circuito principale
        sbox_prefix = f"sbox_{i+1}"
        
        # Mappa gli input della S-box
        sbox_mappings = {}
        for j in range(6):
            sbox_mappings[f'sbox{i+1}_in{j}'] = sbox_inputs[i][j]
        
        # Aggiungi la S-box al circuito
        circuit.add_circuit(s_box, sbox_prefix, sbox_mappings)
        
        # Collect the output nodes
        sbox_out_wires = []
        for j in range(4):
            out_wire = f"{sbox_prefix}_out{j}"
            sbox_out_wires.append(out_wire)
            
        sbox_outputs.extend(sbox_out_wires)
    
    # Permutazione P finale (da 32 a 32 bit)
    permuted = p_permutation(circuit, sbox_outputs)
    
    return permuted

def des_round(circuit, left_half, right_half, subkey, round_num):
    """
    Esegue un singolo round del DES.
    
    Args:
        circuit: Circuito cg esistente
        left_half: Lista dei 32 wire del lato sinistro
        right_half: Lista dei 32 wire del lato destro
        subkey: Lista dei 48 wire della sottochiave
        round_num: Numero del round corrente
        
    Returns:
        Tuple con le liste dei 32 wire sinistri e destri per il round successivo
    """
    # Il nuovo lato sinistro è il vecchio lato destro
    new_left = right_half
    
    # Calcola la funzione F
    f_result = f_function(circuit, right_half, subkey)
    
    # XOR tra il vecchio lato sinistro e l'output della funzione F
    new_right = []
    for i in range(32):
        xor_wire = f"round{round_num}_R_{i}"
        circuit.add(xor_wire, 'xor', fanin=[left_half[i], f_result[i]])
        new_right.append(xor_wire)
    
    return new_left, new_right

def key_schedule(circuit, key_wires):
    """
    Implementa lo schedule delle chiavi per generare le 16 sottochiavi.
    
    Args:
        circuit: Circuito cg esistente
        key_wires: Lista dei 64 wire della chiave iniziale
        
    Returns:
        Lista di 16 liste, ognuna contenente 48 wire per una sottochiave
    """
    # PC-1: Permuted Choice 1 (da 64 a 56 bit)
    PC1_TABLE = [57, 49, 41, 33, 25, 17, 9,
                 1, 58, 50, 42, 34, 26, 18,
                 10, 2, 59, 51, 43, 35, 27,
                 19, 11, 3, 60, 52, 44, 36,
                 63, 55, 47, 39, 31, 23, 15,
                 7, 62, 54, 46, 38, 30, 22,
                 14, 6, 61, 53, 45, 37, 29,
                 21, 13, 5, 28, 20, 12, 4]
    
    pc1_output = apply_permutation(circuit, key_wires, PC1_TABLE, "PC1")
    
    # Dividi in metà sinistra e destra (C e D)
    C = pc1_output[:28]
    D = pc1_output[28:]
    
    # Schedule di rotazione per ogni round
    SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    
    # PC-2: Permuted Choice 2 (da 56 a 48 bit)
    PC2_TABLE = [14, 17, 11, 24, 1, 5,
                 3, 28, 15, 6, 21, 10,
                 23, 19, 12, 4, 26, 8,
                 16, 7, 27, 20, 13, 2,
                 41, 52, 31, 37, 47, 55,
                 30, 40, 51, 45, 33, 48,
                 44, 49, 39, 56, 34, 53,
                 46, 42, 50, 36, 29, 32]
    
    subkeys = []
    
    for i in range(16):
        # Rotazione circolare a sinistra
        shift = SHIFT_SCHEDULE[i]
        
        # Rotazione per C
        new_C = []
        for j in range(28):
            src_idx = (j - shift) % 28
            rot_wire = f"C{i+1}_{j}"
            circuit.add(rot_wire, 'buf', fanin=[C[src_idx]])
            new_C.append(rot_wire)
        C = new_C
        
        # Rotazione per D
        new_D = []
        for j in range(28):
            src_idx = (j - shift) % 28
            rot_wire = f"D{i+1}_{j}"
            circuit.add(rot_wire, 'buf', fanin=[D[src_idx]])
            new_D.append(rot_wire)
        D = new_D
        
        # Combina C e D e applica PC-2
        CD = C + D
        subkey = apply_permutation(circuit, CD, PC2_TABLE, f"K{i+1}")
        subkeys.append(subkey)
    
    return subkeys

def des_block(circuit, input_block, key_wires):
    """
    Esegue l'intero algoritmo DES su un blocco di input.
    
    Args:
        circuit: Circuito cg esistente
        input_block: Lista dei 64 wire di input
        key_wires: Lista dei 64 wire della chiave
        
    Returns:
        Lista dei 64 wire dell'output cifrato
    """
    # Genera le sottochiavi
    round_keys = key_schedule(circuit, key_wires)
    
    # Permutazione iniziale
    permuted = initial_permutation(circuit, input_block)
    
    # Dividi in metà sinistra e destra
    left, right = permuted[:32], permuted[32:]
    
    # 16 round di Feistel
    for i in range(16):
        left, right = des_round(circuit, left, right, round_keys[i], i+1)
    
    # Scambio finale (contrario al tipico Feistel)
    pre_output = right + left
    
    # Permutazione finale
    output_block = final_permutation(circuit, pre_output)
    
    return output_block

def create_des_circuit(plaintext_hex, key_hex):
    """
    Crea un circuito DES completo con input e key specifici.
    
    Args:
        plaintext_hex: Stringa esadecimale di 16 caratteri (64 bit)
        key_hex: Stringa esadecimale di 16 caratteri (64 bit)
    
    Returns:
        Circuito DES, nomi input e nomi output
    """
    circuit = cg.Circuit()
    
    # Conversione input esadecimale in binario
    plaintext_bin = bin(int(plaintext_hex, 16))[2:].zfill(64)
    key_bin = bin(int(key_hex, 16))[2:].zfill(64)
    
    # Crea input wires per il plaintext
    input_wires = []
    for i in range(64):
        wire_name = f"plaintext_{i}"
        circuit.add(wire_name, 'input')
        input_wires.append(wire_name)
        
        # Se l'input deve essere fisso, aggiungiamo un buffer con valore costante
        if plaintext_bin[i] == '1':
            circuit.add(f"const1_{i}", 'buf', fanin=[wire_name])
        else:
            circuit.add(f"const0_{i}", 'not', fanin=[wire_name])
    
    # Crea input wires per la chiave
    key_wires = []
    for i in range(64):
        wire_name = f"key_{i}"
        circuit.add(wire_name, 'input')
        key_wires.append(wire_name)
        
        # Se la chiave deve essere fissa, aggiungiamo un buffer con valore costante
        if key_bin[i] == '1':
            circuit.add(f"key_const1_{i}", 'buf', fanin=[wire_name])
        else:
            circuit.add(f"key_const0_{i}", 'not', fanin=[wire_name])
    
    # Esegui l'algoritmo DES
    output_wires = des_block(circuit, input_wires, key_wires)
    
    # Marca gli output
    for wire in output_wires:
        circuit.set_output(wire)
    
    return circuit, input_wires, output_wires

def des_encrypt(plaintext_hex, key_hex):
    """
    Cifra un blocco di plaintext usando DES.
    
    Args:
        plaintext_hex: Stringa esadecimale di 16 caratteri (64 bit)
        key_hex: Stringa esadecimale di 16 caratteri (64 bit)
        
    Returns:
        Stringa esadecimale del ciphertext
    """
    circuit, input_wires, output_wires = create_des_circuit(plaintext_hex, key_hex)
    
    # Simula il circuito
    sim_results = simulate_circuit(circuit, {})
    
    # Raccogli gli output in ordine
    output_bits = ""
    for wire in output_wires:
        output_bits += "1" if sim_results[wire] else "0"
    
    # Converti in esadecimale
    ciphertext_hex = hex(int(output_bits, 2))[2:].zfill(16)
    
    return ciphertext_hex