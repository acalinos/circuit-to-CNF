# circuit basics (https://pypi.org/project/circuit/)

from circuit import *

c = circuit()
# c.gate
# porta di input: c.gate(op.id_, is_input=True)
# porta di operazione tra g1 e g2: c.gate(op.op_name, [gate1, gate2, ...])
# porta di output: c.gate(op.id_, is_output=True)
g0 = c.gate(op.id_, is_input=True)
g1 = c.gate(op.id_, is_input=True)
g2 = c.gate(op.and_, [g0, g1])
g3 = c.gate(op.id_, [g2], is_output=True)

print("Il circuito appena creato è", c.gates.to_legible())
# print("Il numero di porte in questo circuito è", c.count())
print("Per l'input [0, 0], l'output è", c.evaluate([0, 0]))
print("Per l'input [0, 1], l'output è", c.evaluate([0, 1]))
print("Per l'input [1, 0], l'output è", c.evaluate([1, 0]))
print("Per l'input [1, 1], l'output è", c.evaluate([1, 1]))
# print([list(c.evaluate(bs)) for bs in [[0, 0], [0, 1], [1, 0], [1, 1]]])