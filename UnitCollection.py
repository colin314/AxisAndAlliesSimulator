from Units import *
from itertools import filterfalse, count
from collections import Counter
from statistics import mean, median

infStrength = (2, 3)
mechInfStrength = infStrength
artStrength = (3, 3)
tankStrength = (7, 6)
infArtComboStrength = ([3, 3], [4, 3])

unitStrengths = {Artillery: artStrength}


class UnitCollection:
    def __init__(self, **kwargs):
        self._unitList = []
        # Infantry
        for i in range(kwargs.get("infantry") or 0):
            self._unitList.append(Infantry(*infStrength))
        for i in range(kwargs.get("infantry_mech") or 0):
            self._unitList.append(MechInfantry(*mechInfStrength))
        for i in range(kwargs.get("artillery") or 0):
            self._unitList.append(Artillery(*artStrength))
        for i in range(kwargs.get("tanks") or 0):
            self._unitList.append(Tank(*tankStrength))

        self._makeComboUnits()

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
        """Remove n units of the specified type from the unit list.
        Returns the number of units removed."""
        oldCount = len([u for u in self._unitList if u is not ComboUnit]) + 2 * len(
            [u for u in self._unitList if u is ComboUnit]
        )
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
                raise Exception("No artillery removed when it should have been")
            if self._removeUnitType(MechInfantry) == 1:
                self._unitList.append(MechInfArt(*infArtComboStrength))
                continue
            if self._removeUnitType(Infantry) == 1:
                self._unitList.append(InfArt(*infArtComboStrength))
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
        """Makes attack rolls for all units in collection and returns the
        number of hits"""
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
                comboType.priority(*unitStrengths[comboType.priority])
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
