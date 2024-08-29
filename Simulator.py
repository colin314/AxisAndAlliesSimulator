from UnitCollection import UnitCollection
from Units import *


def SimulateBattle(
    attacker: UnitCollection,
    defender: UnitCollection,
    printOutcome=False,
    printBattle=False,
):
    round = 0
    while attacker.unitCount() > 0 and defender.unitCount() > 0:
        round += 1
        attackerHits = attacker.attack()
        defenderHits = defender.defend()
        attacker.takeLosses(defenderHits)
        defender.takeLosses(attackerHits)
        if printBattle:
            print(f"Round {round}")
            print(f"Attacker: {attackerHits} hits")
            print(str(attacker))
            print(f"Defender: {defenderHits} hits")
            print(str(defender))
    if printOutcome:
        print(f"Attacker: ")
        print(str(attacker))
        print("Defender: ")
        print(str(defender))
    return (attacker.unitCount(), defender.unitCount())


if __name__ == "__main__":
    print(Unit.diceSize)
    attacker = UnitCollection(
        "./BasicUnitProfile.txt", infantry=8, artillery=4, tanks=0
    )
    # for u in attacker._unitList:
    #     print("Attacker")
    #     if isinstance(u, ComboUnit):
    #         print(type(u).__name__, u.attackVals, u.defenseVals)
    #     else:
    #         print(type(u).__name__, u.attackStrength, u.defenseStrength)
    #     print()
    # defender = UnitCollection("./BasicUnitProfile.txt", infantry=8, artillery=4)
    defender = UnitCollection(
        "./RussianUnitProfile.txt", infantry=12, artillery=4, tanks=0
    )
    # for u in defender._unitList:
    #     print("Defender")
    #     if isinstance(u, ComboUnit):
    #         print(type(u).__name__, u.attackVals, u.defenseVals)
    #     else:
    #         print(type(u).__name__, u.attackStrength, u.defenseStrength)
    results = []
    for i in range(10000):
        (a, d) = SimulateBattle(attacker, defender)
        results.append(1 if a > d else 0)
        attacker.reset()
        defender.reset()
    attackWinRate = float(sum(results)) / float(len(results))
    print(f"attacker wins {attackWinRate:2.2%} percent of the time")
    Unit.diceSize = 6
    print(Unit.diceSize)
    attacker = UnitCollection(
        "./OriginalUnitProfile.txt", infantry=8, artillery=4, tanks=0
    )
    defender = UnitCollection(
        "./OriginalUnitProfile.txt", infantry=8, artillery=4, tanks=0
    )
    results = []
    for i in range(10000):
        (a, d) = SimulateBattle(attacker, defender)
        results.append(1 if a > d else 0)
        attacker.reset()
        defender.reset()
    attackWinRate = float(sum(results)) / float(len(results))
    print(f"attacker wins {attackWinRate:2.2%} percent of the time")
