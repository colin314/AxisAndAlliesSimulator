from dyce import H
from Units import *
import pandas as pd
inf = Infantry((2,3))

print(inf.unitHitDie())
print(inf.unitHitDie(False))

infArt = InfArt([(3,3),(4,4)])
print(infArt.unitHitDie())