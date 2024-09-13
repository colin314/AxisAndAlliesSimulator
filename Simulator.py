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
        while attacker.collectionHP() > 0 and defender.collectionHP() > 0 and attacker.collectionHP() > retreatThreshold and round < maxRounds:
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
        return (attacker.collectionHP(), defender.collectionHP())

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
        print(f"attacker wins \033[91m{attackWinRate:2.2%}\033[97m percent of the time\033[0m")
        attArr = [x[0] for x in unitsLeft if x[0] > 0]
        defArr = [x[1] for x in unitsLeft if x[1] > 0]
        attackingUnitsLeft = mean(attArr) if len(attArr) > 0 else 0
        defendingUnitsLeft = mean(defArr) if len(defArr) > 0 else 0
        print(f"Attacking units left if attacker won: {attackingUnitsLeft:.2f}")
        print(f"Defending units left if defender won: {defendingUnitsLeft:.2f}")
        print(f"Attacking units left on average: {mean([x[0] for x in unitsLeft]):.2f}")
        print(f"Defending units left on average: {mean([x[1] for x in unitsLeft]):.2f}")
        print()

    def swapPlaces(attacker, defender):
        return (defender, attacker)

def battleStats(sim:Simulator, at, df, at_profile, df_profile,  at_lossProfile, df_lossProfile, simCount = 5000):
    Unit.diceSize = 12
    attacker = sim.LoadUnitCollection(at, at_profile)
    defender = sim.LoadUnitCollection(df, df_profile)
    attacker.defineLossPriority(at_lossProfile)
    defender.defineLossPriority(df_lossProfile)

    def resetSides():
        attacker.reset()
        defender.reset()

    # sim.SimulateBattle(attacker, defender, printBattle=True)
    resetSides()
    sim.GenerateBattleStats(attacker, defender, simCount)

    # Unit.diceSize = 6
    # try:
    #     attacker = sim.LoadUnitCollection("AttackerOriginal", "Original")
    #     defender = sim.LoadUnitCollection("DefenderOriginal", "Original")
    #     defender.defineLossPriority([AAA,Battleship,Infantry, MechInfantry, Artillery, InfArt, MechInfArt,
    #                                 Tank, Submarine, Destroyer, TacticalBomber, Fighter,
    #                                 FighterTactBomber, StratBomber, Cruiser, DamagedBattleship, Carrier])
    #     sim.GenerateBattleStats(attacker, defender, simCount)
    # except:
    #     pass
    # Unit.diceSize = 12

def testBattle(sim:Simulator, attacker, defender):
    attacker.reset()
    defender.reset()
    sim.SimulateBattle(attacker, defender, printBattle=True)
    attacker.reset()
    defender.reset()
    sim.GenerateBattleStats(attacker, defender, 5000)
    attacker.reset()
    defender.reset()

if __name__ == "__main__":
    sim = Simulator()
    attackerLossPriority = [AAA,Battleship, Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank,
            TankTactBomber, Submarine, Destroyer, Fighter, TacticalBomber, FighterTactBomber,
            StratBomber, Cruiser, DamagedBattleship, Carrier]
    defenderLossPriority = [AAA,Battleship, Infantry, MechInfantry, InfArt, MechInfArt, Artillery,
                                Tank, Submarine, Destroyer, TacticalBomber, Fighter,
                                FighterTactBomber, StratBomber, Cruiser, DamagedBattleship, Carrier]
    russianLossPriority = [AAA,Battleship, Infantry, MechInfantry, InfArt, Artillery, MechInfArt,
                                Tank, Submarine, Destroyer, TacticalBomber, Fighter,
                                FighterTactBomber, StratBomber, Cruiser, DamagedBattleship, Carrier]

    # Russia on defense
    print("Basic")
    sim.SimulateBattle(sim.LoadUnitCollection("Attacker", "Basic2"), sim.LoadUnitCollection("Defender","Basic2"),printOutcome=True)
    # battleStats(sim, "Attacker", "Defender", "Basic", "Basic", attackerLossPriority, defenderLossPriority)
    # print("Basic 2.0")
    # battleStats(sim, "Attacker", "Defender", "Basic2", "Basic2", attackerLossPriority, defenderLossPriority)
    # Unit.diceSize = 6
    # print("Original")
    # battleStats(sim, "Attacker", "Defender", "Original", "Original", attackerLossPriority, defenderLossPriority)
    # # Russia on attack
    # battleStats(sim, "RussianAttack", "Defender", "Russian", "Basic", russianLossPriority, defenderLossPriority)
    # exit()

