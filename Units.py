class Unit:
    pass


class LandUnit(Unit):
    pass


class AirUnit(Unit):
    pass


class NavalUnit(Unit):
    pass


class ComboUnit(Unit):
    pass


class CombatUnit(Unit):
    pass


class PreCombatUnit(CombatUnit):
    pass


class NonCombatUnit(Unit):
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
