from enum import Enum
# Take in power, spit out the tech they get
class Tech(Enum):
    AdvancedArtillery = 0
    AdvancedMechInfantry = 1
    HeavyBombers = 2
    JetFighters = 3
    SuperSubs = 4
    Radar = 5

class TechMapping():
    def GetTechs(power:str):
        match power.upper():
            case "GERMANS":
                return []
            case "AMERICANS": 
                return []
            case "RUSSIANS":
                return []
            case "BRITISH":
                return []
            case "JAPANESE":
                return [Tech.HeavyBombers]
            case _:
                return []
