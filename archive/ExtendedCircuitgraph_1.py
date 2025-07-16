import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3
from concurrent.futures import ThreadPoolExecutor, as_completed

__all__ = [
    "create_simple_circuit",
    "manual_tseitin_cnf",
    "simulate_circuit",
    "print_cnf_formula",
    "solve_cnf",
    "simulate_multiple_circuits_parallel",
]

def create_simple_circuit():
    """
    Crea un semplice circuito digitale (sommatore a 1 bit) con circuitgraph.

    Ingressi:
      - 'a', 'b': bit da sommare
      - 'cin': riporto in ingresso

    Uscite:
      - 'sum': somma
      - 'carry': riporto in uscita
    """
    circuit = cg.Circuit()
    circuit.add('a', 'input')
    circuit.add('b', 'input')
    circuit.add('cin', 'input')
    circuit.add('s1', 'xor', fanin=['a', 'b'])
    circuit.add('s2', 'xor', fanin=['s1', 'cin'])
    circuit.add('c1', 'and', fanin=['a', 'b'])
    circuit.add('c2', 'and', fanin=['s1', 'cin'])
    circuit.add('cout', 'or', fanin=['c1', 'c2'])
    circuit.add('sum', 'buf', fanin=['s2'])
    circuit.add('carry', 'buf', fanin=['cout'])
    circuit.outputs = ['sum', 'carry']
    return circuit


def manual_tseitin_cnf(circuit):
    """
    Converte un circuito circuitgraph in una formula CNF con codifica Tseitin.

    Restituisce:
      - formula: oggetto CNF di pysat.formula
      - var_map: dizionario nodo -> id variabile CNF
    """
    clauses = []
    nodes = list(circuit.nodes())
    var_map = {node: i + 1 for i, node in enumerate(nodes)}

    for node in nodes:
        node_type = circuit.type(node)
        inputs = list(circuit.fanin(node))

        # Skip inputs and constants
        if node_type == 'input' or node_type.startswith('const'):
            continue

        out_var = var_map[node]
        in_vars = [var_map[inp] for inp in inputs]

        if node_type == 'buf':
            i = in_vars[0]
            clauses += [[-i, out_var], [i, -out_var]]
        elif node_type == 'not':
            i = in_vars[0]
            clauses += [[i, out_var], [-i, -out_var]]
        elif node_type == 'and':
            for i in in_vars:
                clauses.append([-out_var, i])
            clauses.append([-v for v in in_vars] + [out_var])
        elif node_type == 'or':
            clauses.append([-out_var] + in_vars)
            for i in in_vars:
                clauses.append([-i, out_var])
        elif node_type == 'nand':
            for i in in_vars:
                clauses.append([i, out_var])
            clauses.append([-v for v in in_vars] + [-out_var])
        elif node_type == 'nor':
            for i in in_vars:
                clauses.append([-i, -out_var])
            clauses.append(in_vars + [out_var])
        elif node_type == 'xor':
            if len(in_vars) != 2:
                raise ValueError("XOR a due ingressi richiesto")
            a, b = in_vars
            clauses += [[-a, -b, -out_var], [a, b, -out_var], [-a, b, out_var], [a, -b, out_var]]
        elif node_type == 'xnor':
            if len(in_vars) != 2:
                raise ValueError("XNOR a due ingressi richiesto")
            a, b = in_vars
            clauses += [[-a, b, out_var], [a, -b, out_var], [-a, -b, -out_var], [a, b, -out_var]]
        else:
            raise ValueError(f"Porta {node_type} non supportata")

    formula = CNF()
    for c in clauses:
        formula.append(c)
    return formula, var_map


def simulate_circuit(circuit, input_values):
    """
    Simula un circuito dato un dizionario di ingressi booleani (0/1 o False/True).
    Restituisce un dizionario nodo->valore booleano.
    """
    # Convert input_values to bool
    node_values = {n: bool(v) for n, v in input_values.items()}

    # Default constants and inputs
    for node in circuit.nodes():
        if node not in node_values:
            t = circuit.type(node)
            if t == 'input':
                node_values[node] = False
            elif t == 'const0':
                node_values[node] = False
            elif t == 'const1':
                node_values[node] = True

    # Evaluate in topological order
    for node in circuit.topo_sort():
        if node in node_values and circuit.type(node) == 'input':
            continue
        if node not in node_values:
            in_vals = [node_values[i] for i in circuit.fanin(node)]
            t = circuit.type(node)
            if t == 'and':
                node_values[node] = all(in_vals)
            elif t == 'or':
                node_values[node] = any(in_vals)
            elif t == 'not':
                node_values[node] = not in_vals[0]
            elif t == 'xor':
                node_values[node] = sum(in_vals) % 2 == 1
            elif t == 'nand':
                node_values[node] = not all(in_vals)
            elif t == 'nor':
                node_values[node] = not any(in_vals)
            elif t == 'xnor':
                node_values[node] = sum(in_vals) % 2 == 0
            elif t == 'buf':
                node_values[node] = in_vals[0]
            else:
                raise ValueError(f"Porta {t} non supportata in simulazione")

    return node_values


def print_cnf_formula(formula):
    """
    Stampa in formato DIMACS la formula CNF di pysat.
    """
    print(f"p cnf {formula.nv} {len(formula.clauses)}")
    for clause in formula.clauses:
        print(" ".join(map(str, clause)) + " 0")


def solve_cnf(formula, circuit=None, var_map=None):
    """
    Risolve la formula CNF con Glucose3. Se saturo, restituisce il modello.
    Se forniti circuit e var_map, estrae input/output simulati.
    """
    solver = Glucose3()
    for c in formula.clauses:
        solver.add_clause(c)
    sat = solver.solve()
    model = solver.get_model() if sat else None
    if circuit and var_map and sat:
        inv = {v: k for k, v in var_map.items()}
        inputs = {i: int(var_map[i] in model) for i in circuit.inputs()}
        outputs = simulate_circuit(circuit, inputs)
        return {'sat': True, 'model': model, 'inputs': inputs, 'outputs': outputs}
    return {'sat': sat, 'model': model}


def simulate_multiple_circuits_parallel(circuits, input_values_list):
    """
    Simula più circuiti in parallelo. Ritorna lista di dizionari di valori nodo->bool.
    """
    results = [None] * len(circuits)
    with ThreadPoolExecutor() as executor:
        future_map = {executor.submit(simulate_circuit, c, vals): idx
                      for idx, (c, vals) in enumerate(zip(circuits, input_values_list))}
        for fut in as_completed(future_map):
            results[future_map[fut]] = fut.result()
    return results


# if __name__ == "__main__":
#     # Esempio: creazione e simulazione del sommatore a 1 bit
#     circ = create_simple_circuit()
#     print("Circuito creato:", circ)
#     # Manuale CNF + risoluzione
#     cnf, vm = manual_tseitin_cnf(circ)
#     print_cnf_formula(cnf)
#     res = solve_cnf(cnf, circ, vm)
#     print("Risultato CNF:", res)
#     # Simulazione parallela di 3 copie del circuito
#     circuits = [create_simple_circuit() for _ in range(3)]
#     inputs = [{'a':1,'b':0,'cin':1}, {'a':0,'b':1,'cin':1}, {'a':1,'b':1,'cin':1}]
#     parallel = simulate_multiple_circuits_parallel(circuits, inputs)
#     print("Simulazioni parallele:", parallel)
