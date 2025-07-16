# setup.py
from setuptools import setup

setup(
    name="new_circuit_to_cnf",
    version="0.1.0",
    py_modules=["new_circuit_to_cnf", "new_ExtendedCircuitgraph", "solver"],
    install_requires=["pycosat"],
)
