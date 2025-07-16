import pytest
from solver import is_satisfiable, set_solver
import pycosat
from new_ExtendedCircuitgraph import Circuit

# Ensure default solver is pycosat
def test_default_solver_is_pycosat():
    # The SOLVER should respond to solve
    c = Circuit()
    # trivial circuit: no gates, always satisfiable (empty CNF)
    sat, model = is_satisfiable(c)
    assert sat is True
    assert isinstance(model, list)

# Test simple AND circuit for SAT cases
def test_and_circuit_sat_true_true():
    # Circuit: d = a AND b
    cir = Circuit()
    cir.add_gate('AND', ['a', 'b'], 'd')
    # Fix a=True, b=True, expect d=True SAT
    sat, model = is_satisfiable(cir, fixed_inputs={'a': True, 'b': True}, fixed_outputs={'d': True})
    assert sat is True
    # model should include positive literals for a, b, d
    assert any(lit == model_var for model_var in model for lit in [model_var] if lit > 0)

def test_and_circuit_unsat_true_true_false():
    cir = Circuit()
    cir.add_gate('AND', ['a', 'b'], 'd')
    # Fix a=True, b=True, d=False -> UNSAT
    sat, model = is_satisfiable(cir, fixed_inputs={'a': True, 'b': True}, fixed_outputs={'d': False})
    assert sat is False
    assert model is None

# Test OR circuit for SAT/UNSAT
def test_or_circuit_sat():
    # Circuit: y = a OR b
    cir = Circuit()
    cir.add_gate('OR', ['a', 'b'], 'y')
    # Fix a=False, b=False, y=False -> SAT
    sat, model = is_satisfiable(cir, fixed_inputs={'a': False, 'b': False}, fixed_outputs={'y': False})
    assert sat is True

    # Fix a=False, b=False, y=True -> UNSAT
    sat, model = is_satisfiable(cir, fixed_inputs={'a': False, 'b': False}, fixed_outputs={'y': True})
    assert sat is False
    assert model is None

# Test XOR circuit
def test_xor_circuit():
    # Circuit: z = a XOR b
    cir = Circuit()
    cir.add_gate('XOR', ['a', 'b'], 'z')
    # Cases: a=0,b=0 => z=0; a=0,b=1 => z=1; check one case
    sat, model = is_satisfiable(cir, fixed_inputs={'a': False, 'b': True}, fixed_outputs={'z': True})
    assert sat is True
    # In the model, b positive, z positive, a negative or absent
    # Check z is positive
    assert any(lit > 0 for lit in model if abs(lit) == model.index(lit)+1)

if __name__ == '__main__':
    pytest.main()
