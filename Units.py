import random


class Unit:
    def __init__(self):
        self.diceSize = 12

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
        return self._defend(self.defenseStrength)


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
    pass


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    pass


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    pass


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    pass
