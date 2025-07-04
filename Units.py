import random
from time import sleep
from dyce import H
from TechMapping import Tech
from tqdm import tqdm
import sys
from colorama import Style
from colorama import Back
from colorama import Fore
from colorama import init as colorama_init
from Config import Config

class UFmt:
    attHead = f"{Back.RED}{Style.BRIGHT}{Fore.WHITE}"
    tmp = f"{Back.RED}{Fore.WHITE}"
    defHead = f"{Back.BLUE}{Style.BRIGHT}{Fore.WHITE}"
    att = f"{Fore.LIGHTRED_EX}"
    df = f"{Fore.LIGHTBLUE_EX}"
    genHead = f"{Back.WHITE}{Fore.BLACK}"
    Attacker = f"{att}Attacker{Style.RESET_ALL}"
    Defender = f"{df}Defender{Style.RESET_ALL}"
    AttackerHead = f"{attHead}Attacker{Style.RESET_ALL}"
    DefenderHead = f"{defHead}Defender{Style.RESET_ALL}"

class Unit:
    diceSize = Config.DICE_SIZE

    def __init__(self, tech:list[Tech] = []):
        self.cost = 0
        self.tech = tech
        self.advantage = False
        self.HP = 1

    def __lt__(self, other):
        return self.cost <= other.cost

    def __le__(self, other):
        return self.cost <= other.cost

    def __gt__(self, other):
        return self.cost > other.cost

    def _getRollStr(roll, strength):
        adjStr = (13 - strength)
        adjRoll = (13 - roll)
        length = Config.DICE_SIZE
        if roll <= strength:
            p1 = Fore.GREEN + '█' * roll
            p2 = Fore.BLACK + '█' * (strength - roll) 
            p3 = Fore.BLACK + '-' * (length - strength) + Style.RESET_ALL
        else:
            p1 = Fore.LIGHTRED_EX + '█' * strength
            p2 = Fore.RED + '█' * (roll-strength)
            p3 = Fore.BLACK + '-' * (length - roll) + Style.RESET_ALL
        bar = p1 + p2 + p3
        return f'|{bar}| {roll} / {strength}'


class LandUnit(Unit):
    pass


class AirUnit(Unit):
    pass


class NavalUnit(Unit):
    pass


class NonCombatUnit(Unit):
    def __init__(self):
        super().__init__()

class CombatUnit(Unit):
    def __init__(self, strengthArr: list[tuple[int, ...]], tech:list[Tech] = []):
        super().__init__(tech)
        self.attackStrength, self.defenseStrength = strengthArr
        self.didFirstStrike = False
        self._setValidTargets()
        self.applyTech()

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
            x = random.randint(1, Config.DICE_SIZE)
            if self.advantage:
                x = min(x,random.randint(1, Config.DICE_SIZE))
            hits += 1 if x <= value else 0
            sys.stdout.write(f"{f"{self.__class__.__name__}:":<15} {Unit._getRollStr(x,value)} {"HIT" if x <= value else ""}\n")
            sys.stdout.flush()
            sleep(Config.ROLL_DELAY_MS / 1000)
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
        die = H(Config.DICE_SIZE)
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
                hitDie = H({0: Config.DICE_SIZE})
            dice.append(hitDie)
        return sum(dice)

    def applyTech(self):
        """Virtual function used to apply techs that modify combat strength (e.g., Super Subs)"""
        pass

class ComboUnit(CombatUnit):
    """Represents combined arms effects of combining 2 (or more) units."""

    def __init__(self, strengthArr: list[tuple[int, ...]], tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class FirstStrikeUnit(CombatUnit):
    """Represents units that make their combat rolls in the first strike phase (i.e. submarines)"""

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)
        self._counterUnits = []

    def isCountered(self, opponent):
        for counter in self._counterUnits:
            if opponent._unitInstanceInList(counter):
                return True
        return False

    def _doFirstStrikeCombat(self, strength, opponent):
        if self.isCountered(opponent):
            return 0

        self.didFirstStrike = True
        return self._makeRolls(strength)

    def _firstStrikeAttack(self, opponent):
        return self._doFirstStrikeCombat(self.attackStrength, opponent)

    def _firstStrikeDefense(self, opponent):
        return self._doFirstStrikeCombat(self.defenseStrength, opponent)


class Infantry(CombatUnit, LandUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)

class Conscript(CombatUnit, LandUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)

class MechInfantry(Infantry):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Artillery(CombatUnit, LandUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Tank(CombatUnit, LandUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class AAA(FirstStrikeUnit, LandUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Fighter(CombatUnit, AirUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Bomber(CombatUnit, AirUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class TacticalBomber(Bomber):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class StratBomber(Bomber):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)
        if Tech.HeavyBombers in self.tech:
            self.advantage = True


class SurfaceShip(NavalUnit):
    pass


class Submarine(FirstStrikeUnit, NavalUnit):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)
        # TODO: Figure out where to make this definition. Currently double defined
        self.ValidTargets = [NavalUnit]
        self._counterUnits.append(Destroyer)

    def applyTech(self):
        if Tech.SuperSubs in self.tech:
            self.attackStrength = [x + Config.SUPER_SUB_STRENGTH for x in self.attackStrength]


class Warship(CombatUnit, SurfaceShip):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class DamagedCarrier(Warship):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Carrier(Warship, ComboUnit):
    priority = [DamagedCarrier]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)
        self.HP = 2


class DamagedBattleship(Warship):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Battleship(Warship, ComboUnit):
    priority = [DamagedBattleship]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)
        self.HP = 2


class Cruiser(Warship):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Destroyer(Warship):
    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class Transport(SurfaceShip):
    pass

class ConscriptPair(ComboUnit, Conscript):
    priority=[Conscript, Conscript]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)

class InfArt(ComboUnit, Infantry, Artillery):
    priority = [Artillery, Infantry]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    priority = [Artillery, MechInfantry]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    priority = [TacticalBomber, Tank]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    priority = [TacticalBomber, Fighter]

    def __init__(self, strengthArr, tech:list[Tech] = []):
        super().__init__(strengthArr, tech)

class InfArt2(ComboUnit, Artillery, Infantry):
    priority = [InfArt, Infantry]

class MechInfArt2(MechInfArt):
    priority = [MechInfArt, MechInfantry, MechInfantry]

class InfMechInfArt(InfArt, MechInfArt):
    priority = [MechInfArt, Infantry]

class MechInfTank(ComboUnit, MechInfantry, Tank):
    priority = [Tank, MechInfantry]