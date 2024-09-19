import pandas as pd
from Simulator import Simulator

resultArr=[
    [1,5,0,16],
    [0,0,6,-12]
]
resultArr = [x for list in resultArr for x in list]
#resultDf = pd.DataFrame(resultArr, columns=[
#                        "Attacker Won", "Remainder Attacker", "Remainder Defender", "Average IPC Swing (Attacker)"])

print(resultArr)
# sim.GenerateExtendedBattleStats(battleCount=1000)
