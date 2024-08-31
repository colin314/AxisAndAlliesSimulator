from Units import *
from itertools import filterfalse, count
from collections import Counter
from statistics import mean, median
import pandas as pd
from UnitsEnum import Units

unitDict = {Units.Infantry:Infantry,
Units.MechInfantry:MechInfantry,
Units.Artillery:Artillery,
Units.Tank:Tank,
Units.Fighter:Fighter,
Units.TacticalBomber:TacticalBomber,
Units.StratBomber:StratBomber,
Units.Submarine:Submarine,
Units.Destroyer:Destroyer,
Units.Cruiser:Cruiser,
Units.Battleship:Battleship,
Units.Carrier:Carrier,
Units.Transport:Transport,
Units.InfArt:InfArt,
Units.MechInfArt:MechInfArt,
Units.TankTactBomber:TankTactBomber,
Units.FighterTactBomber:FighterTactBomber,}

class UnitCollection:
    def __init__(self, unitList:pd.Series, unitProfiles:pd.DataFrame):
        self._unitList = []
        self.unitStrengths = {}
        self._loadUnitStrengths(unitProfiles)
        self._loadUnits(unitList)

        self._makeComboUnits()
        self.defineLossPriority(
            [Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank]
        )
        self._originalUnitList = self._unitList.copy()

    def _loadUnits(self, unitList:pd.Series):
        for index, row in unitList.items():
            unitType = unitDict[Units(index)] # Convert the int index to a Unit enum value, then get the type from the dictionary
            for i in range(row):
                self._unitList.append(unitType(self.unitStrengths[unitType]))

    def _loadUnitStrengths(self, unitProfiles:pd.DataFrame):
        for index,row in unitProfiles.iterrows():
            unitType = unitDict[Units(index)]
            self.unitStrengths[unitType] = (row["Attack"],row["Defense"])
        
        for key,value in self.unitStrengths.items():
            if issubclass(key,ComboUnit):
                attStr, defStr = value
                att = tuple([int(x) for x in str.split(attStr,"^")])
                defense = tuple([int(x) for x in str.split(defStr,"^")])
                self.unitStrengths[key] = (att,defense)
            else:
                self.unitStrengths[key] = (int(value[0]), int(value[1]))

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
        print(self.unitStrengths[InfArt])
        # Inf & Art
        while self._unitTypeInList(Infantry) and self._unitTypeInList(Artillery):
            if self._removeUnitType(Artillery) == 0:
                raise Exception("No artillery removed when it should have been")
            if self._removeUnitType(MechInfantry) == 1:
                self._unitList.append(MechInfArt(self.unitStrengths[MechInfArt]))
                continue
            if self._removeUnitType(Infantry) == 1:
                self._unitList.append(InfArt(self.unitStrengths[InfArt]))
                continue
            raise Exception("No infantry removed when it should have been")

    def __str__(self):
        collStr = "Units in collection: " + str(self.unitCount()) + "\n"
        unitCount = Counter(type(obj) for obj in self._unitList)
        for objType, objCount in unitCount.items():
            collStr += objType.__name__ + ": " + str(objCount) + "\n"
        return collStr + "\n"

    def unitCount(self):
        return len(
            [u for u in self._unitList if not isinstance(u, ComboUnit)]
        ) + 2 * len([u for u in self._unitList if isinstance(u, ComboUnit)])

    def attack(self):
        hits = 0
        for u in self._unitList:
            hits += u.attack()
        return hits

    def defend(self):
        hits = 0
        for u in self._unitList:
            hits += u.defend()
        return hits

    def defineLossPriority(self, unitTypeList):
        self._lossPriority = unitTypeList

    def takeLosses(self, hitCount):
        if hitCount >= self.unitCount():
            self._unitList = []
            return

        def correctComboUnits(comboType):
            self._unitList.append(
                comboType.priority(*self.unitStrengths[comboType.priority])
            )
            self._makeComboUnits()

        for unitType in self._lossPriority:
            while self._unitTypeInList(unitType) and hitCount > 0:
                removed = self._removeUnitType(unitType, 1)
                if removed > 0 and issubclass(unitType, ComboUnit):
                    correctComboUnits(unitType)
                    self._makeComboUnits()
                hitCount -= removed
        while hitCount > 0:
            unit = self._unitList.pop()
            if isinstance(unit, ComboUnit):
                correctComboUnits(type(unit))
            hitCount -= 1

    def reset(self):
        self._unitList = self._originalUnitList.copy()

    def printUnitsAndStrength(self, label="Unit List"):
        for u in self._unitList:
            print(label)
            if isinstance(u, ComboUnit):
                print(type(u).__name__, u.attackVals, u.defenseVals)
            else:
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            print()


if __name__ == "__main__":
    attacker = UnitCollection(infantry=2, artillery=2, tanks=1, infantry_mech=2)
    print(str(attacker))
    attacker.defineLossPriority(
        [Infantry, MechInfantry, InfArt, MechInfArt, Artillery, Tank]
    )
    while attacker.unitCount() > 0:
        attacker.takeLosses(1)
        print(str(attacker))
    hits = []
    count = 0
    while count < 1000:
        hits.append(attacker.defend())
        count += 1
    print(len(hits))
    print(mean(hits))
    print(median(hits))
