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
        self.ValidTargets = [Unit]
        self.ImmuneTargets = []
        if isinstance(self, AirUnit):
            self.ImmuneTargets.extend([Submarine])
        if isinstance(self, Submarine):
            self.ValidTargets = [NavalUnit]

    def _roll(self, value):
        """Roll the dice against the specified value"""
        x = random.randint(1, self.diceSize)
        return 1 if x <= value else 0

    def attack(self):
        return self._roll(self.attackStrength)

    def defend(self):
        return self._roll(self.defenseStrength)
    
    def unitHitDie(self,attack=True):
        if attack:
            strength = self.attackStrength
        else:
            strength = self.defenseStrength
        die = H(Unit.diceSize)
        unitDie = H({
            1:die.le(strength)[1],
            0:die.ge(strength + 1)[1]
        })
        return unitDie


class ComboUnit(CombatUnit):
    def __init__(self, strengthArr):
        self.attackVals, self.defenseVals = strengthArr
        super().__init__([0, 0])

    def _makeRolls(self, rollValues):
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

        unitDie1 = H({
            1:die.le(strengthVals[0])[1],
            0:die.ge(strengthVals[0] + 1)[1]
        })
        unitDie2 = H({
            1:die.le(strengthVals[1])[1],
            0:die.ge(strengthVals[1] + 1)[1]
        })
        return unitDie1 + unitDie2


class PreCombatUnit(CombatUnit):
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
        self.ValidTargets = [NavalUnit]


class Warship(CombatUnit, SurfaceShip):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Carrier(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class DamagedBattleship(Warship):
    def __init__(self, strengthArr):
        super().__init__(strengthArr)


class Battleship(Warship,ComboUnit):
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


if __name__ == "__main__":
    ia = InfArt([3, 3], [4, 3])

    hits = 0
    for i in range(12):
        hits += ia.attack()
    print(hits)
