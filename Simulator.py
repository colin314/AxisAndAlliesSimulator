from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median

unitLists = "UnitLists.csv"

def SimulateBattle(
    attacker: UnitCollection,
    defender: UnitCollection,
    printOutcome=False,
    printBattle=False,
):
    round = 0
    while attacker.unitCount() > 0 and defender.unitCount() > 0:
        round += 1
        attackerHits = attacker.attack()
        defenderHits = defender.defend()
        attacker.takeLosses(defenderHits)
        defender.takeLosses(attackerHits)
        if printBattle:
            print(f"Round {round}")
            print(f"Attacker: {attackerHits} hits")
            print(str(attacker))
            print(f"Defender: {defenderHits} hits")
            print(str(defender))
    if printOutcome:
        print(f"Attacker: ")
        print(str(attacker))
        print("Defender: ")
        print(str(defender))
    return (attacker.unitCount(), defender.unitCount())

def LoadUnitCollection(listName, profileName):    
    profile = pd.read_csv(f'UnitProfiles_{profileName}.csv', encoding='utf-8',delimiter=",")
    print(profile)
    units = pd.read_csv(unitLists, encoding='utf-8',delimiter=",")
    print(units[listName])

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
    
    LoadUnitCollection("Russia","Basic")
    LoadUnitCollection("Germany","Basic")
    exit()
    # print("Equal - No Tanks")
    # attacker = LoadUnitCollection("Units_German.txt","./UnitProfiles_German.txt")
    # # attacker.printUnitsAndStrength("Attacker")
    # defender = LoadUnitCollection("Units_Russian.txt","./UnitProfiles_Russian.txt")
    # # defender.printUnitsAndStrength("Defender")
    # GenerateBattleStats(attacker,defender)

    # print("Equal - swapped")
    # GenerateBattleStats(defender,attacker)

    # print("German Tanks")
    # attacker = LoadUnitCollection("Units_German_Tanks.txt","./UnitProfiles_German.txt")
    # defender = LoadUnitCollection("Units_Russian.txt","./UnitProfiles_Russian.txt")
    # GenerateBattleStats(attacker,defender)

    # print("Tanks - swapped")
    # GenerateBattleStats(defender,attacker)

    print("Standard Equal")
    attacker = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Basic.txt")
    defender = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Basic.txt")
    GenerateBattleStats(attacker,defender)

    print("Standard - Tanks")
    attacker = LoadUnitCollection("Units_Basic_Tanks.txt","./UnitProfiles_Basic.txt")
    defender = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Basic.txt")
    GenerateBattleStats(attacker,defender)

    print("Standard - Tanks Swapped")
    GenerateBattleStats(defender,attacker)

    print("Standard - Fighters")
    attacker = LoadUnitCollection("Units_Basic_Fighters.txt","./UnitProfiles_Basic.txt")
    defender = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Basic.txt")
    GenerateBattleStats(attacker,defender)

    print("Standard - Fighters Swapped")
    GenerateBattleStats(defender,attacker)

    Unit.diceSize = 6
    print(Unit.diceSize)
    
    print("Equal - No Tanks")
    attacker = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Original.txt")
    defender = LoadUnitCollection("Units_Basic.txt","./UnitProfiles_Original.txt")
    GenerateBattleStats(attacker,defender)

    print("Equal - Tanks")
    attacker = LoadUnitCollection("Units_Basic_Tanks.txt","./UnitProfiles_Original.txt")
    GenerateBattleStats(attacker,defender)

    print("Equal - Tanks swapped")
    GenerateBattleStats(defender,attacker)