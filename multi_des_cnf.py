# multi_des_cnf.py
import circuitgraph as cg
from archive.ExtendedCircuitgraph_0 import manual_tseitin_cnf
import des_circuit   # importiamo il modulo intero, per poter settare INSTANCE_PREFIX

def build_des_instance(circuit, pt_wires, ct_wires, key_wires, rounds, inst_prefix):
    """
    Aggiunge a `circuit` una istanza DES a `rounds` round,
    con input pt_wires (64), output ct_wires (64) e chiave key_wires (64),
    utilizzando `inst_prefix` per il namespace interno.
    """
    # Imposto il namespace per questa istanza
    des_circuit.INSTANCE_PREFIX = inst_prefix

    # 1) key schedule
    subkeys = des_circuit.key_schedule(circuit, key_wires)[:rounds]

    # 2) initial permutation
    perm = des_circuit.initial_permutation(circuit, pt_wires)
    L, R = perm[:32], perm[32:]

    # 3) rounds
    for i in range(rounds):
        newL = R
        F = des_circuit.f_function(circuit, R, subkeys[i], i+1)
        newR = []
        for j in range(32):
            w = f"{inst_prefix}r{rounds}_{i}_{j}"
            circuit.add(w, "xor", fanin=[L[j], F[j]])
            newR.append(w)
        L, R = newL, newR

    # 4) final permutation
    preout = R + L
    outw = des_circuit.final_permutation(circuit, preout)

    # colleghiamo outw sui ct_wires desiderati
    for src, dst in zip(outw, ct_wires):
        circuit.add(f"{inst_prefix}eq_{dst}", "xnor", fanin=[src, dst])

    # Resetto il namespace per non inquinare le istanze successive
    des_circuit.INSTANCE_PREFIX = ""

    return

def create_multi_des_cnf(pairs, rounds):
    """
    pairs: lista di tuple (plaintext_hex, ciphertext_hex)
    rounds: numero di DES rounds da usare
    Torna un oggetto CNF con:
      - n*64 input-pt
      - n*64 input-ct
      - 64 key
      - n*eq nodi che forzano eq input-ct=DES(output)
    """
    C = cg.Circuit()
    # costanti globali
    C.add("CONST0", "input")
    C.add("CONST1", "input")

    # nodi chiave
    key_wires = [f"k_{i}" for i in range(64)]
    for k in key_wires:
        C.add(k, "input")

    # per ogni istanza, PT e CT e DES
    for inst, (pt_hex, ct_hex) in enumerate(pairs):
        inst_prefix = f"inst{inst}_"

        # plaintext
        pt_bin = bin(int(pt_hex,16))[2:].zfill(64)
        pt_w = []
        for j, b in enumerate(pt_bin):
            w = f"{inst_prefix}pt_{j}"
            C.add(w, "input")
            const = "CONST1" if b=="1" else "CONST0"
            C.add(f"{inst_prefix}ptf_{j}", "buf", fanin=[const])
            pt_w.append(w)

        # ciphertext
        ct_bin = bin(int(ct_hex,16))[2:].zfill(64)
        ct_w = []
        for j, b in enumerate(ct_bin):
            w = f"{inst_prefix}ct_{j}"
            C.add(w, "input")
            const = "CONST1" if b=="1" else "CONST0"
            C.add(f"{inst_prefix}ctf_{j}", "buf", fanin=[const])
            ct_w.append(w)

        # aggiungo l'istanza DES con prefisso univoco
        build_des_instance(C, pt_w, ct_w, key_wires, rounds, inst_prefix)

    # Tseitin -> CNF
    return manual_tseitin_cnf(C)
