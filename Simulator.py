import os
from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median
from Resources import bcolors
import sys
from tabulate import tabulate
unitListsFile = "unitLists.csv"
from colorama import init as colorama_init
from colorama import Fore
from colorama import Back
from colorama import Style

class Fmt:
    attHead = f"{Back.RED}{Style.BRIGHT}{Fore.WHITE}"
    tmp = f"{Back.RED}{Fore.WHITE}"
    defHead = f"{Back.BLUE}{Style.BRIGHT}{Fore.WHITE}"
    att = f"{Fore.LIGHTRED_EX}"
    df = f"{Fore.LIGHTBLUE_EX}"
    genHead = f"{Back.WHITE}{Fore.BLACK}"
    Attacker = f"{att}Attacker{Style.RESET_ALL}"
    Defender = f"{df}Defender{Style.RESET_ALL}"
    AttackerHead = f"{attHead}Attacker{Style.RESET_ALL}"
    DefenderHead = f"{defHead}Defender{Style.RESET_ALL}"

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
        attacker.reset()
        defender.reset()
        round = 0
        if printBattle:
            print(f"{bcolors.BOLD}{bcolors.GREEN}Battle Rounds{bcolors.ENDC}")
            print(u'\u2550' * 50)
        retreat = False
        while attacker.currHP() > 0 and defender.currHP() > 0 and not retreat and round < maxRounds:
            attackerHitCount, defenderHitCount = (0, 0)
            round += 1
            # First Strike Phase
            attackerHits = attacker.firstStrikeAttack(defender)
            defenderHits = defender.firstStrikeDefend(attacker)
            attackerHitCount += len(attackerHits)
            defenderHitCount += len(defenderHits)
            attacker.takeLosses(defenderHits)
            defender.takeLosses(attackerHits)

            # General Combat Phase
            attackerHits = attacker.attack()
            defenderHits = defender.defend()
            attackerHitCount += len(attackerHits)
            defenderHitCount += len(defenderHits)
            attacker.takeLosses(defenderHits)
            defender.takeLosses(attackerHits)

            retreat = attacker.currHP() <= retreatThreshold

            if printBattle and not retreat and attacker.currHP() > 0 and defender.currHP() > 0:
                self.PrintBattleState(
                    round, attacker, defender, attackerHitCount, defenderHitCount)
                userInput = input("Press Enter to continue, or type 'r' to retreat: ")
                retreat = retreat if userInput == "" else True

        if printOutcome:
            self.PrintBattleOutcome(attacker, defender)
        return (attacker.currHP(), defender.currHP())

    def PrintBattleState(self, round, attacker:UnitCollection, defender:UnitCollection, aH, dH):
        os.system('cls')
        print(f"Round {bcolors.RED}{round}{bcolors.ENDC}")
        print(u'\u2500' * 40)
        print(f"{Fmt.Attacker} Hits: {aH}")
        print(f"{Fmt.Defender} Hits: {dH}\n")
        print(f"{Fmt.AttackerHead} HP: {attacker.currHP()}")
        attacker.PrintCollectionComparison()
        print()
        print(f"{Fmt.DefenderHead} HP: {defender.currHP()}")
        defender.PrintCollectionComparison()
        print()

    def PrintBattleOutcome(self, attacker: UnitCollection, defender: UnitCollection):
        os.system('cls')
        print()
        if defender.currHP() == 0 and attacker.currHP() > 0:
            print(f"Outcome: {Fmt.attHead}Attacker victory{Style.RESET_ALL}\n")
        else:
            print(f"Outcome: {Fmt.defHead}Defender Victory{Style.RESET_ALL}\n")

        print(f"{Fmt.att}Attacking{Style.RESET_ALL} Units Remaining: {attacker.unitCount()}")
        if attacker.currHP() > 0:
            attacker.PrintGranularCollection()
        print()

        print(f"{Fmt.df}Defending{Style.RESET_ALL} Units Remaining: {defender.unitCount()}")
        if defender.currHP() > 0:
            defender.PrintGranularCollection()
        print()

        ipcSwing = attacker.valueDelta() - defender.valueDelta()
        print(f"{Fore.LIGHTMAGENTA_EX}IPC Swing (Attacker):{Style.RESET_ALL} {ipcSwing}\n")

    def LoadUnitCollection(self, listName, profileName):
        profile = pd.read_csv(
            f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
        unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
        units = UnitCollection(unitList[listName], profile)
        return units

    def GenerateBattleStats(self, attacker: UnitCollection, defender: UnitCollection, battleCount=10000):
        resultArr = []
        attacker.reset()
        defender.reset()
        for i in range(battleCount):
            (a, d) = self.SimulateBattle(attacker, defender)
            attackerWon = 1 if a > d else 0
            tuvSwing = attacker.valueDelta() - defender.valueDelta()
            results = [attackerWon, a, d, tuvSwing]
            resultArr.append(results)
            attacker.reset()
            defender.reset()
        resultDf = pd.DataFrame(resultArr, columns=[
                                "Attacker Won", "Remainder Attacker", "Remainder Defender", "Average IPC Swing (Attacker)"])
        attackWinRate = resultDf["Attacker Won"].mean()
        print(f"Attacker wins {Fore.RED}{attackWinRate:2.2%}{Style.RESET_ALL} percent of the time.")
        victoryData = resultDf.groupby("Attacker Won").mean()
        victoryData = victoryData.set_axis(
            ["Defender Won", "Attacker Won"], axis='index')
        victoryData["Units Remaining"] = victoryData[[
            "Remainder Attacker", "Remainder Defender"]].max(axis=1)

        victoryData = victoryData[[
            "Units Remaining", "Average IPC Swing (Attacker)"]]
        print(tabulate(victoryData, headers="keys", tablefmt="fancy_grid"))
        # print(tabulate(resultDf.groupby("Attacker Won").mean().index.tolist(), tablefmt="fancy_grid"))
        print()
        attacker.reset()
        defender.reset()

    def swapPlaces(attacker, defender):
        return (defender, attacker)

    def simulateBattleWithStats(self, at, df, at_profile="Basic", df_profile="Basic",
                                at_lossProfile=UnitCollection.defaultLossPriority,
                                df_lossProfile=UnitCollection.defaultLossPriority,
                                simCount=1000):
        Unit.diceSize = 12
        attacker = self.LoadUnitCollection(at, at_profile)
        defender = self.LoadUnitCollection(df, df_profile)
        attacker.defineLossPriority(at_lossProfile)
        defender.defineLossPriority(df_lossProfile)

        self.SimulateBattle(attacker, defender, printBattle=True, printOutcome=True)

        print(f"{Fmt.genHead}Statistics{Style.RESET_ALL}\n")
        self.GenerateBattleStats(attacker, defender, simCount)

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


def testBattle(sim: Simulator, attacker, defender):
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
    attackerLossPriority = [AAA, Battleship, Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank,
                            TankTactBomber, Submarine, Destroyer, Fighter, TacticalBomber, FighterTactBomber,
                            StratBomber, Cruiser, DamagedBattleship, Carrier]
    defenderLossPriority = [AAA, Battleship, Infantry, MechInfantry, InfArt, MechInfArt, Artillery,
                            Tank, Submarine, Destroyer, TacticalBomber, Fighter,
                            FighterTactBomber, StratBomber, Cruiser, DamagedBattleship, Carrier]
    russianLossPriority = [AAA, Battleship, Infantry, MechInfantry, InfArt, Artillery, MechInfArt,
                           Tank, Submarine, Destroyer, TacticalBomber, Fighter,
                           FighterTactBomber, StratBomber, Cruiser, DamagedBattleship, Carrier]

    # Russia on defense
    # attacker = sim.LoadUnitCollection("Attacker", "Basic2")
    # defender = sim.LoadUnitCollection("Defender", "Basic2")
    sim.simulateBattleWithStats("Attacker", "Defender")
    # battleStats(sim, "Attacker", "Defender", "Basic", "Basic", attackerLossPriority, defenderLossPriority)
    # print("Basic 2.0")
    # battleStats(sim, "Attacker", "Defender", "Basic2", "Basic2", attackerLossPriority, defenderLossPriority)
    # Unit.diceSize = 6
    # print("Original")
    # battleStats(sim, "Attacker", "Defender", "Original", "Original", attackerLossPriority, defenderLossPriority)
    # # Russia on attack
    # battleStats(sim, "RussianAttack", "Defender", "Russian", "Basic", russianLossPriority, defenderLossPriority)
    # exit()
