import random
from dyce import H


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


class CombatUnit(Unit):
    def __init__(self, strengthArr):
        self.attackStrength, self.defenseStrength = strengthArr
        self._setValidTargets()
        super().__init__()

    def _setValidTargets(self):
        """All special unit hit restrictions are defined here, rather than in the specific classes."""
        self.ValidTargets = [Unit]
        self.ImmuneTargets = []
        if isinstance(self, AirUnit):
            self.ImmuneTargets.extend([Submarine])
        if isinstance(self, Submarine):
            self.ValidTargets = [NavalUnit]

    def _roll(self, value):
        """Roll the dice against the specified value."""
        x = random.randint(1, self.diceSize)
        return 1 if x <= value else 0

    def attack(self):
        """Make an attack roll using the units attack strength."""
        return self._roll(self.attackStrength)

    def defend(self):
        """Make a defense roll using the units defense strength."""
        return self._roll(self.defenseStrength)

    def unitHitDie(self, isAttack=True):
        """Returns a die (i.e., histogram) of potential outcomes of a combat roll."""
        if isAttack:
            strength = self.attackStrength
        else:
            strength = self.defenseStrength
        die = H(Unit.diceSize)
        unitDie = H({
            1: die.le(strength)[1],  # Hits
            0: die.ge(strength + 1)[1]  # Misses
        })
        return unitDie


class ComboUnit(CombatUnit):
    """Represents combined arms effects of combining 2 (or more) units."""

    def __init__(self, strengthArr: list[tuple[int, ...]]):
        self.attackVals, self.defenseVals = strengthArr
        super().__init__([0, 0])

    def _makeRolls(self, rollValues):
        """Equivalent of _makeRoll for non-Combo units"""
        hits = 0
        for value in rollValues:
            hits += self._roll(value)
        return hits

    def attack(self):
        return self._makeRolls(self.attackVals)

    def defend(self):
        return self._makeRolls(self.defenseVals)

    def unitHitDie(self, attack=True):
        die = H(Unit.diceSize)
        if attack:
            strengthVals = self.attackVals
        else:
            strengthVals = self.defenseVals

        # Create a hit die for each unit in the combination
        dice = []
        for strength in strengthVals:
            hitDie = H({
                1: die.le(strength)[1],
                0: die.ge(strength + 1)[1]
            })
            dice.append(hitDie)

        return sum(dice)


class PreCombatUnit(CombatUnit):
    """Represents units that make their combat rolls in the early strike phase (i.e., AAA and submarines)"""
    pass


class Infantry(CombatUnit, LandUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class MechInfantry(Infantry):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Artillery(CombatUnit, LandUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Tank(CombatUnit, LandUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class AAA(PreCombatUnit, LandUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Fighter(CombatUnit, AirUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Bomber(CombatUnit, AirUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class TacticalBomber(Bomber):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class StratBomber(Bomber):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class SurfaceShip(NavalUnit):
    pass


class Submarine(CombatUnit, NavalUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)
        # TODO: Figure out where to make this definition. Currently double defined
        self.ValidTargets = [NavalUnit]


class Warship(CombatUnit, SurfaceShip):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class DamagedCarrier(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Carrier(Warship, ComboUnit):
    priority = DamagedCarrier

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class DamagedBattleship(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Battleship(Warship, ComboUnit):
    priority = DamagedBattleship

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Cruiser(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Destroyer(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Transport(SurfaceShip):
    pass


class InfArt(ComboUnit, Infantry, Artillery):
    priority = Artillery

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    priority = Artillery

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    priority = TacticalBomber

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    priority = TacticalBomber

    def __init__(self, strengthArr):
        super().__init__(strengthArr)
