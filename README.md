# circuit-to-CNF
Tirocinio curricolare, Laurea Triennale in Informatica, Alma Mater Studiorum - Università di Bologna.

# Object
Implementazione di una libreria Python per la Crittanalisi Logica.

# Next step
+ Implementazione di porte n-arie
+ Implementazione della concatenazione di circuiti
  + sequenziali
    + CORRISPONDENZA UNIVOCA output -> input
    + passare circuito e lista di coppie della corrispondenza
  + paralleli
    + circuit1 U circuit2 controllando i gates in comune 
+ XOR di vettori di bit
+ Permutazione con tabella (a 1 corrisponde 7)

# Objectives
Obiettivi dell'attività di tirocinio sono la progettazione e lo sviluppo di una libreria per la Crittanalisi Logica in ambiente Python. 
La libreria permette di descrivere modularmente cifrari a blocco e cifrari di flusso nella forma di circuiti, ma soprattutto di tradurre il relativo problema di key recovery in un problema di soddisfacibilità per un'opportuna formula proposizionale, che venga poi passata ad un portfolio di SAT solver allo stato dell'arte.
Verrà poi studiata l'applicabilità della libreria ottenuta ad alcuni cifrari concreti.

# Activities
+ Studio della letteratura sulla Crittanalisi Logica e il problema SAT.
+ Studio e sperimentazione con alcune librerie Python per il problema SAT e per il progetto e la simulazione di circuiti.
+ Implementazione della libreria in Python.
+ Testing della libreria su Cifrari e Hash Functions.

# TEST

+ Test Vector 1:
Plaintext: 0000000000000000
Key:       0000000000000000
Expected:  8CA64DE9C1B123A7
Test: PASSED

+ Test Vector 2:
Plaintext: FFFFFFFFFFFFFFFF
Key:       FFFFFFFFFFFFFFFF
Expected:  7359B2163E4EDC58
Test: PASSED

+ Test Vector 3:
Plaintext: 0123456789ABCDEF
Key:       133457799BBCDFF1
Expected:  85E813540F0AB405
Test: FAILED

+ Test Vector 4:
Plaintext: 0123456789ABCDEF
Key:       0000000000000000
Expected:  95F8A5E5DD31D900
Test: FAILED