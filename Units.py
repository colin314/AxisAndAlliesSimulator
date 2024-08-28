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
    def __init__(self, attack, defense):
        self.attack = attack
        self.defense = defense
        super().__init__()

    def _roll(self, value):
        """Roll the dice against the specified value"""
        x = random.randint(1, self.diceSize)
        return 1 if x <= value else 0

    def _attack(self):
        return self._roll(self.attack)

    def _defend(self):
        return self._defend(self.defense)


class ComboUnit(CombatUnit):
    pass


class PreCombatUnit(CombatUnit):
    pass


class Infantry(LandUnit, CombatUnit):
    pass


class MechInfantry(Infantry):
    pass


class Artillery(LandUnit, CombatUnit):
    pass


class Tank(LandUnit, CombatUnit):
    pass


class Fighter(AirUnit, CombatUnit):
    pass


class Bomber(AirUnit, CombatUnit):
    pass


class TacticalBomber(Bomber):
    pass


class StratBomber(Bomber):
    pass


class SurfaceShip(NavalUnit):
    pass


class Submarine(NavalUnit, CombatUnit):
    pass


class Warship(SurfaceShip, CombatUnit):
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


inf = Infantry(2, 5)
cUnit = CombatUnit(2, 3)
cUnit._roll()
inf._roll()
