# partial_sat_solver.py
# Utility per risolvere vincoli parziali su un circuito CircuitGraph tramite SAT

import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3
from archive.ExtendedCircuitgraph_0 import manual_tseitin_cnf, create_simple_circuit
from des_circuit import create_des_circuit


def solve_partial(circuit: cg.Circuit,
                  fixed_inputs: dict[str, bool],
                  fixed_outputs: dict[str, bool]) -> tuple[bool, list[int] | None, dict[str, int]]:
    """
    Converte un circuito in CNF via codifica Tseitin e aggiunge clausole unitarie
    per fissare alcuni ingressi (fixed_inputs) e tutte le uscite (fixed_outputs).

    Restituisce:
      - sat: True se l'istanza è soddisfacibile
      - model: lista di interi con il modello SAT (None se insoddisfacibile)
      - var_map: dizionario nodo -> id variabile CNF
    """
    # 1) Costruzione della formula CNF e mappa variabili tramite Tseitin
    cnf, var_map = manual_tseitin_cnf(circuit)

    # 2) Aggiunta clausole unitarie per i vincoli su ingressi e uscite
    for name, val in {**fixed_inputs, **fixed_outputs}.items():
        if name not in var_map:
            raise KeyError(f"Nodo '{name}' non trovato in var_map")
        lit = var_map[name] if val else -var_map[name]
        cnf.append([lit])

    # 3) Risoluzione SAT con Glucose3
    solver = Glucose3()
    for clause in cnf.clauses:
        solver.add_clause(clause)
    sat = solver.solve()
    model = solver.get_model() if sat else None
    solver.delete()

    return sat, model, var_map


if __name__ == "__main__":
    # -------------------------------------------------------------
    # Configurazione dei casi di test
    # Ogni test è un dict con:
    #   - 'name': nome descrittivo
    #   - 'circuit': oggetto Circuit
    #   - 'fixed_inputs': dizionario input fissi
    #   - 'fixed_outputs': dizionario output fissi
    # -------------------------------------------------------------
    tests = []

    # 1) Sommatore a 1 bit (simple adder)
    adder = create_simple_circuit()
    tests.append({
        'name': 'Adder 1-bit: sum=1, carry=0 con a=1, cin=0',
        'circuit': adder,
        'fixed_inputs':  {'a': True,  'cin': False},
        'fixed_outputs': {'sum': True, 'carry': False}
    })

    # 2) Sommatore a 1 bit: un caso UNSAT
    adder2 = create_simple_circuit()
    tests.append({
        'name': 'Adder 1-bit UNSAT: sum=0, carry=0 con a=1, cin=0',
        'circuit': adder2,
        'fixed_inputs':  {'a': True,  'cin': False},
        'fixed_outputs': {'sum': False,'carry': False}
    })

    # 3) DES block: verifica coerenza plaintext->ciphertext
    # Esempio a scopo dimostrativo (chiave e plaintext noti)
    plaintext = '0123456789ABCDEF'
    key       = '133457799BBCDFF1'
    des_circ, p_wires, out_wires = create_des_circuit(plaintext, key)
    # Supponiamo di voler forzare l'output ad un valore arbitrario (ad esempio uguale al plaintext)
    fixed_out_bits = {wire: False for wire in out_wires}
    tests.append({
        'name': f"DES: plaintext={plaintext}, key={key}, forziamo tutti output a 0",
        'circuit': des_circ,
        'fixed_inputs': {},
        'fixed_outputs': fixed_out_bits
    })

    # -------------------------------------------------------------
    # Esecuzione sperimentale dei test
    # -------------------------------------------------------------
    for test in tests:
        name = test['name']
        circuit = test['circuit']
        fin     = test['fixed_inputs']
        fout    = test['fixed_outputs']

        print(f"\n--- TEST: {name} ---")
        try:
            sat, model, var_map = solve_partial(circuit, fin, fout)
            if sat:
                print("SAT: esiste assegnamento compatibile.")
                # Estrazione dei rimanenti input
                remains = {inp: (var_map[inp] in model)
                            for inp in circuit.inputs()
                            if inp not in fin}
                print("Rimanenti input:", remains)
            else:
                print("UNSAT: nessuna assegnazione possibile.")
        except Exception as e:
            print(f"Errore durante il test '{name}': {e}")
