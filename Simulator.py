from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median
from Resources import bcolors
import sys

unitListsFile = "unitLists.csv"


class Simulator:

    def SimulateBattle(
        self,
        attacker: UnitCollection,
        defender: UnitCollection,
        retreatThreshold=0,
        maxRounds=-1,
        printOutcome=False,
        printBattle=False,
    ):
        maxRounds = sys.maxsize if maxRounds < 0 else maxRounds
        round = 0
        if printBattle:
            print(f"{bcolors.BOLD}{bcolors.GREEN}Battle Rounds{bcolors.ENDC}")
            print(u'\u2550' * 50)
        while attacker.unitCount() > 0 and defender.unitCount() > 0 and attacker.unitCount() > retreatThreshold and round < maxRounds:
            round += 1
            attackerHits = attacker.attack()
            defenderHits = defender.defend()
            attacker.takeLosses(defenderHits)
            defender.takeLosses(attackerHits)
            if printBattle:
                self.PrintBattleState(
                    round, attacker, defender, attackerHits, defenderHits)
                input("Press Enter to continue...")
        if printOutcome:
            self.PrintCombatants(attacker, defender)
        return (attacker.unitCount(), defender.unitCount())

    def PrintBattleState(self, round, attacker, defender, aH, dH):
        print(f"Round {bcolors.RED}{round}{bcolors.ENDC}")
        print(u'\u2500' * 40)
        print(f"Attacker Hits: {len(aH)}")
        print(f"Defender Hits: {len(dH)}")
        print("Attacker: ")
        attacker.PrintCollectionComparison()
        print("Defender: ")
        defender.PrintCollectionComparison()
        print("\n")

    def PrintCombatants(self, attacker: UnitCollection, defender: UnitCollection):
        print("Attacker: ")
        attacker.PrintCollection()
        print("Defender: ")
        defender.PrintCollection()
        print("\n")

    def LoadUnitCollection(self, listName, profileName):
        profile = pd.read_csv(
            f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
        unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
        units = UnitCollection(unitList[listName], profile)
        return units

    def GenerateBattleStats(self, attacker, defender, battleCount=10000):
        results = []
        unitsLeft = []
        for i in range(battleCount):
            (a, d) = self.SimulateBattle(attacker, defender)
            results.append(1 if a > d else 0)
            unitsLeft.append([a, d])
            attacker.reset()
            defender.reset()
        attackWinRate = float(sum(results)) / float(len(results))
        print(f"attacker wins \033[91m{
              attackWinRate:2.2%}\033[97m percent of the time\033[0m")
        attackingUnitsLeft = mean([x[0] for x in unitsLeft if x[0] > 0])
        defendingUnitsLeft = mean([x[1] for x in unitsLeft if x[1] > 0])
        print(f"Attacking units left if attacker won: {
              attackingUnitsLeft:.2f}")
        print(f"Defending units left if defender won: {
              defendingUnitsLeft:.2f}")
        print(f"Attacking units left on average: {
              mean([x[0] for x in unitsLeft]):.2f}")
        print(f"Defending units left on average: {
              mean([x[1] for x in unitsLeft]):.2f}")
        print()

    def swapPlaces(attacker, defender):
        return (defender, attacker)


if __name__ == "__main__":
    sim = Simulator()
    attacker = sim.LoadUnitCollection("Attacker", "Basic")
    defender = sim.LoadUnitCollection("Defender", "Basic")
    defender.defineLossPriority([Infantry, MechInfantry, Artillery, InfArt, MechInfArt,
                                Tank, Submarine, Destroyer, Fighter, Bomber, Cruiser, Battleship, Carrier])
    sim.SimulateBattle(attacker, defender, retreatThreshold=0,
                       maxRounds=-1, printBattle=True)

    # Unit.diceSize = 6
    # print("Equal - Original")
    # attacker = sim.LoadUnitCollection("Germany", "Original")
    # defender = sim.LoadUnitCollection("Russia", "Original")
    # defender.defineLossPriority([Infantry, MechInfantry, Artillery, InfArt, MechInfArt,
    #                             Tank, Submarine, Destroyer, Fighter, Bomber, Cruiser, Battleship, Carrier])
    # attacker.reset()
    # defender.reset()
    # sim.SimulateBattle(attacker, defender, printBattle=True)
