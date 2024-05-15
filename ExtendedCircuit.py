from circuit import *
from pysat import *
from pysat.formula import *
from pysat.solvers import Solver

class ExtendedCircuit(circuit):

    # Funzione per dividere la stringa in elementi
    def string_to_elements(self, string):
        # Rimuove le parentesi tonde all'inizio e alla fine della stringa
        string = string[1:-1]
        # Divide la stringa in base alla sequenza '),'
        elements = string.split("), ")
        # Rimuove eventuali spazi vuoti
        elements = [element.strip() for element in elements]
        # Ritorna la lista degli elementi
        return elements


    # Funzione per analizzare le porte logiche del circuito in input
    def gates_to_clauses(self, elements):

        # Inizializzo un contatore per gli input
        input_count = 0

        # Inizializzo un contatore per le porte logiche
        n = 1

        # Inizializzo un array di coppie di valori per le porte NOT
        nots = []
        
        # Inizializzo una CNF
        cnf = CNF()

        for element in elements:
            
            # Se l'elemento è uguale a ('id',), allora è un input
            if element == "('id',":
                input_count = input_count + 1
                if input_count > 1:
                    n = n + 1
                else:
                    n = 1
                print("Numero di input:", input_count, ", n:", n)

            # Se l'elemento è uguale a ('not', n), allora è una porta not
            elif str(element).startswith("('not',"):
                variable = int(element.split(",")[1].strip()) + 1
                n = n + 1         
                # Aggiungo la coppia di valori (n, variable) all'array nots
                nots.append((variable, n)) 
                print("Nella lista nots:", nots, ", quindi ogni volta che trovo", n, "scrivo", -variable)

            # Se l'elemento è uguale a ('and', n, m), allora è una porta and
            elif str(element).startswith("('and',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 AND V2 = (V1 OR V1) AND (V2 OR V2)

                bool1 = False
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([variable1, variable1])
                    cnf.append([variable2, variable2])
                elif bool1 and not bool2:
                    cnf.append([-variable1, -variable1])
                    cnf.append([variable2, variable2])
                elif not bool1 and bool2:
                    cnf.append([variable1, variable1])
                    cnf.append([-variable2, -variable2])
                elif bool1 and bool2:
                    cnf.append([-variable1, -variable1])
                    cnf.append([-variable2, -variable2])

            # Se l'elemento è uguale a ('nand', n, m), allora è una porta nand
            elif str(element).startswith("('nand',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 NAND V2 = -(V1 AND V2) = -V1 OR -V2 (Leggi di De Morgan)

                bool1 = False
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([-variable1, -variable2])
                elif bool1 and not bool2:
                    cnf.append([variable1, -variable2])
                elif not bool1 and bool2:
                    cnf.append([-variable1, variable2])
                elif bool1 and bool2:
                    cnf.append([variable1, variable2])

            # Se l'elemento è uguale a ('or', n, m), allora è una porta or
            elif str(element).startswith("('or',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 OR V2

                bool1 = False 
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([variable1, variable2])
                elif bool1 and not bool2:
                    cnf.append([-variable1, variable2])
                elif not bool1 and bool2:
                    cnf.append([variable1, -variable2])
                elif bool1 and bool2:
                    cnf.append([-variable1, -variable2])   
                elif bool1 and bool2:  
                    cnf.append([-variable1, -variable2])       
                
            # Se l'elemento è uguale a ('nor', n, m), allora è una porta nor
            elif str(element).startswith("('nor',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 NOR V2 = (-V1 OR -V1) AND (-V2 OR -V2)

                bool1 = False
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([-variable1, -variable1])
                    cnf.append([-variable2, -variable2])
                elif bool1 and not bool2:
                    cnf.append([variable1, variable1])
                    cnf.append([-variable2, -variable2])
                elif not bool1 and bool2:
                    cnf.append([-variable1, -variable1])
                    cnf.append([variable2, variable2])
                elif bool1 and bool2:
                    cnf.append([variable1, variable1])
                    cnf.append([variable2, variable2])
            
            # Se l'elemento è uguale a ('xor', n, m), allora è una porta xor
            elif str(element).startswith("('xor',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 XOR V2 = (V1 OR V2) AND (-V1 OR -V2)

                bool1 = False
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([variable1, variable2])
                    cnf.append([-variable1, -variable2])
                elif bool1 and not bool2:
                    cnf.append([-variable1, variable2])
                    cnf.append([variable1, -variable2])
                elif not bool1 and bool2:
                    cnf.append([variable1, -variable2])
                    cnf.append([-variable1, variable2])
                elif bool1 and bool2:
                    cnf.append([-variable1, -variable2])
                    cnf.append([variable1, variable2])
            
            # Se l'elemento è uguale a ('xnor', n, m), allora è una porta xnor
            elif str(element).startswith("('xnor',"):
                variable1 = int(element.split(",")[1].strip())
                variable1 = variable1 + 1
                variable2 = int(element.split(",")[2].strip())
                variable2 = variable2 + 1

                n = n + 1

                # V1 XNOR V2 = (-V1 OR V2) AND (V1 OR -V2)

                bool1 = False
                bool2 = False

                for i in range(0, n):
                    if (i, variable1) in nots:
                        variable1 = i
                        bool1 = True
                    if (i, variable2) in nots:
                        variable2 = i
                        bool2 = True

                if not bool1 and not bool2:
                    cnf.append([-variable1, variable2])
                    cnf.append([variable1, -variable2])
                elif bool1 and not bool2:
                    cnf.append([variable1, variable2])
                    cnf.append([-variable1, -variable2])
                elif not bool1 and bool2:
                    cnf.append([-variable1, -variable2])
                    cnf.append([variable1, variable2])
                elif bool1 and bool2:
                    cnf.append([variable1, -variable2])
                    cnf.append([-variable1, variable2])
            
            # Se l'elemento è uguale a ('id', n), allora è una porta output
            elif str(element).startswith("('id',"):
                variable = element.split(",")[1].strip()
                # Elimina la parentesi tonda finale
                variable = variable[:-1]
                n = n + 1
                print("Fine del circuito, numero di porte:", n)
            
            else:
                print("Tipo di gate non riconosciuto:", element)

        return cnf
   

    # Funzione per convertire il circuito in CNF
    def to_cnf(self):

        # Converti il circuito in una stringa
        string = str(self.gates.to_legible())

        # Dividi la stringa in elementi
        elements = self.string_to_elements(string)

        if len(elements) == self.count():
            print("La stringa è stata divisa correttamente.")
            # print(elements)

            cnf = self.gates_to_clauses(elements)
            print(cnf)
            return cnf

        else:
            print("Errore nella divisione della stringa.")
            return


    # Funzione per testare la soddisfacibilità della CNF
    def cnf_to_model(self, cnf: CNF):
        solver = Solver(name="g4")
        solver.append_formula(cnf)

        if solver.solve():
            model = solver.get_model()
            print("Modello trovato:", model)

        else:
            model = None
            print("Modello non trovato.")
            
        return model


# Test
ec = ExtendedCircuit()

g1 = ec.gate(op.id_, is_input=True)
g2 = ec.gate(op.id_, is_input=True)
g3 = ec.gate(op.xnor_, [g1, g2])
g4 = ec.gate(op.and_, [g1, g3])
g5 = ec.gate(op.nor_, [g2, g4])
g6 = ec.gate(op.or_, [g3, g5])

g7 = ec.gate(op.id_, [g6], is_output=True)

print("La stringa corrispondente è", ec.gates.to_legible())
print("Il circuito è composto da", ec.count(), "porte")

# Converti il circuito in CNF e trova un modello
cnf = ec.to_cnf()
model = ec.cnf_to_model(cnf)