import pytest
from new_circuit_to_cnf import (
    index_wires, cnf_and, cnf_or, cnf_xor, cnf_buf,
    add_unit_clauses, circuit_to_cnf
)
from new_ExtendedCircuitgraph import Circuit


def test_index_wires_empty():
    cir = Circuit()
    # No gates, no wires
    mapping = index_wires(cir)
    assert mapping == {}


def test_index_wires_non_empty():
    cir = Circuit()
    cir.add_gate('AND', ['a', 'b'], 'c')
    mapping = index_wires(cir)
    # sorted order: ['a','b','c']
    assert mapping == {'a': 1, 'b': 2, 'c': 3}


def test_cnf_and():
    # AND gate: y = a AND b
    clauses = cnf_and([1, 2], 3)
    # Expect 2*(inputs) clauses: (¬a ∨ y), (¬b ∨ y), (¬y ∨ a), (¬y ∨ b)
    assert [-1, 3] in clauses
    assert [-2, 3] in clauses
    assert [-3, 1] in clauses
    assert [-3, 2] in clauses
    assert len(clauses) == 4


def test_cnf_or():
    # OR gate: y = a OR b OR c
    clauses = cnf_or([1, 2, 3], 4)
    # Expect one clause (1,2,3,¬4) and each (4,¬i)
    assert [1, 2, 3, -4] in clauses
    for i in [1, 2, 3]:
        assert [4, -i] in clauses
    assert len(clauses) == 1 + 3


def test_cnf_xor():
    # XOR gate: y = a ⊕ b
    clauses = cnf_xor(1, 2, 3)
    # Expect 4 clauses
    assert len(clauses) == 4
    # Check one known combination
    assert [-1, -2, -3] in clauses
    assert [1, -2, 3] in clauses


def test_cnf_buf():
    # BUF gate: y = x
    clauses = cnf_buf(1, 2)
    assert [-1, 2] in clauses
    assert [-2, 1] in clauses
    assert len(clauses) == 2


def test_add_unit_clauses():
    clauses = []
    mapping = {'a': 1, 'b': 2}
    fixed = {'a': True, 'b': False}
    add_unit_clauses(clauses, fixed, mapping)
    assert [1] in clauses
    assert [-2] in clauses


def test_circuit_to_cnf_simple():
    # Build circuit: d = a AND b; y = d OR c
    cir = Circuit()
    cir.add_gate('AND', ['a', 'b'], 'd')
    cir.add_gate('OR', ['d', 'c'], 'y')
    nvars, clauses = circuit_to_cnf(cir)
    # Wires: a,b,c,d,y -> 5 variables
    assert nvars == 5
    # Check some expected clauses
    # from AND: (¬a ∨ d), (¬b ∨ d), (¬d ∨ a), (¬d ∨ b)
    assert [-1, 4] in clauses
    assert [-2, 4] in clauses
    # from OR: (d ∨ c ∨ ¬y)
    # mapping: a:1,b:2,c:3,d:4,y:5
    assert [4, 3, -5] in clauses

if __name__ == '__main__':
    pytest.main()
