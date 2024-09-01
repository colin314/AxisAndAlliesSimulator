from Units import *
from Hit import *

sub = Submarine([4,4])
dd = Destroyer([4,4])
fighter = Fighter([6,8])

hit = SubHit()

print(hit.UnitIsValidTarget(dd))
print(hit.UnitIsValidTarget(fighter))
print(hit.UnitTypeIsValidTarget(StratBomber))
print(hit.UnitTypeIsValidTarget(Transport))