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
import json
from matplotlib import pyplot as plt

# This is just to keep pandas from complaining
pd.set_option('future.no_silent_downcasting', True)

# This dictionary defines the mapping between the unit type enum
# and specific unit types.
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
            Units.DamagedCarrier: DamagedCarrier
            }

defaultLossPriority = [AAA, Battleship, Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank,
                       TankTactBomber, Submarine, Destroyer, Fighter, TacticalBomber, FighterTactBomber,
                       StratBomber, Cruiser, DamagedBattleship, Carrier]

comboSeparator = "^"


class UnitCollection:
    """A group of units that will attack or defend together."""

# region Initialization functions
    def __init__(self, unitList: pd.Series, unitProfiles: pd.DataFrame):
        self._unitList = []
        self.unitStrengths = {}
        self.unitCosts = {}

        # Call initialization functions (load units, etc.)
        self._loadUnitStrengths(unitProfiles)
        self._loadUnits(unitList)
        self._makeComboUnits()
        self.defineLossPriority(defaultLossPriority)

        # Record original collection state to support resets
        self.originalCost = self.currCost()
        self._originalLossPriority = self._lossPriority.copy()
        self._originalUnitList = self._unitList.copy()
        unitCounter = Counter(type(obj) for obj in self._unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        self.oldTable = unitArr
        self.oldTableOriginal = unitArr.copy()

    def _loadUnitStrengths(self, unitProfiles: pd.DataFrame):
        """Use the given profile to define the combat strengths of each unit type."""
        for index, row in unitProfiles.iterrows():
            # It's critical that the index values of the data frame match the int value in the Units enum
            # Load the unit's strength
            unitType = unitDict[Units(index)]
            strengths = []
            for vals in (row["Attack"], row["Defense"]):
                strengthVals = [int(x) for x in str.split(vals,comboSeparator)]
                strengths.append(strengthVals)
            strengthTup = tuple(strengths)
            # Leaving this horrid nested list comprehension for posterity
            # strengthTup = tuple([[int(x) for x in str.split(vals,comboSeparator)] for vals in (
            #     row["Attack"], row["Defense"])])
            self.unitStrengths[unitType] = strengthTup

            # Load the unit's cost
            self.unitCosts[unitType] = int(row["Cost"])

    def _loadUnits(self, unitList: pd.Series):
        """Use the given unit series to populate the collection with units."""
        for index, row in unitList.items():
            # Convert the int index to a Unit enum value, then get the type from the dictionary
            unitType = unitDict[Units(index)]
            for i in range(row):
                self._addUnit(unitType)

# endregion

# region Private helper functions
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

    def _addUnit(self, unitType):
        unit = unitType(self.unitStrengths[unitType])
        unit.cost = self.unitCosts[unitType]
        self._unitList.append(unit)

    def _makeComboUnits(self):
        # Inf & Art
        while self._unitTypeInList(Infantry) and self._unitTypeInList(Artillery):
            if self._removeUnitType(Artillery) == 0:
                raise Exception(
                    "No artillery removed when it should have been")
            if self._removeUnitType(MechInfantry) == 1:
                self._addUnit(MechInfArt)
                continue
            if self._removeUnitType(Infantry) == 1:
                self._addUnit(InfArt)
                continue
            raise Exception("No infantry removed when it should have been")
        while self._unitTypeInList(TacticalBomber) and (self._unitTypeInList(Fighter) or self._unitTypeInList(Tank)):
            if self._removeUnitType(TacticalBomber) == 0:
                raise Exception(
                    "No tactical bomber removed when it should have been")
            if self._removeUnitType(Fighter) == 1:
                self._addUnit(FighterTactBomber)
                continue
            if self._removeUnitType(Tank) == 1:
                self._addUnit(TankTactBomber)
                continue
            raise Exception("No fighter/tank removed when it should have been")
# endregion

# region Magic methods

    def __str__(self):
        collStr = "Units in collection: " + str(self.currHP()) + "\n"
        unitCount = Counter(type(obj) for obj in self._unitList)
        for objType, objCount in unitCount.items():
            collStr += objType.__name__ + ": " + str(objCount) + "\n"
        return collStr + "\n"

# endregion

# region Collection modification functions

    def reset(self):
        self._unitList = self._originalUnitList.copy()
        self._lossPriority = self._originalLossPriority.copy()
        self.oldTable = self.oldTableOriginal.copy()

    def defineLossPriority(self, unitTypeList):
        self._lossPriority = unitTypeList
        self._originalLossPriority = unitTypeList.copy()

# endregion

# region Printing Functions

    def PrintCollection(self):
        print(f"Unit Count: {self.currHP()}")
        unitCounter = Counter(type(obj) for obj in self._unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        print(tabulate(unitArr, headers="firstrow", tablefmt="fancy_grid"))

    def PrintCollectionComparison(self):
        print(f"Unit Count: {self.currHP()}")
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

    def printUnitsAndStrength(self, label="Unit List"):
        for u in self._unitList:
            print(label)
            if isinstance(u, ComboUnit):
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            else:
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            print()

    def PrintCollectionStats(self, label: str, attack=True):
        print(label)
        genStats = {
            "HP": self.currHP(),
            "Total Cost": self.currCost(),
            "Expected Hits": self.expectedHits(attack),
            "IPC / Hit": self.currCost() / self.expectedHits(attack)
        }
        print(json.dumps(genStats, indent=4))
        stats = self.collectionEndurance(attack)
        print(json.dumps(stats, indent=4))
        self.PrintCollection()
        print()

# endregion

# region Collection stats functions

    def currHP(self):
        return len(
            [u for u in self._unitList if not isinstance(u, ComboUnit)]
        ) + 2 * len([u for u in self._unitList if isinstance(u, ComboUnit)])

    def currCost(self):
        totalCost = 0
        for u in self._unitList:
            totalCost += u.cost
        return totalCost

    def expectedHits(self, attack=True):
        if len(self._unitList) > 0:
            dice = [u.unitHitDie(attack) for u in self._unitList]
            return sum(dice).mean()
        else:
            return H({0: 12})

    def hitsPerIpc(self, attack=True):
        hits = self.expectedHits(attack)
        cost = self.currCost()
        return hits/cost * 10

    def collectionEndurance(self, attack=True):
        startingStrength = self.expectedHits(attack)
        startingUnitCount = self.currHP()
        startingCost = self.currCost()
        halfStrength = 0.5 * startingStrength
        currStrength = startingStrength
        placeholderUnit = CombatUnit((0, 0))
        while len(self._unitList) > 0 and currStrength > halfStrength:
            self.takeLosses([Hit(placeholderUnit)])
            currStrength = self.expectedHits(attack)
        endurance = startingUnitCount - self.currHP()
        enduranceRatio = (float(endurance) / startingUnitCount)
        remainingValue = self.currCost()
        lostValue = startingCost - remainingValue
        relLostValue = float(lostValue) / startingCost
        costPerLostUnit = float(lostValue) / endurance
        rv = {
            "endurance": endurance,
            "enduranceRatio": f"{enduranceRatio:.1%}",
            "remainingUnits": len(self._unitList),
            "lostValue": lostValue,
            "remainingValue": remainingValue,
            "% Value Lost": f"{relLostValue:.1%}",
            "Lost / Unit": f"{costPerLostUnit:.2f}"
        }
        self.reset()
        return rv

    def generateHitCurve(self, isAttack=True):
        placeholderUnit = CombatUnit((0,0))
        curveList = []
        while len(self._unitList) > 0:
            curveList.append([self.currHP(), self.expectedHits(isAttack)])
            self.takeLosses([Hit(placeholderUnit)])
        df = pd.DataFrame(curveList, columns=["HP", "Expected Hits"])
        plt.plot(df["HP"], df["Expected Hits"])
        plt.show()

    def valueDelta(self):
        return self.currCost() - self.originalCost


# endregion

# region Combat functions

    def attack(self):
        hits = []
        for u in self._unitList:
            success = u.attack()
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits
    
    def firstStrikeAttack(self, opponent):
        hits = []
        for u in [x for x in self._unitList if isinstance(x, FirstStrikeUnit)]:
            success = u._firstStrikeAttack(opponent)
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

    def firstStrikeDefend(self, opponent):
        hits = []
        for u in [x for x in self._unitList if isinstance(x, FirstStrikeUnit)]:
            success = u._firstStrikeDefense(opponent)
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
        self._addUnit(comboType.priority)
        self._makeComboUnits()

    def _applyHit(self, hit: Hit):
        """Applies the hit with no regard for loss priority"""
        unit = next(
            (x for x in self._unitList if hit.UnitIsValidTarget(x)), None)
        if unit != None:
            self._unitList.remove(unit)
        return unit

# endregion


if __name__ == "__main__":
    Unit.diceSize = 12
    profileName = "Basic2"
    unitListsFile = "unitLists.csv"
    listName = "Attacker"
    profile = pd.read_csv(
        f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
    unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
    units = UnitCollection(unitList[listName], profile)
    units.PrintCollectionStats("Attacker", attack=True)
    # units.generateHitCurve()

    # profileName = "Basic2"
    # unitListsFile = "unitLists.csv"
    # listName = "Defender"
    # profile = pd.read_csv(
    #     f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
    # unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
    # units = UnitCollection(unitList[listName], profile)
    # units.PrintCollectionStats("Defender", attack=False)
