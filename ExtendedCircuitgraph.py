import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3

def create_simple_circuit():
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
            clauses.append([-var for var in in_vars] + [out_var])
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
    Simula un circuito con input specificati e restituisce tutti i valori dei nodi.
    
    Args:
        circuit: Circuito cg da simulare
        input_values: Dizionario con valori per i nodi di input
        
    Returns:
        Dizionario con valori booleani per tutti i nodi
    """
    node_values = input_values.copy()  # Inizializza con i valori di input forniti
    
    # Aggiungi valori predefiniti per tutti i nodi mancanti
    for node in circuit.nodes():
        if node not in node_values:
            # Inizializza gli input mancanti a False
            if circuit.type(node) == 'input':
                node_values[node] = False
            # Inizializza i nodi const0/const1 ai loro valori
            elif circuit.type(node) == 'const0':
                node_values[node] = False
            elif circuit.type(node) == 'const1':
                node_values[node] = True
    
    # Usa l'ordine topologico per valutare i nodi in sequenza
    for node in circuit.topo_sort():
        # Salta i nodi già valutati (input e costanti)
        if node in node_values:
            continue
        
        # Verifica se tutti i nodi di input sono presenti
        missing_inputs = False
        for in_node in circuit.fanin(node):
            if in_node not in node_values:
                print(f"Errore: nodo {in_node} necessario per {node} non è stato valutato")
                missing_inputs = True
        
        if missing_inputs:
            continue
        
        # Ottieni i valori degli input
        in_values = [node_values[in_node] for in_node in circuit.fanin(node)]
        
        # Valuta il nodo in base al suo tipo
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
        else:
            raise ValueError(f"Tipo di porta {gate_type} non supportato")
    
    # Verifica che tutti i nodi siano stati valutati
    for node in circuit.nodes():
        if node not in node_values:
            print(f"Avviso: il nodo {node} non è stato valutato")
    
    return node_values

def simulate_circuit_vecchia(circuit, inputs):
    node_values = inputs.copy()
    topo_order = []
    visited = set()
    
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for in_node in circuit.fanin(node):
            dfs(in_node)
        topo_order.append(node)
    
    for node in circuit.nodes():
        dfs(node)
    
    for node in topo_order:
        if circuit.type(node) == 'input':
            continue
        in_values = [node_values[in_node] for in_node in circuit.fanin(node)]
        if circuit.type(node) == 'buf':
            node_values[node] = in_values[0]
        elif circuit.type(node) == 'and':
            node_values[node] = all(in_values)
        elif circuit.type(node) == 'or':
            node_values[node] = any(in_values)
        elif circuit.type(node) == 'xor':
            node_values[node] = sum(in_values) % 2 == 1
    
    return {out: int(node_values[out]) for out in circuit.outputs}

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