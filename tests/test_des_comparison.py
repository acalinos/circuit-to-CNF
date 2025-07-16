#!/usr/bin/env python3
import random
import pandas as pd
from des_python import des_encrypt as python_encrypt
from des_circuit import des_encrypt as circuit_encrypt

def main():
    NUM_TESTS = 20
    results = []

    for _ in range(NUM_TESTS):
        # Genera chiave e plaintext casuali a 64 bit (16 hex)
        key_hex = '{:016X}'.format(random.getrandbits(64))
        pt_hex  = '{:016X}'.format(random.getrandbits(64))

        # Calcola i ciphertext
        ct_python  = python_encrypt(pt_hex, key_hex)
        ct_circuit = circuit_encrypt(pt_hex, key_hex)

        # Registra il risultato
        results.append({
            'Plaintext':    pt_hex,
            'Key':          key_hex,
            'Python DES':  ct_python,
            'Circuit DES': ct_circuit,
            'Match':       ct_python == ct_circuit
        })

    # Mostra i risultati
    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    # Verifica finale
    if df['Match'].all():
        print("\nTutti i test PASSANO!")
    else:
        print("\nATTENZIONE: alcuni test NON corrispondono!")

if __name__ == "__main__":
    main()
