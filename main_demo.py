# main_demo.py
# Test semplice per dimostrare l'uso del modulo solver e circuitgraph

from new_ExtendedCircuitgraph import Circuit
from solver import is_satisfiable

def demo_simple_circuit():
    # Esempio: y = (a AND b) OR c
    cir = Circuit()
    cir.add_gate('AND', ['a','b'], 'd')
    cir.add_gate('OR',  ['d','c'], 'y')

    # Fissa input a=True, b=True e l'output y=True
    sat, model = is_satisfiable(
        cir,
        fixed_inputs={'a': True, 'b': True},
        fixed_outputs={'y': True}
    )

    print("Circuit:", cir)
    print(f"SAT? {sat}")
    if sat:
        print("Modello (var positive=true):", model)
    else:
        print("Nessun assegnamento possibile.")

if __name__ == "__main__":
    demo_simple_circuit()
