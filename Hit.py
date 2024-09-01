from Units import *


class Hit:
    def __init__(self, unit:CombatUnit):
        self.Vulnerable = unit.ValidTargets
        self.Immune = unit.ImmuneTargets

    def UnitIsValidTarget(self, unit: Unit):
        isVulnerable = any(isinstance(unit, vType) for vType in self.Vulnerable)
        isImmune = any(isinstance(unit, iType) for iType in self.Immune)
        return isVulnerable and not isImmune
    
    def UnitTypeIsValidTarget(self, unitType):
        isVulnerable = any(issubclass(unitType, vType) for vType in self.Vulnerable)
        isImmune = any(issubclass(unitType, iType) for iType in self.Immune)
        return isVulnerable and not isImmune
