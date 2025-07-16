# multi_des.py
"""
Costruzione di un circuito composto da più istanze di DES
sulla base della libreria Circuit.
"""
from typing import List, Tuple, Dict
from new_ExtendedCircuitgraph import Circuit
# Importa il tuo builder DES, che restituisce una Circuit per un DES a n_rounds
from des_circuit import build_des_circuit


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
        pairs_xy: lista di tuple (input_map, output_map) per ogni istanza,
                  dove input_map e output_map mappano wire DES base -> valore booleano.
        n_rounds: numero di round di DES per ogni istanza.
    Returns:
        big_circuit: Circuit unito in parallelo con prefissi per ogni istanza
        fixed_inputs: dizionario wire_fullname -> bool
        fixed_outputs: dizionario wire_fullname -> bool
    """
    big = Circuit()
    fixed_inputs: Dict[str, bool] = {}
    fixed_outputs: Dict[str, bool] = {}

    for i, (x_map, y_map) in enumerate(pairs_xy):
        # Costruisci il circuito DES base
        base = build_des_circuit(n_rounds)
        # Prefisso univoco per questa istanza
        prefix = f"inst{i}_"
        inst = clone_circuit_with_prefix(base, prefix)
        # Componi in parallelo
        big = big.parallel_compose(inst)
        # Aggiungi vincoli fissati
        for w, val in x_map.items():
            fixed_inputs[prefix + w] = val
        for w, val in y_map.items():
            fixed_outputs[prefix + w] = val

    return big, fixed_inputs, fixed_outputs


# Esempio rapido se eseguito come script
if __name__ == '__main__':
    # due coppie di esempio (usa wire nome base come definito in build_des_circuit)
    example_pairs = [({'pt0': True, 'pt1': False}, {'ct0': False, 'ct1': True}),
                     ({'pt0': False, 'pt1': True}, {'ct0': True, 'ct1': False})]
    circ, inp, out = build_multi_des(example_pairs, n_rounds=3)
    print(f"Circuit multi-DES: {len(circ.gates)} gate totali")
    print("Fixed inputs:", inp)
    print("Fixed outputs:", out)
