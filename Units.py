import random


class Unit:
    diceSize = 12

    def __init__(self):
        self.cost = 0

    pass


class LandUnit(Unit):
    def __init__(self):
        super().__init__()


class AirUnit(Unit):
    def __init__(self):
        super().__init__()


class NavalUnit(Unit):
    def __init__(self):
        super().__init__()


class NonCombatUnit(Unit):
    def __init__(self):
        super().__init__()

    pass


class CombatUnit(Unit):
    def __init__(self, attackStrength, defenseStrength):
        self.attackStrength = attackStrength
        self.defenseStrength = defenseStrength
        super().__init__()

    def _roll(self, value):
        """Roll the dice against the specified value"""
        x = random.randint(1, self.diceSize)
        return 1 if x <= value else 0

    def attack(self):
        return self._roll(self.attackStrength)

    def defend(self):
        return self._roll(self.defenseStrength)


class ComboUnit(CombatUnit):
    def __init__(self, attackVals, defenseVals):
        self.attackVals = attackVals
        self.defenseVals = defenseVals
        super().__init__(0, 0)

    def _makeRolls(self, rollValues):
        hits = 0
        for value in rollValues:
            hits += self._roll(value)
        return hits

    def attack(self):
        return self._makeRolls(self.attackVals)

    def defend(self):
        return self._makeRolls(self.defenseVals)


class PreCombatUnit(CombatUnit):
    pass


class Infantry(CombatUnit, LandUnit):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class MechInfantry(Infantry):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Artillery(CombatUnit, LandUnit):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Tank(CombatUnit, LandUnit):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Fighter(CombatUnit, AirUnit):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Bomber(CombatUnit, AirUnit):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class TacticalBomber(Bomber):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class StratBomber(Bomber):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class SurfaceShip(NavalUnit):
    pass


class Submarine(CombatUnit, NavalUnit):
    pass


class Warship(CombatUnit, SurfaceShip):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Carrier(Warship):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Battleship(Warship):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Cruiser(Warship):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Destroyer(Warship):
    def __init__(self, attackStrength, defenseStrength):
        super().__init__(attackStrength, defenseStrength)


class Transport(SurfaceShip):
    pass


class InfArt(ComboUnit, Infantry, Artillery):
    priority = Artillery

    def __init__(self, attackVals, defenseVals):
        super().__init__(attackVals, defenseVals)


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    priority = Artillery

    def __init__(self, attackVals, defenseVals):
        super().__init__(attackVals, defenseVals)


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    priority = TacticalBomber

    def __init__(self, attackVals, defenseVals):
        super().__init__(attackVals, defenseVals)


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    priority = TacticalBomber

    def __init__(self, attackVals, defenseVals):
        super().__init__(attackVals, defenseVals)


if __name__ == "__main__":
    ia = InfArt([3, 3], [4, 3])

    hits = 0
    for i in range(12):
        hits += ia.attack()
    print(hits)
