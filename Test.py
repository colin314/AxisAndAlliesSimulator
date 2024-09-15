import pandas as pd
from Simulator import Simulator


sim = Simulator()
sim.LoadAttacker("Attacker", "Fodder")
sim.LoadDefender("Defender", "Fodder")

sim.GenerateBattleStats(battleCount=1000)
# sim.GenerateExtendedBattleStats(battleCount=1000)
