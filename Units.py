"""
Units module for Axis & Allies Simulator.

This module defines all unit types and their combat mechanics, including
land units, air units, naval units, and special combination units that
represent combined arms effects.
"""

import random
import sys
from typing import List, Optional

from colorama import Back, Fore, Style, init as colorama_init
from dyce import H
from tqdm import tqdm

from TechMapping import Tech

# Import the battle rolls UI
try:
    from UI_BattleRolls import add_roll_result
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class UnitFormatter:
    """Utility class for color formatting of unit combat output."""
    
    attacker_header = f"{Back.RED}{Style.BRIGHT}{Fore.WHITE}"
    temp = f"{Back.RED}{Fore.WHITE}"
    defender_header = f"{Back.BLUE}{Style.BRIGHT}{Fore.WHITE}"
    attacker_color = f"{Fore.LIGHTRED_EX}"
    defender_color = f"{Fore.LIGHTBLUE_EX}"
    general_header = f"{Back.WHITE}{Fore.BLACK}"
    attacker = f"{attacker_color}Attacker{Style.RESET_ALL}"
    defender = f"{defender_color}Defender{Style.RESET_ALL}"
    attacker_header_text = f"{attacker_header}Attacker{Style.RESET_ALL}"
    defender_header_text = f"{defender_header}Defender{Style.RESET_ALL}"

class Unit:
    """
    Base class for all combat units in the Axis & Allies simulator.
    
    This class provides basic comparison operators and defines the dice size
    used for all combat rolls.
    """
    
    dice_size = 12

    def __init__(self, tech: List[Tech] = None):
        """
        Initialize a unit with optional technology effects.
        
        Args:
            tech: List of technology effects to apply to this unit
        """
        self.cost = 0
        self.tech = tech or []
        self.advantage = False

    def __lt__(self, other: 'Unit') -> bool:
        """Compare units by cost for sorting purposes."""
        return self.cost <= other.cost

    def __le__(self, other: 'Unit') -> bool:
        """Compare units by cost for sorting purposes."""
        return self.cost <= other.cost

    def __gt__(self, other: 'Unit') -> bool:
        """Compare units by cost for sorting purposes."""
        return self.cost > other.cost

    @staticmethod
    def _get_roll_string(roll: int, strength: int) -> str:
        """
        Generate a visual representation of a combat roll.
        
        Args:
            roll: The dice roll result (1-12)
            strength: The combat strength threshold
            
        Returns:
            Colored bar chart showing the roll outcome
        """
        length = Unit.dice_size
        if roll <= strength:
            p1 = Fore.GREEN + '█' * roll
            p2 = Fore.BLACK + '█' * (strength - roll) 
            p3 = Style.RESET_ALL + '-' * (length - strength)
        else:
            p1 = Fore.LIGHTRED_EX + '█' * strength
            p2 = Fore.RED + '█' * (roll - strength)
            p3 = Style.RESET_ALL + '-' * (length - roll)
        bar = p1 + p2 + p3
        return f'|{bar}| {roll} / {strength}'


class LandUnit(Unit):
    """Base class for all land-based combat units."""
    pass


class AirUnit(Unit):
    """Base class for all air-based combat units."""
    pass


class NavalUnit(Unit):
    """Base class for all naval combat units."""
    pass


class NonCombatUnit(Unit):
    """Base class for units that cannot participate in combat."""
    
    def __init__(self):
        super().__init__()


class CombatUnit(Unit):
    """
    Base class for units that can participate in combat.
    
    This class handles combat mechanics including dice rolling,
    first strike capabilities, and target restrictions.
    """
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        """
        Initialize a combat unit with attack and defense strengths.
        
        Args:
            strength_array: Tuple containing (attack_strengths, defense_strengths)
            tech: List of technology effects to apply
        """
        super().__init__(tech)
        self.attack_strength, self.defense_strength = strength_array
        self.did_first_strike = False
        self._set_valid_targets()
        self.apply_tech()

    def _set_valid_targets(self) -> None:
        """
        Define which unit types this unit can attack and which are immune.
        
        All special unit hit restrictions are defined here, rather than 
        in the specific unit classes.
        """
        self.valid_targets = [Unit]
        self.immune_targets = []
        
        if isinstance(self, AirUnit):
            self.immune_targets.extend([Submarine])
        if isinstance(self, Submarine):
            self.valid_targets = [NavalUnit]

    def _make_rolls(self, roll_values: List[int], side: str = "") -> int:
        """
        Execute combat rolls for this unit.
        
        Args:
            roll_values: List of combat strength values to roll against
            side: Which side is rolling ("Attacker" or "Defender")
            
        Returns:
            Number of hits scored
        """
        hits = 0
        for value in roll_values:
            roll = random.randint(1, Unit.dice_size)
            
            if self.advantage:
                # Heavy bombers get to roll twice and take the better result
                roll = min(roll, random.randint(1, Unit.dice_size))
            
            hit = roll <= value
            hits += 1 if hit else 0
            
            # Display the roll result
            unit_name = self.__class__.__name__
            
            if GUI_AVAILABLE:
                # Use GUI display
                add_roll_result(unit_name, roll, value, hit, side)
            else:
                # Fall back to console output
                roll_display = Unit._get_roll_string(roll, value)
                hit_text = "HIT" if hit else ""
                sys.stdout.write(f"{unit_name:<15} {roll_display} {hit_text}\n")
                sys.stdout.flush()
            
        return hits

    def _do_standard_combat(self, strength: List[int], side: str = "") -> int:
        """
        Perform standard combat phase rolls.
        
        Args:
            strength: List of combat strength values
            side: Which side is rolling ("Attacker" or "Defender")
            
        Returns:
            Number of hits if unit hasn't made first strike, 0 otherwise
        """
        if not self._made_first_strike():
            return self._make_rolls(strength, side)
        else:
            return 0

    def _made_first_strike(self) -> bool:
        """
        Check and reset first strike status.
        
        Returns:
            True if this unit already made a first strike this round
        """
        did_first_strike = self.did_first_strike
        self.did_first_strike = False
        return did_first_strike

    def attack(self, side: str = "Attacker") -> int:
        """Make an attack roll using the unit's attack strength."""
        return self._do_standard_combat(self.attack_strength, side)

    def defend(self, side: str = "Defender") -> int:
        """Make a defense roll using the unit's defense strength."""
        return self._do_standard_combat(self.defense_strength, side)

    def unit_hit_die(self, is_attack: bool = True) -> H:
        """
        Return a probability distribution of potential combat outcomes.
        
        Args:
            is_attack: True for attack roll, False for defense roll
            
        Returns:
            Histogram representing the probability distribution of hits
        """
        die = H(Unit.dice_size)
        strength_values = self.attack_strength if is_attack else self.defense_strength

        # Create a hit die for each unit in the combination
        dice = []
        for strength in strength_values:
            if strength > 0:
                hit_die = H({
                    1: die.le(strength)[1],
                    0: die.ge(strength + 1)[1]
                })
            else:
                hit_die = H({0: Unit.dice_size})
            dice.append(hit_die)
        
        return sum(dice)

    def apply_tech(self) -> None:
        """Apply technology effects to this unit. Override in subclasses."""
        pass

class ComboUnit(CombatUnit):
    """
    Represents combined arms effects of combining 2 or more units.
    
    Combo units provide enhanced combat effectiveness when multiple
    unit types fight together.
    """

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class FirstStrikeUnit(CombatUnit):
    """
    Represents units that make their combat rolls in the first strike phase.
    
    Examples include submarines and anti-aircraft guns that fire before
    the main combat phase.
    """

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)
        self._counter_units = []

    def _do_first_strike_combat(self, strength: List[int], opponent, side: str = "") -> int:
        """
        Execute first strike combat if not countered by enemy units.
        
        Args:
            strength: Combat strength values to roll against
            opponent: Enemy force being attacked
            side: Which side is rolling ("Attacker" or "Defender")
            
        Returns:
            Number of hits if not countered, 0 if countered
        """
        countered = False
        for counter in self._counter_units:
            countered = opponent._unit_instance_in_list(counter)
            if countered:
                break
                
        if countered:
            return 0

        self.did_first_strike = True
        return self._make_rolls(strength, side)

    def _first_strike_attack(self, opponent, side: str = "Attacker") -> int:
        """Execute first strike attack phase."""
        return self._do_first_strike_combat(self.attack_strength, opponent, side)

    def _first_strike_defense(self, opponent, side: str = "Defender") -> int:
        """Execute first strike defense phase."""
        return self._do_first_strike_combat(self.defense_strength, opponent, side)


# Land Units
class Infantry(CombatUnit, LandUnit):
    """Basic infantry unit - cheapest land combat unit."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Conscript(CombatUnit, LandUnit):
    """Weaker infantry variant with reduced combat effectiveness."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class MechInfantry(Infantry):
    """Mechanized infantry with enhanced mobility and combat power."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Artillery(CombatUnit, LandUnit):
    """Artillery unit that provides combat bonuses to infantry."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Tank(CombatUnit, LandUnit):
    """Armored unit with high attack and defense values."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class AAA(FirstStrikeUnit, LandUnit):
    """Anti-aircraft artillery that fires at air units before combat."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


# Air Units
class Fighter(CombatUnit, AirUnit):
    """Fighter aircraft with balanced attack and defense capabilities."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Bomber(CombatUnit, AirUnit):
    """Base bomber class for strategic bombing operations."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class TacticalBomber(Bomber):
    """Tactical bomber that can provide combined arms bonuses."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class StratBomber(Bomber):
    """Strategic bomber with heavy bombing capabilities."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)
        if Tech.HeavyBombers in self.tech:
            self.advantage = True


# Naval Units
class SurfaceShip(NavalUnit):
    """Base class for surface naval vessels."""
    pass


class Submarine(FirstStrikeUnit, NavalUnit):
    """Submarine with first strike capability and special targeting rules."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)
        self.valid_targets = [NavalUnit]
        self._counter_units.append(Destroyer)

    def apply_tech(self) -> None:
        """Apply Super Submarines technology if available."""
        if Tech.SuperSubs in self.tech:
            self.attack_strength = [x + 2 for x in self.attack_strength]


class Warship(CombatUnit, SurfaceShip):
    """Base class for armed surface vessels."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class DamagedCarrier(Warship):
    """Aircraft carrier that has taken damage and lost combat effectiveness."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Carrier(Warship, ComboUnit):
    """Aircraft carrier that can transport and launch fighters."""
    
    priority = [DamagedCarrier]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class DamagedBattleship(Warship):
    """Battleship that has taken damage but can still fight."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Battleship(Warship, ComboUnit):
    """Heavy warship with powerful guns and thick armor."""
    
    priority = [DamagedBattleship]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Cruiser(Warship):
    """Medium warship with balanced capabilities."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Destroyer(Warship):
    """Fast warship that counters submarines."""
    
    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class Transport(SurfaceShip):
    """Non-combat vessel for transporting land units."""
    pass

# Combined Arms Units
class ConscriptPair(ComboUnit, Conscript):
    """Two conscripts fighting together with enhanced effectiveness."""
    
    priority = [Conscript, Conscript]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class InfArt(ComboUnit, Infantry, Artillery):
    """Infantry supported by artillery for enhanced combat effectiveness."""
    
    priority = [Artillery, Infantry]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class MechInfArt(ComboUnit, MechInfantry, Artillery):
    """Mechanized infantry supported by artillery."""
    
    priority = [Artillery, MechInfantry]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class TankTactBomber(ComboUnit, Tank, TacticalBomber):
    """Tank supported by tactical bomber for air-ground coordination."""
    
    priority = [TacticalBomber, Tank]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class FighterTactBomber(ComboUnit, Fighter, TacticalBomber):
    """Fighter escorting tactical bomber for enhanced air power."""
    
    priority = [TacticalBomber, Fighter]

    def __init__(self, strength_array: List[tuple], tech: List[Tech] = None):
        super().__init__(strength_array, tech)


class InfArt2(ComboUnit, Artillery, Infantry):
    """Enhanced infantry-artillery combination."""
    
    priority = [InfArt, Infantry]


class MechInfArt2(MechInfArt):
    """Enhanced mechanized infantry-artillery combination."""
    
    priority = [MechInfArt, MechInfantry, MechInfantry]


class InfMechInfArt(InfArt, MechInfArt):
    """Combined infantry and mechanized infantry with artillery support."""
    
    priority = [MechInfArt, Infantry]


class MechInfTank(ComboUnit, MechInfantry, Tank):
    """Mechanized infantry working with tanks for armored assault."""
    
    priority = [Tank, MechInfantry]