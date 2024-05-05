from circuit import *

c = circuit()

g0 = c.gate(op.id_, is_input=True)
g1 = c.gate(op.id_, is_input=True)
g2 = c.gate(op.id_, is_input=True)
g3 = c.gate(op.id_, is_input=True)

g4 = c.gate(op.and_, [g1, g2])
g5 = c.gate(op.or_, [g4, g3])
g6 = c.gate(op.xor_, [g0, g5])
g7 = c.gate(op.not_, [g6])

g8 = c.gate(op.id_, [g7], is_output=True)


print("Il circuito appena creato è", c.gates.to_legible())
# Il circuito appena creato è (('id',), ('id',), ('id',), ('id',), ('and', 1, 2), ('or', 4, 3), ('xor', 0, 5), ('not', 6), ('id', 7))

print("Il circuito è composto da", c.count(), "porte")
# Il circuito è composto da 9 porte

c.prune_and_topological_sort_stable()
print("Il circuito ottimizzato è composto da", c.count(), "porte")
# Il circuito ottimizzato è composto da 9 porte