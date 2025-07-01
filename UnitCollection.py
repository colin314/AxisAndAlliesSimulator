"""
Unit Collection module for Axis & Allies Simulator.

This module manages collections of units, including loading unit profiles,
creating combination units, handling combat casualties, and generating
statistical reports about force composition and effectiveness.
"""

import json
import math
from collections import Counter
from itertools import count, cycle, filterfalse
from statistics import mean, median
from typing import Dict, List, Optional, Type, Union

import pandas as pd
from dyce import H
from matplotlib import pyplot as plt
from tabulate import tabulate

from Hit import Hit
from Resources import bcolors
from TechMapping import Tech, TechMapping
from Units import *
from UnitsEnum import Units

# Suppress pandas warnings
pd.set_option("future.no_silent_downcasting", True)

# Map UI strings to unit enum values
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

# Map unit enum values to unit classes
UNIT_CLASS_MAP = {
    Units.Infantry: Infantry,
    Units.MechInfantry: MechInfantry,
    Units.Artillery: Artillery,
    Units.Tank: Tank,
    Units.AAA: AAA,
    Units.Fighter: Fighter,
    Units.TacticalBomber: TacticalBomber,
    Units.StratBomber: StratBomber,
    Units.Submarine: Submarine,
    Units.Destroyer: Destroyer,
    Units.Cruiser: Cruiser,
    Units.Battleship: Battleship,
    Units.Carrier: Carrier,
    Units.Transport: Transport,
    Units.InfArt: InfArt,
    Units.MechInfArt: MechInfArt,
    Units.TankTactBomber: TankTactBomber,
    Units.FighterTactBomber: FighterTactBomber,
    Units.DamagedBattleship: DamagedBattleship,
    Units.DamagedCarrier: DamagedCarrier,
    Units.Conscript: Conscript,
    Units.ConscriptPair: ConscriptPair,
    Units.InfArt2: InfArt2,
    Units.InfMechInfArt: InfMechInfArt,
    Units.MechInfArt2: MechInfArt2,
    Units.MechInfTank: MechInfTank,
}

COMBO_SEPARATOR = "^"


class UnitCollection:
    """
    A collection of units that will attack or defend together.
    
    This class manages groups of units, handles combined arms effects,
    tracks casualties, and provides statistical analysis of combat effectiveness.
    """
    
    DEFAULT_LOSS_PRIORITY = [
        AAA,
        Battleship,
        Conscript,
        ConscriptPair,
        Infantry,
        InfArt2,
        InfMechInfArt,
        InfArt,
        Artillery,
        MechInfArt2,
        MechInfArt,
        MechInfantry,
        Tank,
        MechInfTank,
        TankTactBomber,
        Submarine,
        Destroyer,
        Fighter,
        TacticalBomber,
        FighterTactBomber,
        StratBomber,
        Cruiser,
        DamagedBattleship,
        Carrier,
        DamagedCarrier,
    ]

    def __init__(
        self, 
        unit_list: pd.Series, 
        unit_profiles: pd.DataFrame, 
        power: str = "Neutral"
    ):
        """
        Initialize a unit collection with units and their combat profiles.
        
        Args:
            unit_list: Series containing unit counts by type
            unit_profiles: DataFrame with unit combat statistics
            power: Nation/power name for technology determination
        """
        self._unit_list: List[Unit] = []
        self.unit_strengths: Dict[Type[Unit], tuple] = {}
        self.unit_costs: Dict[Type[Unit], int] = {}
        self.power = power
        self.techs = TechMapping.GetTechs(power)

        # Initialize the collection
        self._load_unit_strengths(unit_profiles)
        self._load_units(unit_list)
        self._make_combo_units()
        self.define_loss_priority(UnitCollection.DEFAULT_LOSS_PRIORITY)
        self._unit_list.sort()

        # Record original state for resets
        self.original_cost = self.current_cost()
        self._original_loss_priority = self._loss_priority.copy()
        self._original_unit_list = self._unit_list.copy()
        
        # Create unit count table
        unit_counter = Counter(type(obj) for obj in self._get_granular_unit_list())
        unit_array = [["Unit", "Count"]]
        for obj_type, obj_count in unit_counter.items():
            unit_array.append([obj_type.__name__, obj_count])
        self.old_table = unit_array
        self.old_table_original = unit_array.copy()

    def _load_unit_strengths(self, unit_profiles: pd.DataFrame) -> None:
        """
        Load combat strengths and costs for each unit type from profiles.
        
        Args:
            unit_profiles: DataFrame containing unit statistics
        """
        for index, row in unit_profiles.iterrows():
            # Map from unit profile key to unit class
            unit_type = UNIT_CLASS_MAP[Units(row["Key"])]
            
            # Parse attack and defense strength values
            strengths = []
            for vals in (row["Attack"], row["Defense"]):
                strength_vals = [int(x) for x in str.split(vals, COMBO_SEPARATOR)]
                strengths.append(strength_vals)
            strength_tuple = tuple(strengths)
            
            self.unit_strengths[unit_type] = strength_tuple
            self.unit_costs[unit_type] = int(row["Cost"])

    # def _loadTechs(self):
    #     if Tech.SuperSubs in self.Techs:
    #         attack, defense = self.unitStrengths[Submarine]
    #         attack = [x + 2 for x in attack]
    #         self.unitStrengths[Units.Submarine] = (attack, defense)
    #         print(self.unitStrengths[Units.Submarine])

    def _load_units(self, unit_list: pd.DataFrame) -> None:
        """
        Populate the collection with units from the unit list.
        
        Args:
            unit_list: DataFrame containing unit counts by type
        """
        for index, row in unit_list.iterrows():
            # Convert the int index to a Unit enum value, then get the type from the dictionary
            unit_type = UNIT_CLASS_MAP[Units(row["Key"])]
            for i in range(row.iloc[1]):
                self._add_unit(unit_type)

    # endregion

    # Helper Methods
    def _unit_type_in_list(self, unit_type: Type[Unit]) -> bool:
        """Check if any unit of the specified type exists in the collection."""
        return any(type(unit) == unit_type for unit in self._unit_list)

    def _unit_instance_in_list(self, unit_type: Type[Unit]) -> bool:
        """Check if any instance of the specified unit type exists in the collection."""
        return any(isinstance(unit, unit_type) for unit in self._unit_list)

    def _remove_unit_type(self, unit_type: Type[Unit], remove_count: int = 1) -> int:
        """
        Remove specified number of units of the given type.
        
        Args:
            unit_type: The type of unit to remove
            remove_count: Number of units to remove
            
        Returns:
            Number of units actually removed
        """
        old_count = len(self._unit_list)
        self._unit_list = list(
            filterfalse(
                lambda u, counter=count(): type(u) == unit_type
                and next(counter) < remove_count,
                self._unit_list,
            )
        )
        new_count = len(self._unit_list)
        return old_count - new_count

    def _remove_unit_instance(self, unit_type: Type[Unit], remove_count: int = 1) -> int:
        """
        Remove specified number of unit instances of the given type.
        
        Args:
            unit_type: The type of unit to remove
            remove_count: Number of units to remove
            
        Returns:
            Number of units actually removed
        """
        old_count = len(self._unit_list)
        self._unit_list = list(
            filterfalse(
                lambda u, counter=count(): isinstance(u, unit_type)
                and next(counter) < remove_count,
                self._unit_list,
            )
        )
        new_count = len(self._unit_list)
        return old_count - new_count

    def _count_unit_type_in_list(self, unit_type: Type[Unit]) -> int:
        """Count the number of units of the specified type."""
        return len([x for x in self._unit_list if type(x) == unit_type])

    def _add_unit(self, unit_type: Type[Unit]) -> None:
        """Add a new unit of the specified type to the collection."""
        self._unit_list.append(self._make_unit(unit_type))

    def _make_unit(self, unit_type: Type[Unit]) -> Unit:
        """
        Create a new unit instance with proper strength and cost values.
        
        Args:
            unit_type: The class of unit to create
            
        Returns:
            Configured unit instance
        """
        unit = unit_type(self.unit_strengths[unit_type], self.techs)
        unit.cost = self.unit_costs[unit_type]
        return unit

    def _make_combo_units(self) -> None:
        """
        Create combined arms units by pairing compatible unit types.
        
        This method automatically combines units that fight more effectively
        together, such as infantry with artillery or tanks with tactical bombers.
        """
        # Advanced Mechanized Infantry technology
        if Tech.AdvancedMechInfantry in self.techs:
            while self._unit_type_in_list(MechInfantry) and self._unit_type_in_list(Tank):
                if self._remove_unit_type(Tank) == 0:
                    raise Exception("No tank removed when it should have been")
                if self._remove_unit_type(MechInfantry) == 0:
                    raise Exception("No mechanized infantry removed when it should have been")
                self._add_unit(MechInfTank)

        # Infantry & Artillery combinations
        while (
            self._unit_type_in_list(Infantry) or self._unit_type_in_list(MechInfantry)
        ) and self._unit_type_in_list(Artillery):
            if self._remove_unit_type(Artillery) == 0:
                raise Exception("No artillery removed when it should have been")
            if self._remove_unit_type(MechInfantry) == 1:
                self._add_unit(MechInfArt)
                continue
            if self._remove_unit_type(Infantry) == 1:
                self._add_unit(InfArt)
                continue
            raise Exception("No infantry removed when it should have been")

        # Advanced Artillery technology
        if Tech.AdvancedArtillery in self.techs:
            while (
                self._unit_type_in_list(Infantry) or self._unit_type_in_list(MechInfantry)
            ) and (self._unit_type_in_list(InfArt) or self._unit_type_in_list(MechInfArt)):
                if self._remove_unit_type(MechInfArt) == 1:
                    if self._remove_unit_type(MechInfantry) == 1:
                        self._add_unit(MechInfArt2)
                        continue
                    if self._remove_unit_type(Infantry) == 1:
                        self._add_unit(InfMechInfArt)
                        continue
                elif self._remove_unit_type(InfArt) == 1:
                    if self._remove_unit_type(MechInfantry) == 1:
                        self._add_unit(InfMechInfArt)
                        continue
                    if self._remove_unit_type(Infantry) == 1:
                        self._add_unit(InfArt2)
                        continue
                raise Exception("Error building advanced artillery support")

        # Tactical bomber combined arms
        while self._unit_type_in_list(TacticalBomber) and (
            self._unit_type_in_list(Fighter) or self._unit_type_in_list(Tank)
        ):
            if self._remove_unit_type(TacticalBomber) == 0:
                raise Exception("No tactical bomber removed when it should have been")
            if self._remove_unit_type(Fighter) == 1:
                self._add_unit(FighterTactBomber)
                continue
            if self._remove_unit_type(Tank) == 1:
                self._add_unit(TankTactBomber)
                continue
            raise Exception("No fighter/tank removed when it should have been")
        
        # Conscript pairs
        while self._count_unit_type_in_list(Conscript) > 1:
            if self._remove_unit_type(Conscript, 2) != 2:
                raise Exception("Error while creating conscript combo units")
            self._add_unit(ConscriptPair)

    def _get_granular_unit_list(self):
        unitList = []

        # recursive function to break up combo units into non-combo units
        def breakUpComboUnit(unit):
            if not isinstance(unit, ComboUnit):
                return [unit]
            units = []
            for t in unit.priority:
                subUnit = self._make_unit(t)
                units.extend(breakUpComboUnit(subUnit))
            return units

        for u in self._unit_list:
            if (
                isinstance(u, ComboUnit)
                and not isinstance(u, Battleship)
                and not isinstance(u, Carrier)
            ):
                unitList.extend(breakUpComboUnit(u))
            else:
                unitList.append(u)
        unitList.sort()
        return unitList

    # endregion

    # region Magic methods

    def __str__(self):
        collStr = "Units in collection: " + str(self.currHP()) + "\n"
        unitCount = Counter(type(obj) for obj in self._unit_list)
        for objType, objCount in unitCount.items():
            collStr += objType.__name__ + ": " + str(objCount) + "\n"
        return collStr + "\n"

    # endregion

    # region Collection modification functions

    def reset(self):
        self._unit_list = self._original_unit_list.copy()
        self._loss_priority = self._originalLossPriority.copy()
        self.oldTable = self.old_table_original.copy()

    def define_loss_priority(self, unitTypeList):
        self._loss_priority = unitTypeList
        self._originalLossPriority = unitTypeList.copy()

    # endregion

    # region Printing Functions

    def PrintCollection(self):
        # print(f"Unit Count: {self.currHP()}")
        self._unit_list.sort()
        unitCounter = Counter(type(obj) for obj in self._unit_list)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        print(tabulate(unitArr, headers="firstrow", tablefmt="fancy_grid"))

    def PrintGranularCollection(self):
        unitList = self._get_granular_unit_list()
        unitCounter = Counter(type(obj) for obj in unitList)
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        print(tabulate(unitArr, headers="firstrow", tablefmt="fancy_grid"))

    def PrintCollectionComparison(self):
        self._unit_list.sort()
        # print(f"Current HP: {self.currHP()}")
        unitCounter = Counter(type(obj) for obj in self._get_granular_unit_list())
        unitArr = [["Unit", "Count"]]
        for objType, objCount in unitCounter.items():
            unitArr.append([objType.__name__, objCount])
        df1 = self._unitStrArrToDf(self.oldTable)
        df2 = self._unitStrArrToDf(unitArr)
        dfJoin = pd.concat([df1, df2], axis=1, join="outer")
        printArr = [["Unit", "Before", "After"]]
        df = dfJoin.infer_objects(copy=False).fillna(0).reset_index()
        df.Count = df.Count.astype(int)
        printArr.extend(df.values.tolist())
        print(tabulate(printArr, tablefmt="fancy_grid"))
        self.oldTable = unitArr

    def _unitStrArrToDf(self, arr):
        indexes = [x[0] for x in arr[1:]]
        headers = ["Count"]
        count = [x[1] for x in arr[1:]]
        df = pd.DataFrame(count, index=indexes, columns=headers)
        return df

    def printUnitsAndStrength(self, label="Unit List"):
        for u in self._unit_list:
            print(label)
            if isinstance(u, ComboUnit):
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            else:
                print(type(u).__name__, u.attackStrength, u.defenseStrength)
            print()

    def PrintCollectionStats(self, label: str, attack=True):
        print(label)
        hits = self.expectedHits(attack)
        genStats = {
            "Total Cost": self.current_cost(),
            "HP": self.currHP(),
            "IPC / HP": self.current_cost() / self.currHP(),
            "Expected Hits": self.expectedHits(attack),
            "IPC / Hit": self.current_cost() / hits if hits > 0 else "Infinity",
        }
        print(json.dumps(genStats, indent=4))
        stats = self.collectionEndurance(attack)
        print(json.dumps(stats, indent=4))
        self.PrintCollection()
        print()

    # endregion

    # region Collection stats functions

    def GetCollectionStats(self, isAttack=True):
        hits = self.expectedHits(isAttack)
        genStats = {
            "Total Cost": self.current_cost(),
            "HP": self.currHP(),
            "IPC / HP": self.current_cost() / self.currHP(),
            "Expected Hits": self.expectedHits(isAttack),
            "IPC / Hit": self.current_cost() / hits if hits > 0 else "Infinity",
        }
        stats = self.collectionEndurance(isAttack)
        stats = {**genStats, **stats}
        return stats

    def currHP(self):
        return len(self._get_granular_unit_list())

    def unitCount(self):
        unitCount = 0
        for u in self._unit_list:
            unitCount += len(u.attackStrength)
        return unitCount

    def current_cost(self):
        totalCost = 0
        for u in self._unit_list:
            totalCost += u.cost
        return totalCost

    def expectedHits(self, isAttack=True):
        if len(self._unit_list) > 0:
            dice = [u.unitHitDie(isAttack) for u in self._unit_list]
            return sum(dice).mean()
        else:
            return H({0: 12}).mean()

    def expectedCurve(self, attack=True) -> H:
        if len(self._unit_list) > 0:
            dice = [u.unitHitDie(attack) for u in self._unit_list]
            return sum(dice)
        else:
            return H({0: 12})

    def hitsPerIpc(self, attack=True):
        hits = self.expectedHits(attack)
        cost = self.current_cost()
        return hits / cost * 10

    def collectionEndurance(self, attack=True):
        startingStrength = self.expectedHits(attack)
        if startingStrength == 0:
            rv = {
                "endurance": "N/A",
                "enduranceRatio": "N/A",
                "remainingUnits": "N/A",
                "lostValue": "N/A",
                "remainingValue": "N/A",
                "% Value Lost": "N/A",
                "Lost / Unit": "N/A",
            }
            return rv
        startingUnitCount = self.currHP()
        startingCost = self.current_cost()
        halfStrength = 0.5 * startingStrength
        currStrength = startingStrength
        placeholderUnit = CombatUnit((0, 0))
        while len(self._unit_list) > 0 and currStrength > halfStrength:
            self.takeLosses([Hit(placeholderUnit)])
            currStrength = self.expectedHits(attack)
        endurance = startingUnitCount - self.currHP()
        enduranceRatio = float(endurance) / startingUnitCount
        remainingValue = self.current_cost()
        lostValue = startingCost - remainingValue
        relLostValue = float(lostValue) / startingCost
        costPerLostUnit = float(lostValue) / endurance
        rv = {
            "endurance": endurance,
            "enduranceRatio": f"{enduranceRatio:.1%}",
            "remainingUnits": len(self._unit_list),
            "lostValue": lostValue,
            "remainingValue": remainingValue,
            "% Value Lost": f"{relLostValue:.1%}",
            "Lost / Unit": f"{costPerLostUnit:.2f}",
        }
        self.reset()
        return rv

    def generateHitCurve(self, isAttack=True):
        placeholderUnit = CombatUnit((0, 0))
        curveList = []
        originalHP = self.currHP()
        while len(self._unit_list) > 0:
            curveList.append([self.currHP(), self.expectedHits(isAttack)])
            self.takeLosses([Hit(placeholderUnit)])
        df = pd.DataFrame(curveList, columns=["HP Lost", "Expected Hits"])
        return df

    def valueDelta(self):
        return self.current_cost() - self.original_cost

    # endregion

    # region Combat functions

    def attack(self):
        hits = []
        for u in self._unit_list:
            success = u.attack()
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def firstStrikeAttack(self, opponent):
        hits = []
        for u in [x for x in self._unit_list if isinstance(x, FirstStrikeUnit)]:
            success = u._firstStrikeAttack(opponent)
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def defend(self):
        hits = []
        for u in self._unit_list:
            success = u.defend()
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def firstStrikeDefend(self, opponent):
        hits = []
        for u in [x for x in self._unit_list if isinstance(x, FirstStrikeUnit)]:
            success = u._firstStrikeDefense(opponent)
            if success > 0:
                hits.extend(self._generateHit(u, success))
        return hits

    def _generateHit(self, unit: CombatUnit, hitNumber):
        hits = []
        for i in range(hitNumber):
            hit = Hit(unit)
            # Air vs Sub
            if isinstance(unit, AirUnit) and self._unit_instance_in_list(Destroyer):
                hit.Immune.remove(Submarine)
            hits.append(hit)
        return hits

    def takeLosses(self, hitList):
        leftOver = []
        hitList.sort()
        for hit in hitList:
            if len(self._unit_list) == 0:
                break  # All units killed, no need to apply further hits
            for unitType in self._loss_priority:
                removed = 0
                if self._unitTypeInList(unitType) and hit.UnitTypeIsValidTarget(
                    unitType
                ):
                    removed = self._removeUnitType(unitType, 1)
                    if removed > 0 and issubclass(unitType, ComboUnit):
                        self._correctComboUnits(unitType)
                        self._makeComboUnits()
                if removed > 0:
                    break  # hit was applied, we can break out of the loop
            if removed == 0:
                # Hit wasn't applied (for whatever reason, likely a bug, or the unit list is empty)
                leftOver.append(hit)

        if len(leftOver) > 0:
            print(
                f"{bcolors.RED}ERROR: Units exist outside of the loss priority{
                  bcolors.ENDC}"
            )
            print(leftOver)
            hitList = []  # just keep track of hits that couldn't be applied at all
            for hit in leftOver:
                if len(self._unit_list) == 0:
                    break
                removedUnit = self._applyHit(hit)
                if removedUnit == None:
                    hitList.append(hit)
                if removedUnit != None and isinstance(removedUnit, ComboUnit):
                    self._correctComboUnits(type(removedUnit))
            if len(hitList) > 0:
                print(
                    f"{bcolors.RED}ERROR: Some hits could not be applied{
                      bcolors.ENDC}"
                )
                print(hitList)

    def CanFirstStrike(self):
        return self._unit_instance_in_list(FirstStrikeUnit)

    def _correctComboUnits(self, comboType):
        self._addUnit(comboType.priority[0])
        self._makeComboUnits()

    def _applyHit(self, hit: Hit):
        """Applies the hit with no regard for loss priority"""
        unit = next((x for x in self._unit_list if hit.UnitIsValidTarget(x)), None)
        if unit != None:
            self._unit_list.remove(unit)
        return unit

    def generateUnitDict(self, isLand: bool = True):
        rv = {}
        isNaval = not isLand
        # Need to
        unitList = self._get_granular_unit_list()
        unitCounter = Counter(type(obj) for obj in unitList)
        _unitDict = {}
        for objType, objCount in unitCounter.items():
            _unitDict[objType.__name__] = objCount
        if isLand:
            rv["conscript"] = _unitDict["Conscript"] if "Conscript" in _unitDict.keys() else 0
            rv["aaGun"] = _unitDict["AAA"] if "AAA" in _unitDict.keys() else 0
            rv["infantry"] = _unitDict["Infantry"] if "Infantry" in _unitDict.keys() else 0
            rv["mech_infantry"] = _unitDict["MechInfantry"] if "MechInfantry" in _unitDict.keys() else 0
            rv["artillery"] = _unitDict["Artillery"] if "Artillery" in _unitDict.keys() else 0
            rv["armour"] = _unitDict["Tank"] if "Tank" in _unitDict.keys() else 0
            rv["fighter"] = _unitDict["Fighter"] if "Fighter" in _unitDict.keys() else 0
            rv["tactical_bomber"] = _unitDict["TacticalBomber"] if "TacticalBomber" in _unitDict.keys() else 0
            rv["bomber"] = _unitDict["StratBomber"] if "StratBomber" in _unitDict.keys() else 0
        elif isNaval:
            rv["battleship"] = _unitDict["Battleship"] if "Battleship" in _unitDict.keys() else 0
            rv["carrier"] = _unitDict["Carrier"] if "Carrier" in _unitDict.keys() else 0
            rv["submarine"] = _unitDict["Submarine"] if "Submarine" in _unitDict.keys() else 0
            rv["destroyer"] = _unitDict["Destroyer"] if "Destroyer" in _unitDict.keys() else 0
            rv["cruiser"] = _unitDict["Cruiser"] if "Cruiser" in _unitDict.keys() else 0
            rv["fighter"] = _unitDict["Fighter"] if "Fighter" in _unitDict.keys() else 0
            rv["tactical_bomber"] = _unitDict["TacticalBomber"] if "TacticalBomber" in _unitDict.keys() else 0
            rv["bomber"] = _unitDict["StratBomber"] if "StratBomber" in _unitDict.keys() else 0
            rv["carrier_hit"] = _unitDict["DamagedCarrier"] if "DamagedCarrier" in _unitDict.keys() else 0
            rv["battleship_hit"] = _unitDict["DamagedBattleship"] if "DamagedBattleship" in _unitDict.keys() else 0
        return rv

    def reload_units_from_dict(self, new_units: Dict[str, int]) -> None:
        """
        Clear current units and reload from a dictionary mapping.
        
        Args:
            new_units: Dictionary mapping unit UI names to counts
        """
        self._unit_list.clear()
        for key, value in new_units.items():
            for i in range(value):
                self._add_unit(UNIT_CLASS_MAP[UNIT_UI_MAP[key]])
        self._make_combo_units()


# endregion


if __name__ == "__main__":
    Unit.diceSize = 12
    profileName = "Basic"
    unitListsFile = "unitLists.csv"
    listName = "Attacker"
    profile = pd.read_csv(
        f"UnitProfiles_{profileName}.csv", encoding="utf-8", delimiter=","
    )
    unitList = pd.read_csv(unitListsFile, encoding="utf-8", delimiter=",")
    units = UnitCollection(unitList[listName], profile)
    units.PrintGranularCollection()
    # units.generateHitCurve()

    # profileName = "Basic2"
    # unitListsFile = "unitLists.csv"
    # listName = "Defender"
    # profile = pd.read_csv(
    #     f'UnitProfiles_{profileName}.csv', encoding='utf-8', delimiter=",")
    # unitList = pd.read_csv(unitListsFile, encoding='utf-8', delimiter=",")
    # units = UnitCollection(unitList[listName], profile)
    # units.PrintCollectionStats("Defender", attack=False)
