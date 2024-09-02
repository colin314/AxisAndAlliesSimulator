from functools import cmp_to_key
from Units import *
from UnitCollection import UnitCollection
from Simulator import Simulator
from Hit import Hit

sim = Simulator()
units = sim.LoadUnitCollection("BasicNaval", "Basic")

# subHit = Hit(Submarine([4,4]))
# print(subHit.Vulnerable,subHit.Immune)
# airHit = Hit(Fighter([6,8]))
# print(airHit.Vulnerable,airHit.Immune)
# hit = Hit(Infantry([2,3]))
# print(hit.Vulnerable,hit.Immune)

# print()
# hitList = [hit,airHit,subHit]
# print([h.Vulnerable for h in hitList])
# print([h.Immune for h in hitList])
# hitList.sort()
# print([h.Vulnerable for h in hitList])
# print([h.Immune for h in hitList])