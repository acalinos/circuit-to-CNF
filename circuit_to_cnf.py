from circuit import *
from pysat import *
from pysat.formula import *
from pysat.solvers import Solver

c = circuit()

g0 = c.gate(op.id_, is_input=True)
g1 = c.gate(op.id_, is_input=True)
g2 = c.gate(op.xnor_, [g0, g1])

g3 = c.gate(op.id_, [g2], is_output=True)

# print("La stringa corrispondente è", c.gates.to_legible())
# print("Il circuito è composto da", c.count(), "porte")


# Funzione per dividere la stringa in elementi
def string_to_elements(string):
    # Rimuove le parentesi tonde all'inizio e alla fine della stringa
    string = string[1:-1]
    # Divide la stringa in base alla sequenza '),'
    elements = string.split("), ")
    # Rimuove eventuali spazi vuoti
    elements = [element.strip() for element in elements]
    # Ritorna la lista degli elementi
    return elements


# Funzione per analizzare le porte logiche del circuito in input
def gates_to_clauses(elements):

    # Inizializzo un contatore per gli input
    input_count = 0

    # Inizializzo un contatore per le porte logiche
    n = 0
    
    # Inizializzo una CNF
    cnf = CNF()

    for element in elements:
        
        # Se l'elemento è uguale a ('id',), allora è un input
        if element == "('id',":
            input_count = input_count + 1
            n = n + 1
            print("Numero di input:", input_count)

        # Se l'elemento è uguale a ('nand', n, m), allora è una porta NAND
        elif str(element).startswith("('nand',"):
            variable1 = int(element.split(",")[1].strip())
            variable2 = int(element.split(",")[2].strip())
            n = n + 1
            cnf.append([-variable1, -variable2])
            print("Nand tra le variabili", variable1, "e", variable2)

        # Se l'elemento è uguale a ('or', n, m), allora è una porta OR
        elif str(element).startswith("('or',"):
            variable1 = int(element.split(",")[1].strip())
            variable2 = int(element.split(",")[2].strip())
            n = n + 1
            cnf.append([variable1, variable2])
            print("Or tra le variabili", variable1, "e", variable2)
        
        # Se l'elemento è uguale a ('id', n), allora è un output
        elif str(element).startswith("('id',"):
            variable = element.split(",")[1].strip()
            # Elimina la parentesi tonda finale
            variable = variable[:-1]
            n = n + 1
            print("Output della variabile", variable)
            print("Fine del circuito, numero di porte:", n)
        
        else:
            print("Tipo di gate non riconosciuto:", element)

    return cnf
    

# Funzione per convertire il circuito in CNF
def circuit_to_cnf(c: circuit):

    # Converti il circuito in una stringa
    string = str(c.gates.to_legible())

    # Dividi la stringa in elementi
    elements = string_to_elements(string)

    if len(elements) == c.count():
        print("La stringa è stata divisa correttamente.")
        print(elements)

        cnf = gates_to_clauses(elements)
        print(cnf)
        return cnf

    else:
        print("Errore nella divisione della stringa.")
        return


# Test
circuit_to_cnf(c)