from Units import *
from itertools import filterfalse, count

infStrength = (2, 3)
mechInfStrength = infStrength
artStrength = (3, 3)
tankStrength = (7, 6)


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
        return any(isinstance(unit, unitType) for unit in self._unitList)

    def _removeUnitType(self, unitType, removeCount=1):
        self._unitList = list(
            filterfalse(
                lambda u, counter=count(): isinstance(u, unitType)
                and next(counter) < removeCount,
                self._unitList,
            )
        )

    def _makeComboUnits(self):
        # Inf & Art
        pass
        # while(self._unitTypeInList(Infantry) and self._unitTypeInList(Artillery)):

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


if __name__ == "__main__":
    attacker = UnitCollection(infantry=2, artillery=2, tanks=1)
    print(attacker._unitList)
    attacker._removeUnitType(Tank)
    print(attacker._unitList)
    hits = 0
    count = 0
    while hits != 3:
        hits = attacker.defend()
        count += 1
    print(count)
