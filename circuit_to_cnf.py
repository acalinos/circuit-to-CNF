from circuit import *
from pysat import *
from pysat.formula import *

c = circuit()

g0 = c.gate(op.id_, is_input=True)
g1 = c.gate(op.id_, is_input=True)
g2 = c.gate(op.xnor_, [g0, g1])

g3 = c.gate(op.id_, [g2], is_output=True)

# print("La stringa corrispondente è", c.gates.to_legible())
# print("Il circuito è composto da", c.count(), "porte")


# Funzione per dividere la stringa in elementi
def split_string(string):
    # Rimuovi le parentesi tonde all'inizio e alla fine della stringa
    string = string[1:-1]
    # Dividi la stringa in base alla sequenza '),'
    elements = string.split("), ")
    # Rimuovi eventuali spazi vuoti
    elements = [element.strip() for element in elements]
    # Ritorna la lista degli elementi
    return elements


# Funzione per analizzare le porte logiche del circuito in input
def analize_gates(elements, input_count, clauses_list):

    n = 0

    for element in elements:
        
        # Se l'elemento è uguale a ('id',), allora è un input
        if element == "('id',":
            input_count = input_count + 1
            n = n + 1
            print("Numero di input:", input_count)

        # Se l'elemento è uguale a ('not', n), allora è una porta not
        elif str(element).startswith("('not',"):
            # Identifica la variabile dal numero
            variable = element.split(",")[1].strip()
            # Casting della variabile a intero
            variable = int(variable) 
            n = n + 1          
            print("Not della variabile", variable)

        # Se l'elemento è uguale a ('and', n, m), allora è una porta and
        elif str(element).startswith("('and',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            and_clause = And(Atom(variable1), Atom(variable2))
            n = n + 1
            print("And tra le variabili", variable1, "e", variable2)
            print(and_clause)

        # Se l'elemento è uguale a ('nand', n, m), allora è una porta nand
        elif str(element).startswith("('nand',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            nand_clause = Neg(And(Atom(variable1), Atom(variable2)))
            n = n + 1
            print("Nand tra le variabili", variable1, "e", variable2)
            print(nand_clause)

        # Se l'elemento è uguale a ('or', n, m), allora è una porta or
        elif str(element).startswith("('or',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            or_clause = Or(Atom(variable1), Atom(variable2))
            n = n + 1
            print("Or tra le variabili", variable1, "e", variable2)
            print(or_clause)

        # Se l'elemento è uguale a ('nor', n, m), allora è una porta nor
        elif str(element).startswith("('nor',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            nor_clause = Neg(Or(Atom(variable1), Atom(variable2)))
            n = n + 1
            print("Nor tra le variabili", variable1, "e", variable2)
            print(nor_clause)
        
        # Se l'elemento è uguale a ('xor', n, m), allora è una porta xor
        elif str(element).startswith("('xor',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            xor_clause = XOr(Atom(variable1), Atom(variable2))
            n = n + 1
            print("Xor tra le variabili", variable1, "e", variable2)
            print(xor_clause)
        
        # Se l'elemento è uguale a ('xnor', n, m), allora è una porta xnor
        elif str(element).startswith("('xnor',"):
            variable1 = element.split(",")[1].strip()
            variable2 = element.split(",")[2].strip()
            xnor_clause = Neg(XOr(Atom(variable1), Atom(variable2)))
            n = n + 1
            print("Xnor tra le variabili", variable1, "e", variable2)
            print(xnor_clause)
        
        # Se l'elemento è uguale a ('id', n), allora è una porta output
        elif str(element).startswith("('id',"):
            variable = element.split(",")[1].strip()
            # Elimina la parentesi tonda finale
            variable = variable[:-1]
            n = n + 1
            print("Output della variabile", variable)
            print("Fine del circuito, totale cose:", n)
        
        else:
            print("Tipo di gate non riconosciuto:", element)
    

# Funzione per convertire il circuito in CNF
def circuit_to_cnf(c: circuit):

    # Converti il circuito in una stringa
    string = str(c.gates.to_legible())

    # Dividi la stringa in elementi
    elements = split_string(string)

    if len(elements) == c.count():
        print("La stringa è stata divisa correttamente.")
        print(elements)

        input_count = 0
        clauses_list = []

        analize_gates(elements, input_count, clauses_list)
        # print(analize_gates(elements, input_count, clauses_list))

    else:
        print("Errore nella divisione della stringa.")
        return


# Test
circuit_to_cnf(c)