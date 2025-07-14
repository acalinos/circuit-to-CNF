import circuitgraph as cg
from ExtendedCircuitgraph_old import manual_tseitin_cnf, simulate_circuit

DEBUG = True

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

# Permutazione generica
def apply_permutation(circuit, input_wires, perm_table, prefix):
    output_wires = []
    for i, pos in enumerate(perm_table):
        out_wire = f"{prefix}p{i}"
        circuit.add(out_wire, 'buf', fanin=[input_wires[pos - 1]])
        output_wires.append(out_wire)
    # debug_print(f"[DEBUG] Permutazione {prefix}: {output_wires}")
    return output_wires

# Tabelle di permutazione
IP_TABLE = [58, 50, 42, 34, 26, 18, 10, 2,
            60, 52, 44, 36, 28, 20, 12, 4,
            62, 54, 46, 38, 30, 22, 14, 6,
            64, 56, 48, 40, 32, 24, 16, 8,
            57, 49, 41, 33, 25, 17,  9, 1,
            59, 51, 43, 35, 27, 19, 11, 3,
            61, 53, 45, 37, 29, 21, 13, 5,
            63, 55, 47, 39, 31, 23, 15, 7]

def initial_permutation(circuit, input_wires):
    return apply_permutation(circuit, input_wires, IP_TABLE, "IP")

EXPANSION_TABLE = [32,  1,  2,  3,  4,  5,
                   4,  5,  6,  7,  8,  9,
                   8,  9, 10, 11, 12, 13,
                  12, 13, 14, 15, 16, 17,
                  16, 17, 18, 19, 20, 21,
                  20, 21, 22, 23, 24, 25,
                  24, 25, 26, 27, 28, 29,
                  28, 29, 30, 31, 32,  1]

def expansion_permutation(circuit, input_wires, prefix="E_"):
    return apply_permutation(circuit, input_wires, EXPANSION_TABLE, prefix)

P_TABLE = [16,  7, 20, 21,
           29, 12, 28, 17,
            1, 15, 23, 26,
            5, 18, 31, 10,
            2,  8, 24, 14,
           32, 27,  3,  9,
           19, 13, 30,  6,
           22, 11,  4, 25]

def p_permutation(circuit, input_wires, prefix="P_"):
    return apply_permutation(circuit, input_wires, P_TABLE, prefix)

FP_TABLE = [40, 8, 48, 16, 56, 24, 64, 32,
            39, 7, 47, 15, 55, 23, 63, 31,
            38, 6, 46, 14, 54, 22, 62, 30,
            37, 5, 45, 13, 53, 21, 61, 29,
            36, 4, 44, 12, 52, 20, 60, 28,
            35, 3, 43, 11, 51, 19, 59, 27,
            34, 2, 42, 10, 50, 18, 58, 26,
            33, 1, 41, 9, 49, 17, 57, 25]

def final_permutation(circuit, input_wires):
    return apply_permutation(circuit, input_wires, FP_TABLE, "FP")

# Tabelle S-Box
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

def f_function(circuit, right_half, subkey, round_num):
    round_prefix = f"r{round_num}_"
    expanded = expansion_permutation(circuit, right_half, f"{round_prefix}E_")
    # debug_print(f"[DEBUG] Round {round_num} - Espansione: {expanded}")
    xor_outputs = []
    for i in range(48):
        xor_wire = f"{round_prefix}xor_E_K_{i}"
        circuit.add(xor_wire, 'xor', fanin=[expanded[i], subkey[i]])
        xor_outputs.append(xor_wire)
    # debug_print(f"[DEBUG] Round {round_num} - XOR outputs: {xor_outputs}")
    sbox_inputs = [xor_outputs[i:i+6] for i in range(0, 48, 6)]
    sbox_outputs = []
    for sbox_number in range(1, 9):
        i = sbox_number - 1
        sbox_table = SBOX_TABLES[i]
        input_wires = sbox_inputs[i]
        output_wires = [f"{round_prefix}sbox{sbox_number}_out{j}" for j in range(4)]
        not_wires_dict = {}
        for j, wire in enumerate(input_wires):
            not_wire_name = f"{round_prefix}sbox{sbox_number}_not_in{j}"
            if not_wire_name not in circuit.nodes():
                circuit.add(not_wire_name, 'not', fanin=[wire])
            not_wires_dict[j] = not_wire_name
        or_inputs = {j: [] for j in range(4)}
        for comb_idx in range(64):
            bin_comb = format(comb_idx, '06b')
            row = int(bin_comb[0] + bin_comb[5], 2)
            col = int(bin_comb[1:5], 2)
            sbox_value = sbox_table[row][col]
            bin_value = format(sbox_value, '04b')
            and_terms = []
            for j, bit in enumerate(bin_comb):
                if bit == '1':
                    and_terms.append(input_wires[j])
                else:
                    and_terms.append(not_wires_dict[j])
            and_wire = f"{round_prefix}sbox{sbox_number}_and_{comb_idx}"
            circuit.add(and_wire, 'and', fanin=and_terms)
            for j, bit in enumerate(bin_value):
                if bit == '1':
                    or_inputs[j].append(and_wire)
        for j in range(4):
            if or_inputs[j]:
                or_wire = f"{round_prefix}sbox{sbox_number}_or_{j}"
                circuit.add(or_wire, 'or', fanin=or_inputs[j])
                circuit.add(output_wires[j], 'buf', fanin=[or_wire])
            else:
                const_wire = f"{round_prefix}const0_{sbox_number}_{j}"
                if const_wire not in circuit.nodes():
                    circuit.add(const_wire, 'buf', fanin=["CONST0"])
                circuit.add(output_wires[j], 'buf', fanin=[const_wire])
        # NON invertiamo l'ordine: usiamo l'ordine naturale dei bit (MSB in output_wires[0])
        sbox_outputs.extend(output_wires)
        # debug_print(f"[DEBUG] Round {round_num} - SBox {sbox_number} output wires: {output_wires}")
    permuted = p_permutation(circuit, sbox_outputs, f"{round_prefix}P_")
    # debug_print(f"[DEBUG] Round {round_num} - Permutazione P: {permuted}")
    return permuted

def des_round(circuit, left_half, right_half, subkey, round_num):
    new_left = right_half
    f_result = f_function(circuit, right_half, subkey, round_num)
    new_right = []
    for i in range(32):
        xor_wire = f"r{round_num}_R_{i}"
        circuit.add(xor_wire, 'xor', fanin=[left_half[i], f_result[i]])
        new_right.append(xor_wire)
    # debug_print(f"[DEBUG] Round {round_num} - new_right: {new_right}")
    return new_left, new_right

def key_schedule(circuit, key_wires):
    PC1_TABLE = [57, 49, 41, 33, 25, 17, 9,
                 1, 58, 50, 42, 34, 26, 18,
                 10, 2, 59, 51, 43, 35, 27,
                 19, 11, 3, 60, 52, 44, 36,
                 63, 55, 47, 39, 31, 23, 15,
                 7, 62, 54, 46, 38, 30, 22,
                 14, 6, 61, 53, 45, 37, 29,
                 21, 13, 5, 28, 20, 12, 4]
    pc1_output = apply_permutation(circuit, key_wires, PC1_TABLE, "PC1")
    C = pc1_output[:28]
    D = pc1_output[28:]
    SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
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
        shift = SHIFT_SCHEDULE[i]
        # Rotazione a sinistra (j + shift) % 28
        new_C = []
        for j in range(28):
            src_idx = (j + shift) % 28
            rot_wire = f"C{i+1}_{j}"
            circuit.add(rot_wire, 'buf', fanin=[C[src_idx]])
            new_C.append(rot_wire)
        C = new_C

        new_D = []
        for j in range(28):
            src_idx = (j + shift) % 28
            rot_wire = f"D{i+1}_{j}"
            circuit.add(rot_wire, 'buf', fanin=[D[src_idx]])
            new_D.append(rot_wire)
        D = new_D
        CD = C + D
        subkey = apply_permutation(circuit, CD, PC2_TABLE, f"K{i+1}")
        subkeys.append(subkey)
        # debug_print(f"[DEBUG] Sottochiave round {i+1}: {subkey}")
    return subkeys

def des_block(circuit, input_block, key_wires):
    round_keys = key_schedule(circuit, key_wires)
    permuted = initial_permutation(circuit, input_block)
    left, right = permuted[:32], permuted[32:]
    for i in range(16):
        left, right = des_round(circuit, left, right, round_keys[i], i+1)
    pre_output = right + left
    output_block = final_permutation(circuit, pre_output)
    # debug_print("[DEBUG] Output wires finali:", output_block)
    return output_block

def create_des_circuit(plaintext_hex, key_hex):
    circuit = cg.Circuit()
    # Nodi costanti globali
    circuit.add("CONST0", "input")
    circuit.add("CONST1", "input")
    plaintext_bin = bin(int(plaintext_hex, 16))[2:].zfill(64)
    key_bin = bin(int(key_hex, 16))[2:].zfill(64)
    input_wires = []
    # Creazione dei nodi per il plaintext
    for i in range(64):
        wire_name = f"plaintext_{i}"
        circuit.add(wire_name, 'input')
        input_wires.append(wire_name)
        if plaintext_bin[i] == '1':
            circuit.add(f"const1_{i}", 'buf', fanin=["CONST1"])
        else:
            circuit.add(f"const0_{i}", 'buf', fanin=["CONST0"])

    key_wires = []
    # Creazione dei nodi per la chiave
    for i in range(64):
        wire_name = f"key_{i}"
        circuit.add(wire_name, 'input')
        key_wires.append(wire_name)
        if key_bin[i] == '1':
            circuit.add(f"key_const1_{i}", 'buf', fanin=["CONST1"])
        else:
            circuit.add(f"key_const0_{i}", 'buf', fanin=["CONST0"])

    output_wires = des_block(circuit, input_wires, key_wires)
    for wire in output_wires:
        circuit.set_output(wire)
    # debug_print("[DEBUG] Circuit creato con", len(circuit.nodes()), "nodi.")
    return circuit, input_wires, output_wires

def des_encrypt(plaintext_hex, key_hex):
    circuit, input_wires, output_wires = create_des_circuit(plaintext_hex, key_hex)
    plaintext_bin = bin(int(plaintext_hex, 16))[2:].zfill(64)
    key_bin = bin(int(key_hex, 16))[2:].zfill(64)
    input_values = {}
    # Assegna valori costanti globali
    input_values["CONST0"] = False
    input_values["CONST1"] = True
    for i, bit in enumerate(plaintext_bin):
        input_values[f"plaintext_{i}"] = (bit == '1')
    for i, bit in enumerate(key_bin):
        input_values[f"key_{i}"] = (bit == '1')
    sim_results = simulate_circuit(circuit, input_values)
    debug_round1 = {node: sim_results[node] for node in sim_results if node.startswith("r1_")}
    # debug_print("[DEBUG] Stato simulazione round 1:", debug_round1)
    output_bits = "".join("1" if sim_results[wire] else "0" for wire in output_wires)
    ciphertext_hex = hex(int(output_bits, 2))[2:].upper().zfill(16)
    return ciphertext_hex
