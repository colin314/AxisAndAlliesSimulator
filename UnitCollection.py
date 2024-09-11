import math
from Units import *
from itertools import cycle, filterfalse, count
from collections import Counter
from statistics import mean, median
import pandas as pd
from UnitsEnum import Units
from tabulate import tabulate
from Hit import Hit
from Resources import bcolors
from dyce import H

pd.set_option('future.no_silent_downcasting', True)

unitDict = {Units.Infantry: Infantry,
            Units.MechInfantry: MechInfantry,
            Units.Artillery: Artillery,
            Units.Tank: Tank,
            Units.AAA: AAA,
            Units.Fighter: Fighter,
            Units.TacticalBomber: TacticalBomber,
            Units.StratBomber: StratBomber,
            Units.Submarine: Submarine,
            Units.Destroyer: Destroyer,
            Units.Cruiser: Cruiser,
            Units.Battleship: Battleship,
            Units.Carrier: Carrier,
            Units.Transport: Transport,
            Units.InfArt: InfArt,
            Units.MechInfArt: MechInfArt,
            Units.TankTactBomber: TankTactBomber,
            Units.FighterTactBomber: FighterTactBomber,
            Units.DamagedBattleship: DamagedBattleship,
            }


class UnitCollection:
    def __init__(self, unitList: pd.Series, unitProfiles: pd.DataFrame):
        self._unitList = []
        self.unitStrengths = {}
        self.unitCosts = {}
        self._loadUnitStrengths(unitProfiles)
        self._loadUnits(unitList)

        self._makeComboUnits()
        self.defineLossPriority(
            [Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank,
                TankTactBomber, Submarine, Destroyer, Fighter, TacticalBomber, FighterTactBomber,
                StratBomber, Cruiser, Battleship, Carrier]
        )
        self._originalLossPriority = self._lossPriority.copy()
        self._originalUnitList = self._unitList.copy()
        unitCounter = Counter(type(obj) for obj in self._unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        self.oldTable = unitArr
        self.oldTableOriginal = unitArr.copy()
        # self._correctLossPriority()

    def _loadUnits(self, unitList: pd.Series):
        for index, row in unitList.items():
            # Convert the int index to a Unit enum value, then get the type from the dictionary
            unitType = unitDict[Units(index)]
            for i in range(row):
                newUnit = unitType(self.unitStrengths[unitType])
                newUnit.cost = self.unitCosts[unitType]
                self._unitList.append(newUnit)

    def _loadUnitStrengths(self, unitProfiles: pd.DataFrame):
        for index, row in unitProfiles.iterrows():
            unitType = unitDict[Units(index)]
            self.unitStrengths[unitType] = (row["Attack"], row["Defense"])
            self.unitCosts[unitType] = int(row["Cost"])

        for key, value in self.unitStrengths.items():
            if issubclass(key, ComboUnit):
                attStr, defStr = value
                att = tuple([int(x) for x in str.split(attStr, "^")])
                defense = tuple([int(x) for x in str.split(defStr, "^")])
                self.unitStrengths[key] = (att, defense)
            else:
                self.unitStrengths[key] = (int(value[0]), int(value[1]))

    def _correctLossPriority(self):
        for type in list(self._lossPriority):
            if not self._unitInstanceInList(type):
                self._lossPriority.remove(type)

    def _unitTypeInList(self, unitType):
        return any(type(unit) == unitType for unit in self._unitList)

    def _unitInstanceInList(self, unitType):
        return any(isinstance(unit, unitType) for unit in self._unitList)

    def _removeUnitType(self, unitType, removeCount=1):
        """Remove n units of the specified type from the unit list.
        Returns the number of units removed."""
        oldCount = len(self._unitList)
        self._unitList = list(
            filterfalse(
                lambda u, counter=count(): type(u) == unitType
                and next(counter) < removeCount,
                self._unitList,
            )
        )
        newCount = len(self._unitList)
        return oldCount - newCount

    def _removeUnitInstance(self, unitType, removeCount=1):
        """Remove n units of the specified instance from the unit list.
        Returns the number of units removed."""
        oldCount = len(self._unitList)
        self._unitList = list(
            filterfalse(
                lambda u, counter=count(): isinstance(u, unitType)
                and next(counter) < removeCount,
                self._unitList,
            )
        )
        newCount = len(self._unitList)
        return oldCount - newCount

    def _makeComboUnits(self):
        # Inf & Art
        while self._unitTypeInList(Infantry) and self._unitTypeInList(Artillery):
            if self._removeUnitType(Artillery) == 0:
                raise Exception(
                    "No artillery removed when it should have been")
            if self._removeUnitType(MechInfantry) == 1:
                self._unitList.append(MechInfArt(
                    self.unitStrengths[MechInfArt]))
                continue
            if self._removeUnitType(Infantry) == 1:
                self._unitList.append(InfArt(self.unitStrengths[InfArt]))
                continue
            raise Exception("No infantry removed when it should have been")
        while self._unitTypeInList(TacticalBomber) and (self._unitTypeInList(Fighter) or self._unitTypeInList(Tank)):
            if self._removeUnitType(TacticalBomber) == 0:
                raise Exception(
                    "No tactical bomber removed when it should have been")
            if self._removeUnitType(Fighter) == 1:
                self._unitList.append(FighterTactBomber(
                    self.unitStrengths[FighterTactBomber]))
                continue
            if self._removeUnitType(Tank) == 1:
                self._unitList.append(TankTactBomber(
                    self.unitStrengths[TankTactBomber]))
                continue
            raise Exception("No fighter/tank removed when it should have been")

    def __str__(self):
        collStr = "Units in collection: " + str(self.unitCount()) + "\n"
        unitCount = Counter(type(obj) for obj in self._unitList)
        for objType, objCount in unitCount.items():
            collStr += objType.__name__ + ": " + str(objCount) + "\n"
        return collStr + "\n"

    def PrintCollection(self):
        print(f"Unit Count: {self.unitCount()}")
        unitCounter = Counter(type(obj) for obj in self._unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        print(tabulate(unitArr, headers="firstrow", tablefmt="fancy_grid"))

    def PrintCollectionComparison(self):
        print(f"Unit Count: {self.unitCount()}")
        unitCounter = Counter(type(obj) for obj in self._unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        df1 = self._unitStrArrToDf(self.oldTable)
        df2 = self._unitStrArrToDf(unitArr)
        dfJoin = pd.concat([df1, df2], axis=1, join='outer')
        printArr = [["Unit", "Before", "After"]]
        df = dfJoin.infer_objects(copy=False).fillna(0).reset_index()
        df.Count = df.Count.astype(int)
        printArr.extend(df.values.tolist())
        print(tabulate(printArr, tablefmt="fancy_grid"))
        self.oldTable = unitArr

    def _unitStrArrToDf(self, arr):
        indexes = [x[0] for x in arr[1:]]
        headers = ["Count"]
        count = [x[1] for x in arr[1:]]
        df = pd.DataFrame(count, index=indexes, columns=headers)
        return df

# BUG: Battleships are combo units, but only a single unit
    def unitCount(self):
        return len(
            [u for u in self._unitList if not isinstance(u, ComboUnit)]
        ) + 2 * len([u for u in self._unitList if isinstance(u, ComboUnit)])

    def attack(self):
        hits = []
        for u in self._unitList:
            success = u.attack()
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def defend(self):
        hits = []
        for u in self._unitList:
            success = u.defend()
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def _generateHit(self, unit: CombatUnit, hitNumber):
        hits = []
        for i in range(hitNumber):
            hit = Hit(unit)
            # Air vs Sub
            if isinstance(unit, AirUnit) and self._unitInstanceInList(Destroyer):
                hit.Immune.remove(Submarine)
            hits.append(hit)
        return hits

    def defineLossPriority(self, unitTypeList):
        self._lossPriority = unitTypeList
        self._originalLossPriority = unitTypeList.copy()

    def takeLosses(self, hitList):
        leftOver = []
        hitList.sort()
        for hit in hitList:
            if len(self._unitList) == 0:
                break  # All units killed, no need to apply further hits
            for unitType in self._lossPriority:
                removed = 0
                if self._unitTypeInList(unitType) and hit.UnitTypeIsValidTarget(unitType):
                    removed = self._removeUnitType(unitType, 1)
                    if removed > 0 and issubclass(unitType, ComboUnit):
                        self._correctComboUnits(unitType)
                        self._makeComboUnits()
                if removed > 0:
                    break  # hit was applied, we can break out of the loop
            if removed == 0:
                # Hit wasn't applied (for whatever reason, likely a bug, or the unit list is empty)
                leftOver.append(hit)

        if len(leftOver) > 0:
            print(f"{bcolors.RED}ERROR: Units exist outside of the loss priority{
                  bcolors.ENDC}")
            print(leftOver)
            hitList = []  # just keep track of hits that couldn't be applied at all
            for hit in leftOver:
                if len(self._unitList) == 0:
                    break
                removedUnit = self._applyHit(hit)
                if removedUnit == None:
                    hitList.append(hit)
                if removedUnit != None and isinstance(removedUnit, ComboUnit):
                    self._correctComboUnits(type(removedUnit))
            if len(hitList) > 0:
                print(f"{bcolors.RED}ERROR: Some hits could not be applied{
                      bcolors.ENDC}")
                print(hitList)

    def _correctComboUnits(self, comboType):
        self._unitList.append(
            comboType.priority(self.unitStrengths[comboType.priority])
        )
        self._makeComboUnits()

    def _applyHit(self, hit: Hit):
        """Applies the hit with no regard for loss priority"""
        unit = next(
            (x for x in self._unitList if hit.UnitIsValidTarget(x)), None)
        if unit != None:
            self._unitList.remove(unit)
        return unit

    def reset(self):
        self._unitList = self._originalUnitList.copy()
        self._lossPriority = self._originalLossPriority.copy()
        self.oldTable = self.oldTableOriginal.copy()
        # self._correctLossPriority()

    def printUnitsAndStrength(self, label="Unit List"):
        for u in self._unitList:
            print(label)
            if isinstance(u, ComboUnit):
                print(type(u).__name__, u.attackVals, u.defenseVals)
            else:
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            print()

    def collectionCost(self):
        totalCost = 0
        for u in self._unitList:
            totalCost += u.cost
        return totalCost

    def expectedHits(self, attack=True):
        dice = [u.unitHitDie(attack) for u in self._unitList]
        return sum(dice).mean()

    def hitsPerIpc(self, attack=True):
        hits = self.expectedHits(attack)
        cost = self.collectionCost()
        return hits/cost * 10


if __name__ == "__main__":
    profileName = "Basic"
    unitListsFile = "unitLists.csv"
    listName = "Attacker"
    profile = pd.read_csv(
        f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
    unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
    units = UnitCollection(unitList[listName], profile)
    print(units.hitsPerIpc())
