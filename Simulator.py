"""
Battle Simulator for Axis & Allies

This module provides the main battle simulation functionality for the Axis & Allies
board game simulator. It handles combat resolution, statistics generation, and
battle outcome analysis for both land and naval battles.
"""

from colorama import Style, Back, Fore, init as colorama_init
import argparse
import os
from typing import List, Dict, Tuple
from UnitCollection import UnitCollection
from Units import *
import pandas as pd
from statistics import mean, median
from Resources import bcolors
import sys
from tabulate import tabulate
from UI_UnitSelector import GetUnitList, Combatant
from UI_CasualtySelector import get_unit_casualties
from UnitsEnum import Units

# Constants
UNIT_LISTS_FILE = "unitLists.csv"

# Mapping from UI unit names to internal unit enums
UNIT_UI_MAP = {
    "infantry": Units.Infantry,
    "mech_infantry": Units.MechInfantry,
    "artillery": Units.Artillery,
    "armour": Units.Tank,
    "fighter": Units.Fighter,
    "tactical_bomber": Units.TacticalBomber,
    "bomber": Units.StratBomber,
    "aaGun": Units.AAA,
    "conscript": Units.Conscript,
    "cruiser": Units.Cruiser,
    "battleship": Units.Battleship,
    "submarine": Units.Submarine,
    "destroyer": Units.Destroyer,
    "carrier": Units.Carrier,
    "battleship_hit": Units.DamagedBattleship,
    "carrier_hit": Units.DamagedCarrier,
    "transport": Units.Transport,
}


class Fmt:
    """Formatting constants for colored console output."""
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


class Simulator:
    """
    Main battle simulator for Axis & Allies combat resolution.
    
    This class handles the simulation of battles between attacking and defending
    forces, including casualty selection, multiple round combat, and statistical
    analysis of battle outcomes.
    """

    def SimulateBattle(
        self,
        retreat_threshold=0,
        max_rounds=-1,
        print_outcome=False,
        print_battle=False,
        is_land: bool = True
    ):
        """
        Simulate a battle between attacker and defender.
        
        Args:
            retreat_threshold: HP threshold at which attacker retreats
            max_rounds: Maximum number of rounds (-1 for unlimited)
            print_outcome: Whether to print the battle outcome
            print_battle: Whether to print each round of battle
            is_land: True for land battle, False for naval battle
            
        Returns:
            Tuple of (attacker_hp, defender_hp) remaining after battle
        """
        max_rounds = sys.maxsize if max_rounds < 0 else max_rounds
        self.attacker.reset()
        self.defender.reset()
        battle_round = 0
        if print_battle:
            print(f"{bcolors.BOLD}{bcolors.GREEN}Battle Rounds{bcolors.ENDC}")
            print("\u2550" * 50)
        retreat = False
        while (
            self.attacker.currHP() > 0
            and self.defender.currHP() > 0
            and not retreat
            and battle_round < max_rounds
        ):
            os.system("cls")
            attacker_hit_count, defender_hit_count = (0, 0)
            battle_round += 1
            # First Strike Phase
            if self.attacker.CanFirstStrike():
                print(f"{Fmt.Attacker} Submarines:")
                attacker_hits = self.attacker.firstStrikeAttack(self.defender)
                attacker_hit_count += len(attacker_hits)
                def_units = self._getCasualties(self.defender, len(attacker_hits), is_land, "Defender")

            if self.defender.CanFirstStrike():
                print(f"{Fmt.Defender} Submarines:")
                defender_hits = self.defender.firstStrikeDefend(self.attacker)
                defender_hit_count += len(defender_hits)
                att_units = self._getCasualties(self.attacker, len(defender_hits), is_land, "Attacker")

            if self.attacker.CanFirstStrike():
                self.defender.reload_units_from_dict(def_units)
                for u in self.defender._unit_list:
                    if isinstance(u, FirstStrikeUnit):
                        u.didFirstStrike = True

            if self.defender.CanFirstStrike():
                self.attacker.reload_units_from_dict(att_units)
                for u in self.attacker._unit_list:
                    if isinstance(u, FirstStrikeUnit):
                        u.didFirstStrike = True

            # General Combat Phase
            print(f"{Fmt.AttackerHead}")
            attacker_hits = self.attacker.attack()
            attacker_hit_count += len(attacker_hits)
            # Assign hits
            def_units = self._getCasualties(self.defender, len(attacker_hits), is_land, "Defender")
            
            print(f"{Fmt.DefenderHead}")
            defender_hits = self.defender.defend()
            defender_hit_count += len(defender_hits)
            # Assign hits to attacker
            att_units = self._getCasualties(self.attacker, len(defender_hits), is_land, "Attacker")
            
            self.attacker.reload_units_from_dict(att_units)
            self.defender.reload_units_from_dict(def_units)

            retreat = self.attacker.currHP() <= retreat_threshold

            if print_battle:
                self.print_battle_state(
                    battle_round,
                    self.attacker,
                    self.defender,
                    attacker_hit_count,
                    defender_hit_count,
                )
                if (
                    not retreat
                    and self.attacker.currHP() > 0
                    and self.defender.currHP() > 0
                ):
                    userInput = input(
                        "Press Enter to continue, or type 'r' to retreat: "
                    )
                    retreat = retreat if userInput == "" else True

        if print_outcome:
            self.print_battle_outcome()
        return (self.attacker.currHP(), self.defender.currHP())

    def _getCasualties(self, combatant: UnitCollection, num_hits: int, is_land: bool, side: str):
        """Get casualties for a combatant based on the number of hits received."""
        unit_dict = combatant.generateUnitDict(isLand=is_land)
        sub_present = not is_land and unit_dict["submarine"] > 0
        if num_hits > 0:
            if num_hits < combatant.currHP() or sub_present:
                unit_dict = get_unit_casualties(is_land, unit_dict, num_hits, side, combatant.power)
            else:
                unit_dict = {}
        
        return unit_dict

    def _get_round_stats(
        self,
        battle_round: int,
        attacker_expected_hits: float,
        defender_expected_hits: float,
        attacker_hit_count: int,
        defender_hit_count: int,
    ) -> List:
        """Get statistics for a battle round."""
        data_row = [
            battle_round,
            self.attacker.currHP(),
            self.attacker.currCost(),
            attacker_expected_hits,
            attacker_hit_count,
            self.defender.currHP(),
            self.defender.currCost(),
            defender_expected_hits,
            defender_hit_count,
        ]
        return data_row

    def print_battle_state(
        self, 
        battle_round: int, 
        attacker: UnitCollection, 
        defender: UnitCollection, 
        attacker_hits: int, 
        defender_hits: int
    ):
        """Print the current state of the battle."""
        print(f"Round {bcolors.RED}{battle_round}{bcolors.ENDC}")
        print("\u2500" * 40)
        print(f"{Fmt.Attacker} Hits: {attacker_hits}")
        print(f"{Fmt.Defender} Hits: {defender_hits}\n")
        print(f"{Fmt.AttackerHead} HP: {attacker.currHP()}")
        attacker.PrintCollectionComparison()
        print()
        print(f"{Fmt.DefenderHead} HP: {defender.currHP()}")
        defender.PrintCollectionComparison()
        print()

    def print_battle_outcome(self):
        """Print the final outcome of the battle."""
        if self.defender.currHP() == 0 and self.attacker.currHP() > 0:
            print(f"Outcome: {Fmt.attHead}Attacker victory{Style.RESET_ALL}")
        else:
            print(f"Outcome: {Fmt.defHead}Defender Victory{Style.RESET_ALL}")

        ipc_swing = self.attacker.valueDelta() - self.defender.valueDelta()
        print(
            f"{Fore.LIGHTMAGENTA_EX}IPC Swing (Attacker):"
            f"{Style.RESET_ALL} {ipc_swing}\n"
        )

    @staticmethod
    def load_unit_collection(list_name: str, profile_name: str) -> UnitCollection:
        """Load a unit collection from CSV files."""
        profile = pd.read_csv(
            f"UnitProfiles_{profile_name}.csv", encoding="utf-8", delimiter=","
        )
        unit_list = pd.read_csv(UNIT_LISTS_FILE, encoding="utf-8", delimiter=",")

        units = UnitCollection(unit_list[["Key", list_name]], profile)
        return units

    @staticmethod
    def load_unit_collection_from_ui(combatant: Combatant, profile_name: str) -> UnitCollection:
        """Load a unit collection from UI input."""
        headers = ["Key", "ListName"]
        unit_list = combatant.units
        units = [[UNIT_UI_MAP[unit].value, val] for unit, val in unit_list.items()]
        unit_list = pd.DataFrame(units, columns=headers)
        profile = pd.read_csv(
            f"UnitProfiles_{profile_name}.csv", encoding="utf-8", delimiter=","
        )
        units = UnitCollection(unit_list, profile, combatant.power)
        return units

    def load_attacker(self, list_name: str, profile_name: str):
        """Load the attacking force."""
        self.attacker = Simulator.load_unit_collection(list_name, profile_name)

    def load_defender(self, list_name: str, profile_name: str):
        """Load the defending force."""
        self.defender = Simulator.load_unit_collection(list_name, profile_name)

    def reset(self):
        """Reset both attacker and defender to their initial state."""
        self.attacker.reset()
        self.defender.reset()

    def generate_battle_stats(self, battle_count: int = 10000):
        """Generate statistics from multiple battle simulations."""
        result_arr = []
        self.reset()
        for i in range(battle_count):
            (attacker_hp, defender_hp) = self.SimulateBattle()
            attacker_won = 1 if attacker_hp > defender_hp else 0
            tuv_swing = self.attacker.valueDelta() - self.defender.valueDelta()
            results = [attacker_won, attacker_hp, defender_hp, tuv_swing]
            result_arr.append(results)
            self.attacker.reset()
            self.defender.reset()
            
        result_df = pd.DataFrame(
            result_arr,
            columns=[
                "Attacker Won",
                "Remainder Attacker",
                "Remainder Defender",
                "Average IPC Swing (Attacker)",
            ],
        )
        attack_win_rate = result_df["Attacker Won"].mean()
        print(
            f"Attacker wins {Fore.RED}{attack_win_rate:2.2%}"
            f"{Style.RESET_ALL} percent of the time."
        )
        victory_data = result_df.groupby("Attacker Won").mean()
        victory_data["Units Remaining"] = victory_data[
            ["Remainder Attacker", "Remainder Defender"]
        ].max(axis=1)
        victory_data = victory_data[["Units Remaining", "Average IPC Swing (Attacker)"]]
        print(tabulate(victory_data, headers="keys", tablefmt="fancy_grid"))
        print()

    def generate_extended_battle_stats(self, battle_count: int = 2000):
        """Generate extended battle statistics with round-by-round data."""
        result_arr = []
        self.reset()
        round_stats = []
        for i in range(battle_count):
            run_stats = self.SimulateBattleWithStats()
            max_round = len(run_stats) - 1
            for stat in run_stats:
                stat.append(max_round)
            round_stats.extend(run_stats)
            attacker_hp = self.attacker.currHP()
            defender_hp = self.defender.currHP()
            attacker_won = 1 if attacker_hp > defender_hp else 0
            tuv_swing = self.attacker.valueDelta() - self.defender.valueDelta()
            results = [attacker_won, attacker_hp, defender_hp, tuv_swing]
            result_arr.append(results)
            
        headers = [
            "Round",
            "Attacker HP",
            "Attacker TUV",
            "Attacker Expected Hits",
            "Attacker Actual Hits",
            "Defender HP",
            "Defender TUV",
            "Defender Expected Hits",
            "Defender Actual Hits",
            "Max Rounds",
        ]
        rounds_df = pd.DataFrame(round_stats, columns=headers)
        
        # Granular Analysis
        grouped_df = rounds_df.groupby(["Max Rounds", "Round"]).aggregate(
            {
                "Round": "size",
                "Attacker HP": "mean",
                "Attacker TUV": "mean",
                "Attacker Expected Hits": "mean",
                "Attacker Actual Hits": "mean",
                "Defender HP": "mean",
                "Defender TUV": "mean",
                "Defender Expected Hits": "mean",
                "Defender Actual Hits": "mean",
            }
        )
        grouped_df.rename(columns={"Round": "Count"}, inplace=True)
        grouped_df.reset_index()
        grouped_df.to_csv("tmp.csv", sep="\t")

        # Group by round
        grouped_df = rounds_df.groupby(["Round"]).aggregate(
            {
                "Round": "size",
                "Attacker HP": "mean",
                "Attacker TUV": "mean",
                "Attacker Expected Hits": "mean",
                "Attacker Actual Hits": "mean",
                "Defender HP": "mean",
                "Defender TUV": "mean",
                "Defender Expected Hits": "mean",
                "Defender Actual Hits": "mean",
            }
        )
        grouped_df.rename(columns={"Round": "Count"}, inplace=True)
        grouped_df.reset_index()
        grouped_df.to_csv("tmp2.csv", sep="\t")

    @staticmethod
    def swap_places(attacker, defender):
        """Swap the positions of attacker and defender."""
        return (defender, attacker)

    def simulate_battle_with_stats(
        self,
        attacker_loss_profile=UnitCollection.DEFAULT_LOSS_PRIORITY,
        defender_loss_profile=UnitCollection.DEFAULT_LOSS_PRIORITY,
        sim_count: int = 1000,
    ):
        """Simulate a battle with detailed statistics."""
        Unit.diceSize = 12
        self.attacker.define_loss_priority(attacker_loss_profile)
        self.defender.define_loss_priority(defender_loss_profile)

        self.SimulateBattle(print_battle=True, print_outcome=True)

        print(f"{Fmt.genHead}Statistics{Style.RESET_ALL}\n")
        self.generate_battle_stats(sim_count)

    def simulate_battle_web(
        self,
        retreat_threshold=0,
        max_rounds=-1,
        is_land: bool = True
    ) -> Tuple[int, int]:
        """
        Simulate a battle for web interface (non-interactive).
        
        Args:
            retreat_threshold: HP threshold at which attacker retreats
            max_rounds: Maximum number of rounds (-1 for unlimited)
            is_land: True for land battle, False for naval battle
            
        Returns:
            Tuple of (attacker_hp, defender_hp) remaining after battle
        """
        max_rounds = sys.maxsize if max_rounds < 0 else max_rounds
        self.attacker.reset()
        self.defender.reset()
        battle_round = 0
        retreat = False
        
        while (
            self.attacker.currHP() > 0
            and self.defender.currHP() > 0
            and not retreat
            and battle_round < max_rounds
        ):
            attacker_hit_count, defender_hit_count = (0, 0)
            battle_round += 1
            
            # First Strike Phase
            if self.attacker.CanFirstStrike():
                attacker_hits = self.attacker.firstStrikeAttack(self.defender)
                attacker_hit_count += len(attacker_hits)
                def_units = self._getCasualties(self.defender, len(attacker_hits), is_land, "Defender")

            if self.defender.CanFirstStrike():
                defender_hits = self.defender.firstStrikeDefend(self.attacker)
                defender_hit_count += len(defender_hits)
                att_units = self._getCasualties(self.attacker, len(defender_hits), is_land, "Attacker")

            if self.attacker.CanFirstStrike():
                self.defender.reload_units_from_dict(def_units)
                for u in self.defender._unit_list:
                    if isinstance(u, FirstStrikeUnit):
                        u.didFirstStrike = True

            if self.defender.CanFirstStrike():
                self.attacker.reload_units_from_dict(att_units)
                for u in self.attacker._unit_list:
                    if isinstance(u, FirstStrikeUnit):
                        u.didFirstStrike = True

            # General Combat Phase
            attacker_hits = self.attacker.attack()
            attacker_hit_count += len(attacker_hits)
            def_units = self._getCasualties(self.defender, len(attacker_hits), is_land, "Defender")
            
            defender_hits = self.defender.defend()
            defender_hit_count += len(defender_hits)
            att_units = self._getCasualties(self.attacker, len(defender_hits), is_land, "Attacker")
            
            self.attacker.reload_units_from_dict(att_units)
            self.defender.reload_units_from_dict(def_units)

            retreat = self.attacker.currHP() <= retreat_threshold

        return (self.attacker.currHP(), self.defender.currHP())

class Inputs:
    pass


def run_single_simulation():
    """Run a single simulation for testing purposes."""
    # os.system('cls')
    parser = argparse.ArgumentParser()
    inputs = Inputs()
    parser.add_argument("attacker")
    parser.add_argument("attProfile")
    parser.add_argument("defender")
    parser.add_argument("defProfile")
    parser.parse_args(namespace=inputs)

    sim = Simulator()
    sim.load_attacker(inputs.attacker, inputs.attProfile)
    sim.load_defender(inputs.defender, inputs.defProfile)

    print(sim.defender.expectedHits(isAttack=False))
    input("Waiting...")

    sim.SimulateBattle(print_battle=True, print_outcome=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    inputs = Inputs()
    parser.add_argument("isLand")
    parser.parse_args(namespace=inputs)
    is_land = True if int(inputs.isLand) == 1 else False
    lists = GetUnitList(isLand=is_land)
    attacker: UnitCollection = Simulator.load_unit_collection_from_ui(
        lists["attacker"], "Original_d6"
    )
    defender = Simulator.load_unit_collection_from_ui(lists["defender"], "Original_d6")
    sim = Simulator()
    sim.attacker = attacker
    sim.defender = defender
    sim.SimulateBattle(print_battle=True, print_outcome=True, is_land=is_land)
