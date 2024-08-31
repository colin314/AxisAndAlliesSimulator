from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median
from Resources import bcolors
import sys

unitListsFile = "unitLists.csv"

def SimulateBattle(
    attacker: UnitCollection,
    defender: UnitCollection,
    retreatThreshold = 0,
    maxRounds = -1,
    printOutcome=False,
    printBattle=False,
):
    maxRounds = sys.maxsize if maxRounds < 0 else maxRounds
    round = 0
    while attacker.unitCount() > 0 and defender.unitCount() > 0 and attacker.unitCount() > retreatThreshold and round < maxRounds:
        round += 1
        print(round)
        attackerHits = attacker.attack()
        defenderHits = defender.defend()
        attacker.takeLosses(defenderHits)
        defender.takeLosses(attackerHits)
        if printBattle:
            print("Battle")
            PrintBattleState(round, attacker, defender, attackerHits, defenderHits)
    if printOutcome:
        PrintCombatants(attacker, defender)
    return (attacker.unitCount(), defender.unitCount())

def PrintBattleState(round, attacker, defender, aH, dH):
    print(f"Round {bcolors.RED}{round}{bcolors.ENDC}")
    print(u'\u2500' * 30)
    print(f"Attacker Hits: {aH}")
    print(f"Defender Hits: {dH}")
    PrintCombatants(attacker, defender)

def PrintCombatants(attacker:UnitCollection, defender:UnitCollection):
    print("Attacker: ")
    attacker.PrintCollection()
    print("Defender: ")
    defender.PrintCollection()
    print("\n")

def LoadUnitCollection(listName, profileName):    
    profile = pd.read_csv(f'UnitProfiles_{profileName}.csv', encoding='utf-8',delimiter=",")
    unitList = pd.read_csv(unitListsFile, encoding='utf-8',delimiter=",")
    units = UnitCollection(unitList[listName],profile)
    return units

def GenerateBattleStats(attacker, defender, battleCount=10000):
    results = []
    unitsLeft = []
    for i in range(battleCount):
        (a, d) = SimulateBattle(attacker, defender)
        results.append(1 if a > d else 0)
        unitsLeft.append([a,d])
        attacker.reset()
        defender.reset()
    attackWinRate = float(sum(results)) / float(len(results))
    print(f"attacker wins \033[91m{attackWinRate:2.2%}\033[97m percent of the time\033[0m")
    attackingUnitsLeft = mean([x[0] for x in unitsLeft if x[0] > 0])
    defendingUnitsLeft = mean([x[1] for x in unitsLeft if x[1] > 0])
    print(f"Attacking units left if attacker won: {attackingUnitsLeft:.2f}")
    print(f"Defending units left if defender won: {defendingUnitsLeft:.2f}")
    print(f"Attacking units left on average: {mean([x[0] for x in unitsLeft]):.2f}")
    print(f"Defending units left on average: {mean([x[1] for x in unitsLeft]):.2f}")
    print()

def swapPlaces(attacker,defender):
    return (defender, attacker)

if __name__ == "__main__":
    print(Unit.diceSize)
    
    # russianUnits = LoadUnitCollection("Russia","Basic")
    # germanUnits = LoadUnitCollection("Germany","Basic")


    Unit.diceSize = 6
    print("Equal - Original")
    attacker = LoadUnitCollection("Germany", "Original")
    defender = LoadUnitCollection("Russia","Original")
    attacker.reset()
    defender.reset()
    SimulateBattle(attacker, defender,maxRounds=2,printBattle=True)
