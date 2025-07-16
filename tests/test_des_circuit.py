import circuitgraph as cg
from archive.ExtendedCircuitgraph_0 import manual_tseitin_cnf, simulate_circuit
from des_circuit import *
import sys

# Test vector standard DES (da NIST)
def main():
    
    with open("output.txt", "w") as f:
        original_stdout = sys.stdout
        sys.stdout = f
        
        print("=== Test DES Implementation ===")
        plaintext = "0123456789ABCDEF"
        key = "0000000000000000"
        expected_ciphertext = "95F8A5E5DD31D900"
        print(f"Test Vector 1:")
        print(f"Plaintext: {plaintext}")
        print(f"Key:       {key}")
        print(f"Expected:  {expected_ciphertext}")
        try:
            result = des_encrypt(plaintext, key)
            print(f"Result:    {result}")
            print(f"Test {'PASSED' if result == expected_ciphertext else 'FAILED'}")
        except Exception as e:
            print(f"Error during test: {str(e)}")
            import traceback
            traceback.print_exc()   

        sys.stdout = original_stdout
    print("Test completed. Check output.txt for results.")

if __name__ == "__main__":
    main()