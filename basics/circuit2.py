from circuit import *

c = circuit()

g1 = c.gate(op.id_, is_input=True)
g2 = c.gate(op.id_, is_input=True)
g3 = c.gate(op.id_, is_input=True)

ng1 = c.gate(op.not_, [g1])
ng2 = c.gate(op.not_, [g2])
ng3 = c.gate(op.not_, [g3])

g4 = c.gate(op.or_, [g1, g2])
g5 = c.gate(op.or_, [g1, ng3])
g6 = c.gate(op.or_, [ng2, g3])

# g7 = c.gate(op.and_, [g4, g5, g6]) - Value Error

g7 = c.gate(op.and_, [c.gate(op.and_, [g4, g5]), g6])

g8 = c.gate(op.id_, [g7], is_output=True)

print("Il circuito appena creato è", c.gates.to_legible())
# Il circuito appena creato è (('id',), ('id',), ('id',), ('not', 0), ('not', 1), ('not', 2), ('or', 0, 1), ('or', 0, 5), ('and', 6, 7), ('id', 8))

print("Il circuito è composto da", c.count(), "porte")
# Il circuito è composto da 10 porte