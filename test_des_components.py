import circuitgraph as cg
from ExtendedCircuitgraph import manual_tseitin_cnf, simulate_circuit
from des_components import *

# Test vector standard DES (da NIST)
def main():
    print("=== Test DES Implementation ===")
    
    # Test vector 1 (standard NIST)
    plaintext = "0123456789ABCDEF"
    key = "133457799BBCDFF1"
    expected_ciphertext = "85E813540F0AB405"  # Risultato atteso
    
    print(f"Test Vector 1:")
    print(f"Plaintext: {plaintext}")
    print(f"Key:       {key}")
    print(f"Expected:  {expected_ciphertext}")
    
    try:
        # Crea un circuito per il test
        circuit = cg.Circuit()
        
        # Converti plaintext e chiave in valori binari
        plaintext_bin = bin(int(plaintext, 16))[2:].zfill(64)
        key_bin = bin(int(key, 16))[2:].zfill(64)
        
        # Crea input wires
        input_wires = []
        for i in range(64):
            wire_name = f"plaintext_{i}"
            circuit.add(wire_name, 'input')
            input_wires.append(wire_name)
        
        key_wires = []
        for i in range(64):
            wire_name = f"key_{i}"
            circuit.add(wire_name, 'input')
            key_wires.append(wire_name)
        
        # Crea valori di input
        input_values = {}
        for i, bit in enumerate(plaintext_bin):
            input_values[input_wires[i]] = bit == '1'
        
        for i, bit in enumerate(key_bin):
            input_values[key_wires[i]] = bit == '1'
        
        # Esegui DES
        output_wires = des_block(circuit, input_wires, key_wires)
        
        # Imposta gli output
        for wire in output_wires:
            circuit.set_output(wire)

        print(f"Numero totale di nodi nel circuito: {len(circuit.nodes())}")
        print(f"Il nodo r1_sbox4_not_in0 esiste? {'Sì' if 'r1_sbox4_not_in0' in circuit.nodes() else 'No'}")

        # Verifica dei nodi problematici noti
        problematic_nodes = [
            'r1_sbox4_not_in0', 'r1_sbox5_not_in4', 'r1_sbox6_not_in1'
        ]

        for node in problematic_nodes:
            if node in circuit.nodes():
                print(f"Il nodo {node} esiste nel circuito")
                # Verifica anche i suoi fanin
                print(f"  Fanin: {list(circuit.fanin(node))}")
                for fanin_node in circuit.fanin(node):
                    if fanin_node not in circuit.nodes():
                        print(f"  !! Il nodo di fanin {fanin_node} non esiste !!")
            else:
                print(f"Il nodo {node} NON esiste nel circuito")
        
        # Simula il circuito
        result = simulate_circuit(circuit, input_values)
        
        # Converti il risultato in esadecimale
        output_bits = ""
        for wire in output_wires:
            output_bits += "1" if result[wire] else "0"
        
        actual_ciphertext = hex(int(output_bits, 2))[2:].upper().zfill(16)
        
        print(f"Result:    {actual_ciphertext}")
        print(f"Test {'PASSED' if actual_ciphertext == expected_ciphertext else 'FAILED'}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()