from UnitCollection import UnitCollection
from Units import *


def SimulateBattle(
    attacker: UnitCollection, defender: UnitCollection, printOutcome=False
):
    while attacker.unitCount() > 0 and defender.unitCount() > 0:
        attackerHits = attacker.attack()
        defenderHits = defender.defend()
        attacker.takeLosses(defenderHits)
        defender.takeLosses(attackerHits)
    if printOutcome:
        print("Attacker: ")
        print(str(attacker))
        print("Defender: ")
        print(str(defender))
    return (attacker.unitCount(), defender.unitCount())


if __name__ == "__main__":
    attacker = UnitCollection(
        "./BasicUnitProfile.txt", infantry=2, artillery=2, tanks=1, infantry_mech=2
    )
    defender = UnitCollection(
        "./BasicUnitProfile.txt", infantry=2, artillery=2, tanks=1, infantry_mech=2
    )
    results = []
    for i in range(100):
        (a, d) = SimulateBattle(attacker, defender)
        results.append(1 if a > d else 0)
        attacker.reset()
        defender.reset()
    attackWinRate = float(sum(results)) / float(len(results))
    print(f"attacker wins {attackWinRate:2.2%} percent of the time")
