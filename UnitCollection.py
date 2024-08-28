from Units import *

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
    hits = 0
    count = 0
    while hits != 5:
        hits = attacker.defend()
        count += 1
    print(count)
