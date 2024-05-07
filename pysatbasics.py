from pysat.formula import CNF

cnf = CNF()
cnf.append([-1, 2])
cnf.append([-2, 3])

print(cnf)