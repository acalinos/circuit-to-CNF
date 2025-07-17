# multi_des.py
"""
Costruzione di un circuito composto da più istanze di DES
sulla base della libreria Circuit e del builder build_des_instance.
"""

from typing import List, Tuple, Dict
from new_ExtendedCircuitgraph import Circuit
from multi_des_cnf import build_des_instance  # signature: (circuit, pt_wires, ct_wires, key_wires, rounds, inst_prefix)
from solver import is_satisfiable
from des_python import des_encrypt_block

def clone_circuit_with_prefix(circuit: Circuit, prefix: str) -> Circuit:
    """
    Clona un circuito rinominando tutti i wire usando un prefisso.
    """
    new_circ = Circuit()
    for gate in circuit.gates:
        new_inputs = [prefix + w for w in gate.inputs]
        new_output = prefix + gate.output
        new_circ.add_gate(gate.gate_type, new_inputs, new_output)
    return new_circ

def build_multi_des(
    pairs_xy: List[Tuple[Dict[str, bool], Dict[str, bool]]],
    n_rounds: int = 16
) -> Tuple[Circuit, Dict[str, bool], Dict[str, bool]]:
    """
    Costruisce un circuito composto da tante istanze di DES quante coppie in pairs_xy.

    Args:
        pairs_xy: lista di tuple (input_map, output_map) per ogni istanza;
                  le chiavi dei dizionari sono i nomi di wire nel DES base (es. 'pt0', ..., 'ct63').
        n_rounds: numero di round di DES per ciascuna copia.

    Returns:
        big_circuit: Circuit contenente tutte le istanze in parallelo
        fixed_inputs: mappa wire_completo -> bool
        fixed_outputs: mappa wire_completo -> bool
    """
    big_circuit = Circuit()
    fixed_inputs: Dict[str,bool] = {}
    fixed_outputs: Dict[str,bool] = {}

    for idx, (x_map, y_map) in enumerate(pairs_xy):
        # 1) Crea un nuovo circuito DES vuoto
        base = Circuit()

        # 2) Definisci i nomi dei wire per plaintext, ciphertext e chiave
        pt_wires  = [f"pt{i}" for i in range(64)]
        ct_wires  = [f"ct{i}" for i in range(64)]
        key_wires = [f"k{i}"  for i in range(64)]

        # 3) Popola `base` con tutti i gate di DES
        #    build_des_instance modifica `base` in-place
        build_des_instance(
            base,
            pt_wires,
            ct_wires,
            key_wires,
            n_rounds,
            ""   # nessun prefix qui: lo gestiremo al passo successivo
        )

        # 4) Rinomina i wire per evitare collisioni tra istanze
        prefix = f"inst{idx}_"
        inst = clone_circuit_with_prefix(base, prefix)

        # 5) Unisci in parallelo questa istanza al circuito globale
        big_circuit = big_circuit.parallel_compose(inst)

        # 6) Raccogli i vincoli sugli input/output per questa istanza
        for w, val in x_map.items():
            fixed_inputs[prefix + w] = val
        for w, val in y_map.items():
            fixed_outputs[prefix + w] = val

    return big_circuit, fixed_inputs, fixed_outputs

# Esempio di demo rapido
# if __name__ == '__main__':
#     example_pairs = [
#         ({'pt0': True,  'pt1': False}, {'ct0': False, 'ct1': True}),
#         ({'pt0': False, 'pt1': True},  {'ct0': True,  'ct1': False}),
#     ]
#     circ, inp, outp = build_multi_des(example_pairs, n_rounds=3)
#     print(f"Circuit multi‑DES con {len(circ.gates)} gate totali")
#     print("Fixed inputs:", inp)
#     print("Fixed outputs:", outp)

# def demo_multi_des_sat():
    # # Le stesse coppie che ho usato
    # example_pairs = [
    #     ({'pt0': True,  'pt1': False}, {'ct0': False, 'ct1': True}),
    #     ({'pt0': False, 'pt1': True},  {'ct0': True,  'ct1': False}),
    # ]
    # # Costruisci circuito + vincoli
    # circ, fixed_in, fixed_out = build_multi_des(example_pairs, n_rounds=3)
    # # Verifica SAT
    # sat, model = is_satisfiable(circ, fixed_in, fixed_out)
    # print(f"Multi‑DES a 3 round è SAT? {sat}")
    # if sat:
    #     print(f"Modello trovato (prime variabili): {model[:10]}…")

def demo_multi_des_sat():
    # 1) Scegli una chiave e due plaintext
    key = 0x0123456789ABCDEF
    pt0, pt1 = 0x0000000000000000, 0xFFFFFFFFFFFFFFFF

    # 2) Cifra con DES a 3 round
    ct0 = des_encrypt_block(pt0, key, n_rounds=3)
    ct1 = des_encrypt_block(pt1, key, n_rounds=3)

    # 3) Costruisci le mappe bit → wire per plaintext/ciphertext
    x_map0 = { f"pt{i}": bool(pt0 & (1 << (63 - i))) for i in range(64) }
    y_map0 = { f"ct{i}": bool(ct0 & (1 << (63 - i))) for i in range(64) }
    x_map1 = { f"pt{i}": bool(pt1 & (1 << (63 - i))) for i in range(64) }
    y_map1 = { f"ct{i}": bool(ct1 & (1 << (63 - i))) for i in range(64) }

    example_pairs = [
        (x_map0, y_map0),
        (x_map1, y_map1),
    ]

    # 4) Costruisci il multi‑DES e invoca il solver
    circ, fixed_inputs, fixed_outputs = build_multi_des(example_pairs, n_rounds=3)
    sat, model = is_satisfiable(circ, fixed_inputs, fixed_outputs)

    # 5) Stampa il risultato
    print("Multi‑DES a 3 round è SAT?", sat)
    if sat:
        print("Modello (prime 10 variabili):", model[:10])
    else:
        print("Nessun assegnamento coerente trovato.")

if __name__ == "__main__":
    demo_multi_des_sat()
