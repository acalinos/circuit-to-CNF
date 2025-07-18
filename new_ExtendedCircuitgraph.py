# ExtendedCircuitgraph.py
from typing import List, Tuple, Dict, Any

class Gate:
    """
    Rappresenta una porta logica generica.
    Attributes:
        gate_type: tipo di porta, es. 'AND', 'OR', 'XOR', 'BUF'
        inputs: lista di nomi di wire in ingresso
        output: nome del wire di uscita
    """
    def __init__(self, gate_type: str, inputs: List[str], output: str):
        self.gate_type = gate_type
        self.inputs = inputs
        self.output = output

    def __repr__(self) -> str:
        inputs_str = ", ".join(self.inputs)
        return f"Gate(type={self.gate_type}, inputs=[{inputs_str}], output={self.output})"

class Circuit:
    """
    Rappresenta un circuito combinatorio come lista di gate.
    """
    def __init__(self):
        # Lista ordinata di Gate
        self.gates: List[Gate] = []
        # Metadati opzionali per ogni wire (chiave: nome wire)
        self.wires: Dict[str, Any] = {}

    def add_gate(self, gate_type: str, inputs: List[str], output: str) -> None:
        """
        Aggiunge una porta n-arie.
        Args:
            gate_type: tipo di porta ('AND','OR','XOR','BUF',...)
            inputs: lista di wire in ingresso
            output: nome del wire di uscita
        """
        # Registra wire di output e di input
        self.wires.setdefault(output, {})
        for inp in inputs:
            self.wires.setdefault(inp, {})
        # Aggiunge la gate
        self.gates.append(Gate(gate_type, inputs, output))

    def add(self, output: str, gate_type: str, fanin: List[str]) -> None:
        """
        Compatibilità con des_circuit: aggiunge una porta 'gate_type' con fanin e output.
        """
        self.add_gate(gate_type.upper(), fanin, output)

    def nodes(self) -> List[str]:
        """
        Ritorna la lista dei nomi di tutte le wire (nodi) nel circuito.
        """
        return list(self.wires.keys())

    def sequential_compose(self, other: 'Circuit', mapping: List[Tuple[str, str]]) -> 'Circuit':
        """
        Restituisce un nuovo Circuit ottenuto collegando
        l'output di questo circuito agli input di 'other'.
        mapping: lista di tuple (output_wire, input_wire)
        """
        composed = Circuit()
        # Copia i gate e i wire di self
        composed.gates = [Gate(g.gate_type, list(g.inputs), g.output) for g in self.gates]
        composed.wires = dict(self.wires)
        # Mappa le coppie per sostituzione
        rename_map = {out: inp for out, inp in mapping}
        # Copia i gate di other rinominando i wire
        for g in other.gates:
            new_inputs = [rename_map.get(w, w) for w in g.inputs]
            new_output = rename_map.get(g.output, g.output)
            composed.add_gate(g.gate_type, new_inputs, new_output)
        return composed

    def parallel_compose(self, other: 'Circuit') -> 'Circuit':
        """Restituisce un nuovo Circuit combinando gate di questo e di 'other'."""
        composed = Circuit()
        # Copia gate e wire
        composed.gates = [Gate(g.gate_type, list(g.inputs), g.output) for g in self.gates]
        composed.gates += [Gate(g.gate_type, list(g.inputs), g.output) for g in other.gates]
        composed.wires = {**self.wires, **other.wires}
        return composed

    def xor_vector(self, a_wires: List[str], b_wires: List[str], out_wires: List[str]) -> None:
        """Applica XOR bitwise su due vettori di wire."""
        if not (len(a_wires) == len(b_wires) == len(out_wires)):
            raise ValueError("I vettori devono avere la stessa lunghezza")
        for a, b, o in zip(a_wires, b_wires, out_wires):
            self.add_gate('XOR', [a, b], o)

    def permute(self, in_wires: List[str], perm_table: List[int], out_wires: List[str]) -> None:
        """Permuta un vettore di wire secondo perm_table usando BUF."""
        n = len(out_wires)
        if not (len(in_wires) == len(perm_table) == n):
            raise ValueError("Lunghezze di in_wires, perm_table e out_wires devono coincidere")
        for i, j in enumerate(perm_table):
            src = in_wires[j]
            dst = out_wires[i]
            # Rappresentiamo la permutazione con un buffer
            self.add_gate('BUF', [src], dst)

    def __repr__(self) -> str:
        return f"Circuit(gates={self.gates})"
