import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_simple_circuit():
    """
    Crea un semplice circuito (sommatore a 1 bit) con circuitgraph.
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
    clauses = []
    nodes = list(circuit.nodes())
    var_map = {node: i+1 for i, node in enumerate(nodes)}
    
    for node in nodes:
        node_type = circuit.type(node)
        inputs = list(circuit.fanin(node))
        if node_type == 'input':
            continue
        elif node_type == 'buf':
            in_var = var_map[inputs[0]]
            out_var = var_map[node]
            clauses.append([-in_var, out_var])
            clauses.append([in_var, -out_var])
        elif node_type == 'and':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            for in_var in in_vars:
                clauses.append([-out_var, in_var])
            clauses.append([-v for v in in_vars] + [out_var])
        elif node_type == 'or':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            clauses.append([-out_var] + in_vars)
            for in_var in in_vars:
                clauses.append([-in_var, out_var])
        elif node_type == 'xor':
            out_var = var_map[node]
            if len(inputs) == 2:
                a_var, b_var = var_map[inputs[0]], var_map[inputs[1]]
                clauses.append([-a_var, -b_var, -out_var])
                clauses.append([a_var, b_var, -out_var])
                clauses.append([-a_var, b_var, out_var])
                clauses.append([a_var, -b_var, out_var])
    
    formula = CNF()
    for clause in clauses:
        formula.append(clause)
    
    return formula, var_map

def simulate_circuit(circuit, input_values):
    """
    Simula un circuito con input specificati e restituisce un dizionario con i valori dei nodi.
    """
    node_values = input_values.copy()  # Inizializza con gli input forniti
    
    # Aggiunge valori predefiniti per i nodi mancanti
    for node in circuit.nodes():
        if node not in node_values:
            if circuit.type(node) == 'input':
                node_values[node] = False
            elif circuit.type(node) == 'const0':
                node_values[node] = False
            elif circuit.type(node) == 'const1':
                node_values[node] = True
    
    # Valuta i nodi in ordine topologico
    for node in circuit.topo_sort():
        if node in node_values:
            continue
        
        missing_inputs = False
        for in_node in circuit.fanin(node):
            if in_node not in node_values:
                print(f"Errore: nodo {in_node} necessario per {node} non è stato valutato")
                missing_inputs = True
        if missing_inputs:
            continue
        
        in_values = [node_values[in_node] for in_node in circuit.fanin(node)]
        gate_type = circuit.type(node)
        
        if gate_type == 'and':
            node_values[node] = all(in_values)
        elif gate_type == 'or':
            node_values[node] = any(in_values)
        elif gate_type == 'not':
            node_values[node] = not in_values[0]
        elif gate_type == 'xor':
            node_values[node] = sum(in_values) % 2 == 1
        elif gate_type == 'nand':
            node_values[node] = not all(in_values)
        elif gate_type == 'nor':
            node_values[node] = not any(in_values)
        elif gate_type == 'xnor':
            node_values[node] = sum(in_values) % 2 == 0
        elif gate_type == 'buf':
            node_values[node] = in_values[0]
        elif circuit.type(node) == 'const0':
            node_values[node] = False
        elif circuit.type(node) == 'const1':
            node_values[node] = True
        else:
            raise ValueError(f"Tipo di porta {gate_type} non supportato")
    
    for node in circuit.nodes():
        if node not in node_values:
            print(f"Avviso: il nodo {node} non è stato valutato")
    
    return node_values

def print_cnf_formula(formula):
    print(f"p cnf {formula.nv} {len(formula.clauses)}")
    for clause in formula.clauses:
        print(" ".join(map(str, clause)) + " 0")

def solve_cnf(formula, circuit, var_map):
    solver = Glucose3()
    for clause in formula.clauses:
        solver.add_clause(clause)
    sat = solver.solve()
    if sat:
        print("Formula soddisfacibile!")
        model = solver.get_model()
        inv_var_map = {v: k for k, v in var_map.items()}
        inputs = {inp: (1 if var_map[inp] in model else 0) for inp in circuit.inputs()}
        print("Input:", inputs)
        outputs = simulate_circuit(circuit, inputs)
        print("Output simulato:", outputs)
    else:
        print("Formula insoddisfacibile.")
    solver.delete()

def simulate_multiple_circuits_parallel(circuits, input_values_list):
    """
    Simula una lista di circuiti in parallelo.
    
    Parametri:
      - circuits: lista di oggetti Circuit.
      - input_values_list: lista di dizionari, ciascuno contenente i valori di input per il corrispondente circuito.
    
    Restituisce:
      - Una lista dei dizionari di output ottenuti dalla simulazione di ciascun circuito.
    """
    results = [None] * len(circuits)
    with ThreadPoolExecutor() as executor:
        # Mappa ogni simulazione a un indice della lista
        future_to_index = {
            executor.submit(simulate_circuit, circuit, input_values): idx
            for idx, (circuit, input_values) in enumerate(zip(circuits, input_values_list))
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            results[idx] = future.result()
    return results

# Esempio di utilizzo

# if __name__ == "__main__":
#     # Esempio 1: simulazione semplice di un circuito (sommatore a 1 bit)
#     simple_circuit = create_simple_circuit()
#     print("Simulazione semplice del circuito (sommatore a 1 bit):")
#     test_inputs = {'a': 1, 'b': 1, 'cin': 0}
#     result = simulate_circuit(simple_circuit, test_inputs)
#     print("Output:", result)
    
#     # Esempio 2: simulazione in parallelo di più circuiti
#     circuits = [create_simple_circuit() for _ in range(3)]
#     inputs_list = [
#         {'a': 1, 'b': 0, 'cin': 1},
#         {'a': 0, 'b': 1, 'cin': 1},
#         {'a': 1, 'b': 1, 'cin': 1}
#     ]
#     parallel_results = simulate_multiple_circuits_parallel(circuits, inputs_list)
#     print("\nSimulazione parallela di più circuiti:")
#     for idx, res in enumerate(parallel_results):
#         print(f"Circuito {idx+1}: {res}")