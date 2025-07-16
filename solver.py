# solver.py
"""
Wrapper per risolvere un problema SAT generato da un oggetto Circuit.
Il backend (ad es. pycosat) è configurabile tramite la variabile globale SOLVER.
"""
from typing import Dict, List, Optional, Tuple
import pycosat
from new_circuit_to_cnf import circuit_to_cnf
from new_ExtendedCircuitgraph import Circuit

# Backend SAT: a chiunque voglia cambiare solver, basta riassegnare questa variabile
# Il solver deve esportare una funzione "solve(clauses: List[List[int]]) -> List[int] | str"
SOLVER = pycosat


def set_solver(solver_module) -> None:
    """
    Permette di cambiare il modulo di risoluzione SAT.
    Il modulo deve fornire una funzione `solve(clauses)`.
    """
    global SOLVER
    SOLVER = solver_module


def is_satisfiable(
    circuit: Circuit,
    fixed_inputs: Optional[Dict[str, bool]] = None,
    fixed_outputs: Optional[Dict[str, bool]] = None
) -> Tuple[bool, Optional[List[int]]]:
    """
    Determina se c'è un assegnamento degli input non fissati che renda vera la logica del circuito.

    Args:
        circuit: istanza di Circuit
        fixed_inputs: mappa wire->bool per fissare alcuni input
        fixed_outputs: mappa wire->bool per fissare alcuni output
    Returns:
        (is_sat, model)
        - is_sat: True se il CNF è sat, False se unsat
        - model: lista di interi con assegnamenti (variabili positive=vero,
          negative=falso) se is_sat=True, altrimenti None
    """
    # 1) Genera CNF: num_vars, clausole
    num_vars, clauses = circuit_to_cnf(circuit, fixed_inputs, fixed_outputs)

    # 2) Chiama il solver
    result = SOLVER.solve(clauses)

    # 3) Interpreta il risultato
    if isinstance(result, str) and result.upper().startswith('UNSAT'):
        return False, None
    if isinstance(result, list):
        return True, result
    # Alcuni solver ritornano liste vuote per UNSAT, gestiamo genericamente:
    return bool(result), result if result else None
