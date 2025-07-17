# circuit_to_cnf.py
"""
Moduli per convertire un Circuit in CNF.
"""
from typing import List, Tuple, Dict, Optional
from new_ExtendedCircuitgraph import Circuit  # Assicurati che il modulo sia nel PYTHONPATH


def index_wires(circuit: Circuit) -> Dict[str, int]:
    """
    Mappa ogni wire name a un indice intero 1-based.
    """
    wires = set()
    for gate in circuit.gates:
        wires.update(gate.inputs)
        wires.add(gate.output)
    sorted_wires = sorted(wires)
    return {w: i+1 for i, w in enumerate(sorted_wires)}


def cnf_and(inputs: List[int], output: int) -> List[List[int]]:
    """
    Clausole CNF per gate AND n-ario: y = AND(inputs)
    """
    clauses: List[List[int]] = []
    # (¬x_i ∨ y)
    for xi in inputs:
        clauses.append([-xi, output])
    # (¬y ∨ x_1) ∧ ... ∧ (¬y ∨ x_n)
    for xi in inputs:
        clauses.append([-output, xi])
    return clauses


def cnf_or(inputs: List[int], output: int) -> List[List[int]]:
    """
    Clausole CNF per gate OR n-ario: y = OR(inputs)
    """
    clauses: List[List[int]] = []
    # (x1 ∨ x2 ∨ ... ∨ ¬y)
    clauses.append(inputs + [-output])
    # (y ∨ ¬x_i) per i
    for xi in inputs:
        clauses.append([output, -xi])
    return clauses


def cnf_xor(a: int, b: int, y: int) -> List[List[int]]:
    """
    Clausole CNF per gate XOR binario: y = a ⊕ b
    """
    return [
        [-a, -b, -y],
        [ a,  b, -y],
        [-a,  b,  y],
        [ a, -b,  y],
    ]

def cnf_not(x: int, y: int) -> List[List[int]]:
    """
    Clausole CNF per gate NOT unario: y = ¬x
    Equivalenza y ↔ ¬x diventa (y ∨ x) ∧ (¬y ∨ ¬x).
    """
    return [
        [ y,  x],
        [-y, -x],
    ]

def cnf_xnor(a: int, b: int, y: int) -> List[List[int]]:
    """
    Clausole CNF per XNOR: y = ¬(a ⊕ b)  (y = 1 se a == b)
    (¬a ∨ b ∨ ¬y)  ∧  (a ∨ ¬b ∨ ¬y)
    ∧ (y ∨ a ∨ b)  ∧  (y ∨ ¬a ∨ ¬b)
    """
    return [
        [-a,  b, -y],
        [ a, -b, -y],
        [ y,  a,  b],
        [ y, -a, -b],
    ]


def cnf_buf(x: int, y: int) -> List[List[int]]:
    """
    Clausole CNF per buffer: y = x (usato per permutazioni)
    """
    return [[-x, y], [-y, x]]


def add_unit_clauses(
    clauses: List[List[int]],
    fixed: Dict[str, bool],
    wire2idx: Dict[str, int]
) -> None:
    """
    Aggiunge clausole unitarie per fissare valori di alcuni wire.
    """
    for wire, val in fixed.items():
        idx = wire2idx.get(wire)
        if idx is None:
            raise KeyError(f"Wire {wire} non trovato nella mappatura")
        clauses.append([idx if val else -idx])


def circuit_to_cnf(
    circuit: Circuit,
    fixed_inputs: Optional[Dict[str, bool]] = None,
    fixed_outputs: Optional[Dict[str, bool]] = None
) -> Tuple[int, List[List[int]]]:
    """
    Genera CNF (num_vars, clausole) da un Circuit.

    Args:
        circuit: istanza di Circuit da convertire
        fixed_inputs: dizionario wire->bool per fissare input
        fixed_outputs: dizionario wire->bool per fissare output
    Returns:
        num_vars: numero totale di variabili
        clauses: lista di clausole CNF (liste di int)
    """
    wire2idx = index_wires(circuit)
    clauses: List[List[int]] = []

    # Traduci ogni gate
    for gate in circuit.gates:
        out_idx = wire2idx[gate.output]
        in_idxs = [wire2idx[w] for w in gate.inputs]

        if gate.gate_type == 'AND':
            clauses.extend(cnf_and(in_idxs, out_idx))
        elif gate.gate_type == 'OR':
            clauses.extend(cnf_or(in_idxs, out_idx))
        elif gate.gate_type == 'XOR':
            if len(in_idxs) != 2:
                raise ValueError("XOR supporta solo 2 ingressi")
            clauses.extend(cnf_xor(in_idxs[0], in_idxs[1], out_idx))
        elif gate.gate_type == 'BUF':
            if len(in_idxs) != 1:
                raise ValueError("BUF supporta solo 1 ingresso")
            clauses.extend(cnf_buf(in_idxs[0], out_idx))
        elif gate.gate_type == 'NOT':
            # NOT supporta esattamente 1 ingresso
            if len(in_idxs) != 1:
                raise ValueError("NOT supporta solo 1 ingresso")
            clauses.extend(cnf_not(in_idxs[0], out_idx))
        elif gate.gate_type == 'XNOR':
            # XNOR binario, un solo ingresso
            if len(in_idxs) != 2:
                raise ValueError("XNOR supporta solo 2 ingressi")
            clauses.extend(cnf_xnor(in_idxs[0], in_idxs[1], out_idx))
        else:
            raise ValueError(f"Gate type {gate.gate_type} non supportato")

    # Aggiungi clausole per input/output fissati
    if fixed_inputs:
        add_unit_clauses(clauses, fixed_inputs, wire2idx)
    if fixed_outputs:
        add_unit_clauses(clauses, fixed_outputs, wire2idx)

    num_vars = len(wire2idx)
    return num_vars, clauses


# Se eseguito come script, esempio di uso
if __name__ == '__main__':
    # Esempio rapido
    cir = Circuit()
    cir.add_gate('AND', ['a', 'b'], 'd')
    cir.add_gate('OR', ['d', 'c'], 'y')
    nvars, cls = circuit_to_cnf(cir)
    print(f"Variabili: {nvars}\nClausole:")
    for cl in cls:
        print(cl)
