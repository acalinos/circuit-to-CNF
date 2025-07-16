import circuitgraph as cg
from pysat.formula import CNF
from pysat.solvers import Glucose3

def create_simple_circuit():
    """
    Crea un semplice circuito digitale, in questo caso un sommatore a 1 bit.
    
    Il circuito ha tre ingressi:
      - 'a' e 'b': i bit da sommare,
      - 'cin': il riporto in ingresso.
      
    Il circuito calcola:
      - 'sum' (la somma),
      - 'carry' (il riporto in uscita).
      
    La logica interna è la seguente:
      - s1 = a XOR b
      - s2 = s1 XOR cin
      - c1 = a AND b
      - c2 = s1 AND cin
      - cout = c1 OR c2
      - sum = s2 (passato attraverso un buffer)
      - carry = cout (passato attraverso un buffer)
      
    Restituisce l'oggetto circuito.
    """
    circuit = cg.Circuit()
    
    # Aggiunta degli ingressi
    circuit.add('a', 'input')
    circuit.add('b', 'input')
    circuit.add('cin', 'input')
    
    # Costruzione dei gate logici interni
    circuit.add('s1', 'xor', fanin=['a', 'b'])
    circuit.add('s2', 'xor', fanin=['s1', 'cin'])
    circuit.add('c1', 'and', fanin=['a', 'b'])
    circuit.add('c2', 'and', fanin=['s1', 'cin'])
    circuit.add('cout', 'or', fanin=['c1', 'c2'])
    
    # Uscite: i buffer servono a "passare" il segnale in output
    circuit.add('sum', 'buf', fanin=['s2'])
    circuit.add('carry', 'buf', fanin=['cout'])
    
    # Specifica degli output del circuito
    circuit.outputs = ['sum', 'carry']
    
    return circuit


def manual_tseitin_cnf(circuit):
    """
    Converte il circuito in una formula CNF usando la codifica Tseitin.
    
    Per ogni nodo (eccetto input e costanti) vengono aggiunte le clausole che 
    rappresentano l'equivalenza logica tra l'uscita del nodo e la funzione applicata ai suoi ingressi.
    
    I gate supportati sono:
      - 'buf': equivale a un passaggio diretto (out <-> in)
      - 'not': negazione (out <-> ¬in)
      - 'and': AND (out <-> (ingressi ANDed))
      - 'or': OR (out <-> (ingressi ORed))
      - 'nand': NAND
      - 'nor': NOR
      - 'xor': XOR (solo con 2 ingressi)
      - 'xnor': XNOR (solo con 2 ingressi)
    
    Restituisce una coppia (formula, var_map) dove:
      - formula: oggetto CNF (pysat.formula.CNF) con tutte le clausole.
      - var_map: dizionario che associa ad ogni nodo un intero (la variabile)
    """
    clauses = []
    # Otteniamo la lista dei nodi e creiamo una mappa (nodo -> numero variabile)
    nodes = list(circuit.nodes())
    var_map = {node: i+1 for i, node in enumerate(nodes)}
    
    for node in nodes:
        node_type = circuit.type(node)
        inputs = list(circuit.fanin(node))
        
        # Saltiamo gli input e i nodi costanti
        if node_type == 'input' or node_type.startswith('const'):
            continue
        
        # Caso 'buf': il nodo è uguale al suo ingresso
        elif node_type == 'buf':
            in_var = var_map[inputs[0]]
            out_var = var_map[node]
            # Impostiamo l'equivalenza logica: (¬in ∨ out) ∧ (in ∨ ¬out)
            clauses.append([-in_var, out_var])
            clauses.append([in_var, -out_var])
        
        # Caso 'not': negazione
        elif node_type == 'not':
            in_var = var_map[inputs[0]]
            out_var = var_map[node]
            # out <-> ¬in  <=> (in ∨ out) ∧ (¬in ∨ ¬out)
            clauses.append([in_var, out_var])
            clauses.append([-in_var, -out_var])
        
        # Caso 'and': operazione AND
        elif node_type == 'and':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            # Se out è vero allora ogni ingresso deve esserlo
            for in_var in in_vars:
                clauses.append([-out_var, in_var])
            # Se tutti gli ingressi sono veri allora out è vero
            clauses.append([-v for v in in_vars] + [out_var])
        
        # Caso 'or': operazione OR
        elif node_type == 'or':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            # Se out è falso allora almeno un ingresso deve esserlo
            clauses.append([-out_var] + in_vars)
            # Per ogni ingresso, se quell'ingresso è vero allora out deve esserlo
            for in_var in in_vars:
                clauses.append([-in_var, out_var])
        
        # Caso 'nand': NAND (negazione dell'AND)
        elif node_type == 'nand':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            # Se almeno un ingresso è falso, out deve essere vero
            for in_var in in_vars:
                clauses.append([in_var, out_var])
            # Se tutti gli ingressi sono veri, out deve essere falso
            clauses.append([-v for v in in_vars] + [-out_var])
        
        # Caso 'nor': NOR (negazione dell'OR)
        elif node_type == 'nor':
            out_var = var_map[node]
            in_vars = [var_map[inp] for inp in inputs]
            # Se un ingresso è vero, out deve essere falso
            for in_var in in_vars:
                clauses.append([-in_var, -out_var])
            # Se tutti gli ingressi sono falsi, out deve essere vero
            clauses.append(in_vars + [out_var])
        
        # Caso 'xor': XOR per 2 ingressi
        elif node_type == 'xor':
            out_var = var_map[node]
            if len(inputs) != 2:
                raise ValueError("XOR gate con numero di ingressi diverso da 2 non supportato")
            a_var, b_var = var_map[inputs[0]], var_map[inputs[1]]
            # Le clausole per l'equivalenza: out è vero se e solo se a e b sono differenti.
            clauses.append([-a_var, -b_var, -out_var])
            clauses.append([a_var, b_var, -out_var])
            clauses.append([-a_var, b_var, out_var])
            clauses.append([a_var, -b_var, out_var])
        
        # Caso 'xnor': XNOR per 2 ingressi
        elif node_type == 'xnor':
            out_var = var_map[node]
            if len(inputs) != 2:
                raise ValueError("XNOR gate con numero di ingressi diverso da 2 non supportato")
            a_var, b_var = var_map[inputs[0]], var_map[inputs[1]]
            # out è vero se e solo se a e b sono uguali
            clauses.append([-a_var, b_var, out_var])
            clauses.append([a_var, -b_var, out_var])
            clauses.append([-a_var, -b_var, -out_var])
            clauses.append([a_var, b_var, -out_var])
        
        else:
            raise ValueError(f"Tipo di porta '{node_type}' non supportato per la conversione in CNF")
    
    # Costruiamo la formula CNF per pysat
    formula = CNF()
    for clause in clauses:
        formula.append(clause)
    
    return formula, var_map


def simulate_circuit(circuit, inputs):
    """
    Simula manualmente il circuito logico dato un dizionario di input.
    
    La funzione utilizza una visita in ordine topologico (DFS) per valutare ogni nodo 
    solo dopo che tutti i suoi ingressi sono stati valutati.
    
    Parametri:
      - circuit: oggetto Circuit di circuitgraph
      - inputs: dizionario {nodo: valore booleano} contenente i valori degli input
      
    Restituisce:
      - output_values: dizionario {nome_output: 0 o 1} contenente i valori di output del circuito.
    """
    # Inizializza i valori dei nodi con gli input forniti
    node_values = inputs.copy()
    
    # Calcola l'ordine topologico dei nodi con DFS
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
    
    # Valutazione dei nodi secondo l'ordine topologico
    for node in topo_order:
        # Salta gli input, già impostati
        if circuit.type(node) == 'input':
            continue
        
        # Ottieni i valori degli ingressi del nodo
        in_values = [node_values[in_node] for in_node in circuit.fanin(node)]
        
        # Valuta il nodo in base al tipo (supporta buf, and, or, xor)
        if circuit.type(node) == 'buf':
            node_values[node] = in_values[0]
        elif circuit.type(node) == 'and':
            node_values[node] = all(in_values)
        elif circuit.type(node) == 'or':
            node_values[node] = any(in_values)
        elif circuit.type(node) == 'xor':
            # XOR: True se il numero di ingressi True è dispari
            node_values[node] = (sum(in_values) % 2 == 1)
        # Altri tipi di gate possono essere aggiunti qui se necessario
    
    # Estrae i valori degli output del circuito
    output_values = {out: node_values[out] for out in circuit.outputs}
    # Converte i valori booleani in 0 o 1
    output_values = {k: 1 if v else 0 for k, v in output_values.items()}
    
    return output_values


def print_cnf_formula(formula):
    """
    Stampa la formula CNF nel formato DIMACS.
    """
    print("Formula CNF in formato DIMACS:")
    print(f"p cnf {formula.nv} {len(formula.clauses)}")
    for clause in formula.clauses:
        clause_str = " ".join(map(str, clause)) + " 0"
        print(clause_str)


def solve_cnf(formula, circuit, var_map):
    """
    Risolve la formula CNF usando il solver Glucose3 di pysat.
    
    Dopo la risoluzione, stampa l'assegnamento delle variabili, 
    estrae i valori di input e simula il circuito per verificare l'output.
    """
    solver = Glucose3()
    
    # Aggiunge tutte le clausole al solver
    for clause in formula.clauses:
        solver.add_clause(clause)
    
    # Risolve la formula CNF
    sat = solver.solve()
    
    if sat:
        print("La formula è soddisfacibile!")
        model = solver.get_model()
        
        # Crea una mappa inversa: variabile -> nodo
        inv_var_map = {v: k for k, v in var_map.items()}
        
        # Stampa l'assegnamento per ogni nodo
        print("\nAssegnamento delle variabili:")
        for var_id in model:
            abs_var_id = abs(var_id)
            if abs_var_id in inv_var_map:
                node = inv_var_map[abs_var_id]
                value = 1 if var_id > 0 else 0
                print(f"{node}: {value}")
        
        # Estrae i valori di input dal circuito
        inputs = {}
        for inp in circuit.inputs():
            if inp in var_map:
                var_id = var_map[inp]
                inputs[inp] = 1 if var_id in model else 0
        
        print("\nValori di input estratti:")
        print(inputs)
        
        # Simula il circuito con gli input estratti
        try:
            outputs = simulate_circuit(circuit, inputs)
            print("\nOutput simulato:")
            print(outputs)
        except Exception as e:
            print(f"Errore durante la simulazione: {e}")
    else:
        print("La formula non è soddisfacibile.")
    
    solver.delete()


def main():
    # Stampa la versione di CircuitGraph (se disponibile)
    print(f"Versione CircuitGraph: {cg.__version__ if hasattr(cg, '__version__') else 'Sconosciuta'}")
    
    # Creazione del circuito semplice (sommatore a 1 bit)
    circuit = create_simple_circuit()
    print(f"Circuito creato con {len(circuit.nodes())} nodi")
    print(f"Input: {circuit.inputs()}")
    print(f"Output: {circuit.outputs}")
    
    # Visualizzazione della struttura del circuito
    print("\nStruttura del circuito:")
    for node in sorted(circuit.nodes()):
        node_type = circuit.type(node)
        fanin = circuit.fanin(node)
        print(f"{node} ({node_type}) <- {fanin}")
    
    # Conversione manuale del circuito in CNF tramite Tseitin
    try:
        print("\nImplementando manualmente la conversione in CNF...")
        cnf_formula, var_map = manual_tseitin_cnf(circuit)
        print(f"Formula CNF creata con {len(cnf_formula.clauses)} clausole")
        
        # Stampa della mappa delle variabili (nodo -> numero variabile)
        print("\nMappa delle variabili (nodo -> variabile):")
        for node, var in sorted(var_map.items()):
            print(f"{node} -> {var}")
        
        # Stampa della formula CNF in formato DIMACS
        print_cnf_formula(cnf_formula)
        
        # Risoluzione della formula CNF
        print("\nRisoluzione della formula CNF:")
        solve_cnf(cnf_formula, circuit, var_map)
    except Exception as e:
        print(f"Errore durante la conversione in CNF: {e}")
    
    # Verifica del circuito con un set di input di test
    print("\nVerifica del circuito con input specifici:")
    test_inputs = {'a': 1, 'b': 1, 'cin': 0}
    try:
        result = simulate_circuit(circuit, test_inputs)
        print(f"Per input {test_inputs}, l'output è {result}")
    except Exception as e:
        print(f"Errore durante la simulazione: {e}")

if __name__ == "__main__":
    main()
