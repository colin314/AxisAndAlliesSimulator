class Config:
    DICE_SIZE = 6
    ROLL_DELAY_MS = 0
    SUPER_SUB_STRENGTH = 2 if DICE_SIZE == 12 else 1
    defaultLossOrder_Ground = [
        "conscript",
        "aaGun",
        "infantry",
        "mech_infantry",
        "artillery",
        "armour",
        "fighter",
        "tactical_bomber",
        "bomber",
    ]

    defaultLossOrder_Naval = [
        "battleship",
        "carrier",
        "submarine",
        "destroyer",
        "cruiser",
        "fighter",
        "tactical_bomber",
        "bomber",
        "carrier_hit",
        "battleship_hit",
    ]

    powers = [
                "Americans",
                "ANZAC",
                "British",
                "Chinese",
                "French",
                "Germans",
                "Italians",
                "Japanese",
                "Russians",
                "Neutral"
                ]
    
    landUnitDict = {
        0: "infantry",
        1: "mech_infantry",
        2: "artillery",
        3: "armour",
        4: "fighter",
        5: "tactical_bomber",
        6: "bomber",
        7: "aaGun",
        8: "conscript",
    }

    navalUnitDict = {
        0: "submarine",
        1: "destroyer",
        2: "cruiser",
        3: "battleship",
        4: "carrier",
        5: "fighter",
        6: "tactical_bomber",
        7: "bomber",
        8: "battleship_hit",
        9: "carrier_hit",
    }