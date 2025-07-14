#!/usr/bin/env python3
# main.py

import sys
from multi_des_cnf import create_multi_des_cnf
from partial_sat_solver import solve_partial

def run_experiment(pairs, rounds):
    print(f"\n--- Esperimento DES x{len(pairs)} con {rounds} round ---")
    cnf = create_multi_des_cnf(pairs, rounds)
    # qui non ci sono variabili “remaining” da fissare, salvo la chiave,
    # perciò passiamo un dict vuoto: vogliamo sapere se esiste k.
    sat, rem = solve_partial(lambda: cnf, {})
    if sat:
        print("→ SAT: esiste chiave k compatibile!")
        print("   Assegnamento parziale chiave:", rem)
    else:
        print("→ UNSAT: non si riesce a forzare DES in", rounds, "round.")

if __name__ == "__main__":
    # Esempio di coppie generate dal tuo encrypt DES
    sample_pairs = [
        ("0123456789ABCDEF", "85E813540F0AB405"),
        ("1111111111111111", "F40379AB9E0EC533"),
        # aggiungi fino a n
    ]

    # 1) 16 round “vero”:
    run_experiment(sample_pairs, rounds=16)

    # 2) giro di “round ridotti” da 1 a 15
    for r in range(1, 16):
        run_experiment(sample_pairs, rounds=r)
