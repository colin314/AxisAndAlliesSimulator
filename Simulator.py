from colorama import Style
from colorama import Back
from colorama import Fore
from colorama import init as colorama_init
import argparse
import os
from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median
from Resources import bcolors
import sys
from tabulate import tabulate
from UI_UnitSelector import GetUnitList, Combatant
unitListsFile = "unitLists.csv"
from UnitsEnum import Units

UnitUIMap = {
            "infantry":Units.Infantry,
            "mech_infantry": Units.MechInfantry,
            "artillery": Units.Artillery ,
            "armour": Units.Tank ,
            "fighter": Units.Fighter ,
            "tactical_bomber": Units.TacticalBomber ,
            "bomber": Units.StratBomber ,
            "aaGun": Units.AAA ,
            "conscript": Units.Conscript ,
            "cruiser": Units.Cruiser ,
            "battleship": Units.Battleship ,
            "submarine": Units.Submarine ,
            "destroyer": Units.Destroyer ,
            "carrier": Units.Carrier ,
            "battleship_hit": Units.DamagedBattleship ,
            "carrier_hit": Units.DamagedCarrier ,
            "transport": Units.Transport ,
}

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
        retreatThreshold=0,
        maxRounds=-1,
        printOutcome=False,
        printBattle=False,
    ):
        maxRounds = sys.maxsize if maxRounds < 0 else maxRounds
        self.attacker.reset()
        self.defender.reset()
        round = 0
        if printBattle:
            print(f"{bcolors.BOLD}{bcolors.GREEN}Battle Rounds{bcolors.ENDC}")
            print(u'\u2550' * 50)
        retreat = False
        while self.attacker.currHP() > 0 and self.defender.currHP() > 0 and not retreat and round < maxRounds:
            attackerHitCount, defenderHitCount = (0, 0)
            round += 1
            # First Strike Phase
            attackerHits = self.attacker.firstStrikeAttack(self.defender)
            defenderHits = self.defender.firstStrikeDefend(self.attacker)
            attackerHitCount += len(attackerHits)
            defenderHitCount += len(defenderHits)
            self.attacker.takeLosses(defenderHits)
            self.defender.takeLosses(attackerHits)

            # General Combat Phase
            attackerHits = self.attacker.attack()
            defenderHits = self.defender.defend()
            attackerHitCount += len(attackerHits)
            defenderHitCount += len(defenderHits)
            self.attacker.takeLosses(defenderHits)
            self.defender.takeLosses(attackerHits)

            retreat = self.attacker.currHP() <= retreatThreshold

            if printBattle:
                self.PrintBattleState(
                    round, self.attacker, self.defender, attackerHitCount, defenderHitCount)
                if not retreat and self.attacker.currHP() > 0 and self.defender.currHP() > 0:
                    userInput = input(
                        "Press Enter to continue, or type 'r' to retreat: ")
                    retreat = retreat if userInput == "" else True

        if printOutcome:
            self.PrintBattleOutcome()
        return (self.attacker.currHP(), self.defender.currHP())

    def SimulateBattleData(
        self,
        battleCount=1000,
        retreatThreshold=0,
        maxRounds=-1
    ):
        resultArr = []
        self.reset()
        for i in range(battleCount):
            (a, d) = self.SimulateBattle()
            attackerWon = 1 if a > d else 0
            tuvSwing = self.attacker.valueDelta() - self.defender.valueDelta()
            results = [attackerWon, a, d, tuvSwing]
            resultArr.append(results)
            self.attacker.reset()
            self.defender.reset()

        resultDf = pd.DataFrame(resultArr, columns=[
                                "Attacker Won", "Remainder Attacker", "Remainder Defender", "Average IPC Swing (Attacker)"])
        attackWinRate = resultDf["Attacker Won"].mean()
        defenderWinRate = 1 - attackWinRate
        victoryData = resultDf.groupby("Attacker Won").mean()

        resultArr = [
            attackWinRate,
            victoryData["Remainder Attacker"][1] if 1 in victoryData.index else 0,
            victoryData["Average IPC Swing (Attacker)"][1] if 1 in victoryData.index else 0,
            defenderWinRate,
            victoryData["Remainder Defender"][0] if 0 in victoryData.index else 0,
            victoryData["Average IPC Swing (Attacker)"][0] if 0 in victoryData.index else 0,
        ]
        attackerStats = self.attacker.GetCollectionStats(True)
        defenderStats = self.defender.GetCollectionStats(False)
        resultArr.extend([
            attackerStats["HP"],
            attackerStats["IPC / HP"],
            attackerStats["Expected Hits"],
            attackerStats["IPC / Hit"],
            attackerStats["endurance"],
            attackerStats["enduranceRatio"],
            attackerStats["lostValue"],
            attackerStats["Lost / Unit"],
        ])
        resultArr.extend([
            defenderStats["HP"],
            defenderStats["IPC / HP"],
            defenderStats["Expected Hits"],
            defenderStats["IPC / Hit"],
            defenderStats["endurance"],
            defenderStats["enduranceRatio"],
            defenderStats["lostValue"],
            defenderStats["Lost / Unit"],
        ])
        return resultArr

    def _getRoundStats(self, round: int, attackerExpectedHits: float, defenderExpectedHits: float, attackerHitCount: int, defenderHitCount: int):
        dataRow = [round,
                   self.attacker.currHP(), self.attacker.currCost(),
                   attackerExpectedHits, attackerHitCount,
                   self.defender.currHP(), self.defender.currCost(),
                   defenderExpectedHits, defenderHitCount]
        return dataRow

    def SimulateBattleWithStats(
        self,
        retreatThreshold=0,
        maxRounds=-1,
    ):
        maxRounds = sys.maxsize if maxRounds < 0 else maxRounds
        self.reset()
        round = 0
        headers = ["Attacker HP", "Attacker TUV", "Attacker Expected Hits", "Attacker Actual Hits",
                   "Defender HP", "Defender TUV", "Defender Expected Hits", "Defender Actual Hits"]
        roundStats = []
        attackerExpected = self.attacker.expectedHits(isAttack=True)
        defenderExpected = self.defender.expectedHits(isAttack=False)
        roundStats.append(self._getRoundStats(
            round, attackerExpected, defenderExpected, 0, 0))
        retreat = False
        while self.attacker.currHP() > 0 and self.defender.currHP() > 0 and not retreat and round < maxRounds:
            round += 1
            attackerHitCount = 0
            defenderHitCount = 0
            attackerExpected = self.attacker.expectedHits(isAttack=True)
            defenderExpected = self.defender.expectedHits(isAttack=False)

            # First Strike Phase
            attackerHits = self.attacker.firstStrikeAttack(self.defender)
            defenderHits = self.defender.firstStrikeDefend(self.attacker)
            attackerHitCount = len(attackerHits)
            defenderHitCount = len(defenderHits)
            self.attacker.takeLosses(defenderHits)
            self.defender.takeLosses(attackerHits)

            # General Combat Phase
            attackerHits = self.attacker.attack()
            defenderHits = self.defender.defend()
            attackerHitCount += len(attackerHits)
            defenderHitCount += len(defenderHits)
            self.attacker.takeLosses(defenderHits)
            self.defender.takeLosses(attackerHits)

            roundStats.append(self._getRoundStats(
                round, attackerExpected, defenderExpected, attackerHitCount, defenderHitCount))

            retreat = self.attacker.currHP() <= retreatThreshold

        return roundStats

    def PrintBattleState(self, round, attacker: UnitCollection, defender: UnitCollection, aH, dH):
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

    def PrintBattleOutcome(self):
        if self.defender.currHP() == 0 and self.attacker.currHP() > 0:
            print(f"Outcome: {Fmt.attHead}Attacker victory{Style.RESET_ALL}")
        else:
            print(f"Outcome: {Fmt.defHead}Defender Victory{Style.RESET_ALL}")

        ipcSwing = self.attacker.valueDelta() - self.defender.valueDelta()
        print(f"{Fore.LIGHTMAGENTA_EX}IPC Swing (Attacker):{
              Style.RESET_ALL} {ipcSwing}\n")

    def LoadUnitCollection(listName, profileName):
        profile = pd.read_csv(
            f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
        unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")

        units = UnitCollection(unitList[["Key", listName]], profile)
        return units

    def LoadUnitCollectionFromUI(combatant:Combatant, profileName):
        headers = ["Key", "ListName"]
        unitList = combatant.units
        units = [[UnitUIMap[unit].value, val] for unit,val in unitList.items()]
        unitList = pd.DataFrame(units, columns=headers)
        profile = pd.read_csv(f'UnitProfiles_{profileName}.csv', encoding="utf-8", delimiter=",")
        units = UnitCollection(unitList, profile, combatant.power)
        return units


    def LoadAttacker(self, listName, profileName):
        self.attacker = Simulator.LoadUnitCollection(listName, profileName)

    def LoadDefender(self, listName, profileName):
        self.defender = Simulator.LoadUnitCollection(listName, profileName)

    def reset(self):
        self.attacker.reset()
        self.defender.reset()

    def GenerateBattleStats(self, battleCount=10000):
        resultArr = []
        self.reset()
        for i in range(battleCount):
            (a, d) = self.SimulateBattle()
            attackerWon = 1 if a > d else 0
            tuvSwing = self.attacker.valueDelta() - self.defender.valueDelta()
            results = [attackerWon, a, d, tuvSwing]
            resultArr.append(results)
            self.attacker.reset()
            self.defender.reset()
        resultDf = pd.DataFrame(resultArr, columns=[
                                "Attacker Won", "Remainder Attacker", "Remainder Defender", "Average IPC Swing (Attacker)"])
        attackWinRate = resultDf["Attacker Won"].mean()
        print(f"Attacker wins {Fore.RED}{attackWinRate:2.2%}{
              Style.RESET_ALL} percent of the time.")
        victoryData = resultDf.groupby("Attacker Won").mean()
        # victoryData = victoryData.set_axis(
        #     ["Defender Won", "Attacker Won"], axis='index')
        victoryData["Units Remaining"] = victoryData[[
            "Remainder Attacker", "Remainder Defender"]].max(axis=1)
        victoryData = victoryData[[
            "Units Remaining", "Average IPC Swing (Attacker)"]]
        print(tabulate(victoryData, headers="keys", tablefmt="fancy_grid"))
        print()

    def GenerateExtendedBattleStats(self, battleCount=2000):
        resultArr = []
        self.reset()
        roundStats = []
        for i in range(battleCount):
            runStats = self.SimulateBattleWithStats()
            maxRound = len(runStats) - 1
            for i in runStats:
                i.append(maxRound)
            roundStats.extend(runStats)
            a = self.attacker.currHP()
            d = self.defender.currHP()
            attackerWon = 1 if a > d else 0
            tuvSwing = self.attacker.valueDelta() - self.defender.valueDelta()
            results = [attackerWon, a, d, tuvSwing]
            resultArr.append(results)
        headers = ["Round",
                   "Attacker HP", "Attacker TUV", "Attacker Expected Hits", "Attacker Actual Hits",
                   "Defender HP", "Defender TUV", "Defender Expected Hits", "Defender Actual Hits",
                   "Max Rounds"]
        roundsDf = pd.DataFrame(roundStats, columns=headers)
        # Granular Analysis
        groupedDf = roundsDf.groupby(["Max Rounds", "Round"]).aggregate({
            'Round': 'size',
            'Attacker HP': 'mean',
            'Attacker TUV': 'mean',
            'Attacker Expected Hits': 'mean',
            'Attacker Actual Hits': 'mean',
            'Defender HP': 'mean',
            'Defender TUV': 'mean',
            'Defender Expected Hits': 'mean',
            'Defender Actual Hits': 'mean',
        })
        groupedDf.rename(columns={"Round": "Count"}, inplace=True)
        groupedDf.reset_index()
        groupedDf.to_csv("tmp.csv", sep="\t")

        # Group by round
        groupedDf = roundsDf.groupby(["Round"]).aggregate({
            'Round': 'size',
            'Attacker HP': 'mean',
            'Attacker TUV': 'mean',
            'Attacker Expected Hits': 'mean',
            'Attacker Actual Hits': 'mean',
            'Defender HP': 'mean',
            'Defender TUV': 'mean',
            'Defender Expected Hits': 'mean',
            'Defender Actual Hits': 'mean',
        })
        groupedDf.rename(columns={"Round": "Count"}, inplace=True)
        groupedDf.reset_index()
        groupedDf.to_csv("tmp2.csv", sep="\t")
        # }).reset_index(level=0, drop=True)
        # groupedDf.rename(columns={"Round": "Count"}, inplace=True)
        # print(groupedDf)
        # groupedDf.index.name = "Round"
        # print(groupedDf)

        # resultDf = pd.DataFrame(resultArr, columns=[
        #                         "Attacker Won", "Remainder Attacker", "Remainder Defender", "Average IPC Swing (Attacker)"])
        # attackWinRate = resultDf["Attacker Won"].mean()
        # print(f"Attacker wins {Fore.RED}{attackWinRate:2.2%}{
        #       Style.RESET_ALL} percent of the time.")
        # victoryData = resultDf.groupby("Attacker Won").mean()
        # victoryData = victoryData.set_axis(
        #     ["Defender Won", "Attacker Won"], axis='index')
        # victoryData["Units Remaining"] = victoryData[[
        #     "Remainder Attacker", "Remainder Defender"]].max(axis=1)
        # victoryData = victoryData[[
        #     "Units Remaining", "Average IPC Swing (Attacker)"]]
        # print(tabulate(victoryData, headers="keys", tablefmt="fancy_grid"))
        # print()
        # self.reset()

    def swapPlaces(attacker, defender):
        return (defender, attacker)

    def simulateBattleWithStats(self,
                                at_lossProfile=UnitCollection.defaultLossPriority,
                                df_lossProfile=UnitCollection.defaultLossPriority,
                                simCount=1000):
        Unit.diceSize = 12
        # self.LoadAttacker(at, at_profile)
        # self.LoadDefender(df, df_profile)
        self.attacker.defineLossPriority(at_lossProfile)
        self.defender.defineLossPriority(df_lossProfile)

        self.SimulateBattle(printBattle=True, printOutcome=True)

        print(f"{Fmt.genHead}Statistics{Style.RESET_ALL}\n")
        self.GenerateBattleStats(simCount)


class Inputs:
    pass

def RunSingSimulation():
    # os.system('cls')
    parser = argparse.ArgumentParser()
    inputs = Inputs()
    parser.add_argument('attacker')
    parser.add_argument('attProfile')
    parser.add_argument('defender')
    parser.add_argument('defProfile')
    parser.parse_args(namespace=inputs)

    sim = Simulator()
    sim.LoadAttacker(inputs.attacker, inputs.attProfile)
    sim.LoadDefender(inputs.defender, inputs.defProfile)

    print(sim.defender.expectedHits(isAttack=False))
    input("Waiting...")

    sim.SimulateBattle(printBattle=True, printOutcome=True)


if __name__ == "__main__":
    lists = GetUnitList(False)
    attacker = Simulator.LoadUnitCollectionFromUI(lists["attacker"], "Basic")
    defender = Simulator.LoadUnitCollectionFromUI(lists["defender"], "Basic")
    sim = Simulator()
    sim.attacker = attacker
    sim.defender = defender
    attacker.PrintCollection()
    sim.SimulateBattle(printBattle=True, printOutcome=True)

