import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3

def create_simple_circuit():
    """
    Crea un semplice circuito digitale con circuitgraph.
    In questo esempio, creiamo un circuito di un sommatore a 1-bit.
    """
    # Creare un nuovo circuito
    circuit = cg.Circuit()
    
    # Aggiungere input al circuito
    circuit.add('a', 'input')
    circuit.add('b', 'input')
    circuit.add('cin', 'input')
    
    # Aggiungere gates interni
    circuit.add('s1', 'xor', fanin=['a', 'b'])
    circuit.add('s2', 'xor', fanin=['s1', 'cin'])
    circuit.add('c1', 'and', fanin=['a', 'b'])
    circuit.add('c2', 'and', fanin=['s1', 'cin'])
    circuit.add('cout', 'or', fanin=['c1', 'c2'])
    
    # Aggiungere output
    circuit.add('sum', 'buf', fanin=['s2'])
    circuit.add('carry', 'buf', fanin=['cout'])
    
    # Definire gli output
    circuit.outputs = ['sum', 'carry']
    
    return circuit

def manual_tseitin_cnf(circuit):
    """
    Implementazione manuale della conversione Tseitin del circuito in CNF.
    """
    clauses = []
    # Creare una mappa delle variabili (nodo -> variabile)
    nodes = list(circuit.nodes())
    var_map = {node: i+1 for i, node in enumerate(nodes)}
    
    # Per ogni nodo, aggiungi clausole in base al tipo
    for node in nodes:
        node_type = circuit.type(node)
        inputs = list(circuit.fanin(node))
        
        if node_type == 'input':
            # Per gli input non aggiungiamo vincoli
            continue
        
        elif node_type == 'buf':
            # buf(a) = b -> (a ↔ b) -> (a → b) ∧ (b → a) -> (¬a ∨ b) ∧ (a ∨ ¬b)
            in_var = var_map[inputs[0]]
            out_var = var_map[node]
            clauses.append([-in_var, out_var])   # ¬a ∨ b
            clauses.append([in_var, -out_var])   # a ∨ ¬b
            
        elif node_type == 'and':
            # AND(a,b) = c -> (c ↔ (a ∧ b)) -> 
            # (c → (a ∧ b)) ∧ ((a ∧ b) → c) ->
            # (¬c ∨ (a ∧ b)) ∧ (¬(a ∧ b) ∨ c) ->
            # (¬c ∨ a) ∧ (¬c ∨ b) ∧ ((¬a ∨ ¬b) ∨ c) ->
            # (¬c ∨ a) ∧ (¬c ∨ b) ∧ (¬a ∨ ¬b ∨ c)
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            
            # c → a, c → b
            for in_var in in_vars:
                clauses.append([-out_var, in_var])
                
            # a ∧ b → c
            clause = [-var for var in in_vars] + [out_var]
            clauses.append(clause)
            
        elif node_type == 'or':
            # OR(a,b) = c -> (c ↔ (a ∨ b)) ->
            # (c → (a ∨ b)) ∧ ((a ∨ b) → c) ->
            # (¬c ∨ (a ∨ b)) ∧ (¬(a ∨ b) ∨ c) ->
            # (¬c ∨ a ∨ b) ∧ (¬a → c) ∧ (¬b → c) ->
            # (¬c ∨ a ∨ b) ∧ (a ∨ c) ∧ (b ∨ c)
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            
            # c → (a ∨ b)
            clauses.append([-out_var] + [var for var in in_vars])
            
            # (a ∨ b) → c
            for in_var in in_vars:
                clauses.append([-in_var, out_var])
                
        elif node_type == 'xor':
            # XOR(a,b) = c -> (c ↔ (a⊕b)) ->
            # c ↔ ((a ∧ ¬b) ∨ (¬a ∧ b)) ->
            # Questo richiede più clausole...
            out_var = var_map[node]
            if len(inputs) == 2:
                a_var = var_map[inputs[0]]
                b_var = var_map[inputs[1]]
                
                # (a ∧ b) → ¬c
                clauses.append([-a_var, -b_var, -out_var])
                
                # (¬a ∧ ¬b) → ¬c
                clauses.append([a_var, b_var, -out_var])
                
                # (a ∧ ¬b) → c
                clauses.append([-a_var, b_var, out_var])
                
                # (¬a ∧ b) → c
                clauses.append([a_var, -b_var, out_var])
    
    # Crea la formula CNF per pysat
    formula = CNF()
    for clause in clauses:
        formula.append(clause)
        
    return formula, var_map

def simulate_circuit(circuit, inputs):
    """
    Simula il circuito con gli input dati. Implementazione manuale.
    """
    # Dizionario per memorizzare i valori di ogni nodo
    node_values = inputs.copy()
    
    # Ottieni tutti i nodi in ordine topologico
    # (assicurandoci che gli input di un nodo siano valutati prima del nodo stesso)
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
    
    # Valuta il circuito in ordine topologico
    for node in topo_order:
        # Salta gli input (che già abbiamo)
        if circuit.type(node) == 'input':
            continue
            
        # Ottieni i valori degli input di questo nodo
        in_values = [node_values[in_node] for in_node in circuit.fanin(node)]
        
        # Valuta il nodo in base al suo tipo
        if circuit.type(node) == 'buf':
            node_values[node] = in_values[0]
            
        elif circuit.type(node) == 'and':
            node_values[node] = all(in_values)
            
        elif circuit.type(node) == 'or':
            node_values[node] = any(in_values)
            
        elif circuit.type(node) == 'xor':
            # XOR è True se un numero dispari di input è True
            node_values[node] = sum(in_values) % 2 == 1
    
    # Estrai i valori di output
    output_values = {out: node_values[out] for out in circuit.outputs}
    
    # Converti i valori booleani in 0 e 1
    output_values = {k: 1 if v else 0 for k, v in output_values.items()}
    
    return output_values

def print_cnf_formula(formula):
    """
    Stampa la formula CNF in un formato leggibile.
    """
    print("Formula CNF in formato DIMACS:")
    print(f"p cnf {formula.nv} {len(formula.clauses)}")
    for clause in formula.clauses:
        clause_str = " ".join(map(str, clause)) + " 0"
        print(clause_str)

def solve_cnf(formula, circuit, var_map):
    """
    Risolve la formula CNF usando pysat e mostra i risultati.
    """
    # Creare il solver
    solver = Glucose3()
    
    # Aggiungere le clausole al solver
    for clause in formula.clauses:
        solver.add_clause(clause)
    
    # Risolvere la formula
    sat = solver.solve()
    
    if sat:
        print("La formula è soddisfacibile!")
        
        # Ottenere l'assegnamento
        model = solver.get_model()
        
        # Creare la mappa inversa per interpretare i risultati
        inv_var_map = {v: k for k, v in var_map.items()}
        
        # Mostrare i valori per tutti i nodi
        print("\nAssegnamento delle variabili:")
        for var_id in model:
            abs_var_id = abs(var_id)
            if abs_var_id in inv_var_map:
                node = inv_var_map[abs_var_id]
                value = 1 if var_id > 0 else 0
                print(f"{node}: {value}")
        
        # Estrarre i valori degli input
        inputs = {}
        for inp in circuit.inputs():
            if inp in var_map:
                var_id = var_map[inp]
                inputs[inp] = 1 if var_id in model else 0
        
        print("\nValori di input estratti:")
        print(inputs)
        
        # Simulare il circuito con questi input
        try:
            outputs = simulate_circuit(circuit, inputs)
            print("\nOutput simulato:")
            print(outputs)
        except Exception as e:
            print(f"Errore durante la simulazione: {e}")
            outputs = {}
            # Estrai manualmente i valori di output dal modello
            for out in circuit.outputs:
                if out in var_map:
                    var_id = var_map[out]
                    outputs[out] = 1 if var_id in model else 0
            print("\nOutput estratto dal modello:")
            print(outputs)
    else:
        print("La formula non è soddisfacibile.")
    
    # Liberare le risorse
    solver.delete()

def main():
    # Informazioni sulla versione
    print(f"Versione CircuitGraph: {cg.__version__ if hasattr(cg, '__version__') else 'Sconosciuta'}")
    
    # Creare il circuito
    circuit = create_simple_circuit()
    print(f"Circuito creato con {len(circuit.nodes())} nodi")
    print(f"Input: {circuit.inputs()}")
    print(f"Output: {circuit.outputs}")
    
    # Visualizzare la struttura del circuito
    print("\nStruttura del circuito:")
    for node in sorted(circuit.nodes()):
        node_type = circuit.type(node)
        fanin = circuit.fanin(node)
        print(f"{node} ({node_type}) <- {fanin}")
    
    # Convertire in CNF
    try:
        print("\nImplementando manualmente la conversione CNF...")
        cnf_formula, var_map = manual_tseitin_cnf(circuit)
        print(f"Formula CNF creata con {len(cnf_formula.clauses)} clausole")
        
        # Stampa la mappa delle variabili
        print("\nMappa delle variabili (nodo -> variabile):")
        for node, var in sorted(var_map.items()):
            print(f"{node} -> {var}")
        
        # Stampa la formula CNF
        print_cnf_formula(cnf_formula)
        
        # Risolvere la CNF
        print("\nRisoluzione della formula CNF:")
        solve_cnf(cnf_formula, circuit, var_map)
    except Exception as e:
        print(f"Errore durante la conversione in CNF: {e}")
        import traceback
        traceback.print_exc()
    
    # Esempio di verifica del circuito con input specifici
    print("\nVerifica del circuito con input specifici:")
    test_inputs = {'a': 1, 'b': 1, 'cin': 0}
    try:
        result = simulate_circuit(circuit, test_inputs)
        print(f"Per input {test_inputs}, l'output è {result}")
    except Exception as e:
        print(f"Errore durante la simulazione: {e}")

if __name__ == "__main__":
    main()