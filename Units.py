import random
from dyce import H


class Unit:
    diceSize = 12

    def __init__(self):
        self.cost = 0

    def __lt__(self, other):
        return self.cost <= other.cost

    def __le__(self, other):
        return self.cost <= other.cost

    def __gt__(self, other):
        return self.cost > other.cost


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

# TODO: Refactor to use lists for attackStrength and defenseStrength


class CombatUnit(Unit):
    def __init__(self, strengthArr: list[tuple[int, ...]]):
        self.attackStrength, self.defenseStrength = strengthArr
        self.didFirstStrike = False
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

    def _makeRolls(self, rollValues):
        """Equivalent of _makeRoll for non-Combo units"""
        hits = 0
        for value in rollValues:
            x = random.randint(1, Unit.diceSize)
            hits += 1 if x <= value else 0
        return hits

    def _doStandardCombat(self, strength):
        if not self._madeFirstStrike():
            return self._makeRolls(strength)
        else:
            return 0

    def _madeFirstStrike(self):
        didFirstStrike = self.didFirstStrike
        self.didFirstStrike = False
        return didFirstStrike

    def attack(self):
        """Make an attack roll using the units attack strength."""
        return self._doStandardCombat(self.attackStrength)

    def defend(self):
        """Make a defense roll using the units defense strength."""
        return self._doStandardCombat(self.defenseStrength)

    def unitHitDie(self, isAttack=True):
        """Returns a die (i.e., histogram) of potential outcomes of a combat roll."""
        die = H(Unit.diceSize)
        if isAttack:
            strengthVals = self.attackStrength
        else:
            strengthVals = self.defenseStrength

        # Create a hit die for each unit in the combination
        dice = []
        for strength in strengthVals:
            if strength > 0:
                hitDie = H({
                    1: die.le(strength)[1],
                    0: die.ge(strength + 1)[1]
                })
            else:
                hitDie = H({0: Unit.diceSize})
            dice.append(hitDie)

        return sum(dice)


class ComboUnit(CombatUnit):
    """Represents combined arms effects of combining 2 (or more) units."""

    def __init__(self, strengthArr: list[tuple[int, ...]]):
        super().__init__(strengthArr)


class FirstStrikeUnit(CombatUnit):
    """Represents units that make their combat rolls in the first strike phase (i.e. submarines)"""

    def __init__(self, strengthArr):
        super().__init__(strengthArr)
        self._counterUnits = []

    def _doFirstStrikeCombat(self, strength, opponent):
        countered = False
        for counter in self._counterUnits:
            countered = opponent._unitInstanceInList(counter)
            if countered:
                break
        if countered:
            return 0

        self.didFirstStrike = True
        return self._makeRolls(strength)

    def _firstStrikeAttack(self, opponent):
        return self._doFirstStrikeCombat(self.attackStrength, opponent)

    def _firstStrikeDefense(self, opponent):
        return self._doFirstStrikeCombat(self.defenseStrength, opponent)


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


class AAA(FirstStrikeUnit, LandUnit):
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


class Submarine(FirstStrikeUnit, NavalUnit):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)
        # TODO: Figure out where to make this definition. Currently double defined
        self.ValidTargets = [NavalUnit]
        self._counterUnits.append(Destroyer)


class Warship(CombatUnit, SurfaceShip):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class DamagedCarrier(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Carrier(Warship, ComboUnit):
    priority = [DamagedCarrier]

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class DamagedBattleship(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Battleship(Warship, ComboUnit):
    priority = [DamagedBattleship]

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
    priority = [Artillery, Infantry]

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    priority = [Artillery, MechInfantry]

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    priority = [TacticalBomber, Tank]

    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    priority = [TacticalBomber, Fighter]

    def __init__(self, strengthArr):
        super().__init__(strengthArr)
