import pandas as pd
from Simulator import Simulator


sim = Simulator()
sim.LoadAttacker("Attacker", "Fodder")
sim.LoadDefender("Defender", "Fodder")

sim.GenerateExtendedBattleStats(battleCount=500)
