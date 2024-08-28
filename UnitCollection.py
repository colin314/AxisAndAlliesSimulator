from Units import *

infStrength = (2, 3)
mechInfStrength = infStrength
artStrength = (3, 3)
tankStrength = (7, 6)


class UnitCollection:
    def __init__(self, **kwargs):
        self.unitList = []
        # Infantry
        for i in range(kwargs.get("infantry") or 0):
            self.unitList.append(Infantry(*infStrength))
        for i in range(kwargs.get("infantry_mech") or 0):
            self.unitList.append(MechInfantry(*mechInfStrength))
        for i in range(kwargs.get("artillery") or 0):
            self.unitList.append(Artillery(*artStrength))
        for i in range(kwargs.get("tanks") or 0):
            self.unitList.append(Tank(*tankStrength))


if __name__ == "__main__":
    attacker = UnitCollection(infantry=2, artillery=2, tanks=1)
    print(attacker.unitList)
