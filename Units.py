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
    pass


class Artillery(CombatUnit, LandUnit):
    pass


class Tank(CombatUnit, LandUnit):
    pass


class Fighter(CombatUnit, AirUnit):
    pass


class Bomber(CombatUnit, AirUnit):
    pass


class TacticalBomber(Bomber):
    pass


class StratBomber(Bomber):
    pass


class SurfaceShip(NavalUnit):
    pass


class Submarine(CombatUnit, NavalUnit):
    pass


class Warship(CombatUnit, SurfaceShip):
    pass


class Carrier(Warship):
    pass


class Battleship(Warship):
    pass


class Cruiser(Warship):
    pass


class Destroyer(Warship):
    pass


class Transport(SurfaceShip):
    pass


class InfArt(Infantry, Artillery, ComboUnit):
    pass


class MechInfArt(MechInfantry, Artillery, ComboUnit):
    pass


class TankTactBomber(Tank, TacticalBomber, ComboUnit):
    pass


class FighterTactBomber(Fighter, TacticalBomber, ComboUnit):
    pass
