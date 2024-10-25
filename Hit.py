from Units import *


class Hit:
    def __init__(self, unit:CombatUnit):
        self.Vulnerable = unit.ValidTargets
        self.Immune = unit.ImmuneTargets.copy()

    def UnitIsValidTarget(self, unit: Unit):
        isVulnerable = any(isinstance(unit, vType) for vType in self.Vulnerable)
        isImmune = any(isinstance(unit, iType) for iType in self.Immune)
        return isVulnerable and not isImmune
    
    def UnitTypeIsValidTarget(self, unitType):
        isVulnerable = any(issubclass(unitType, vType) for vType in self.Vulnerable)
        isImmune = any(issubclass(unitType, iType) for iType in self.Immune)
        return isVulnerable and not isImmune
    
    # There is likely a bug here. This method is really janky (weird behavior if there is more than one entry in the vulnerable lists)
    def __lt__(self, that):
        cmpVal = None
        for type in self.Vulnerable:
            for type2 in that.Vulnerable:
                cmpVal = True if issubclass(type,type2) and type != type2 else cmpVal
                cmpVal = False if issubclass(type2, type) and type != type2 else cmpVal
        # If specified vulnerabilities are not subclasses of either, then prioritize hits with immunities.
        if cmpVal == None:
            cmpVal = len(self.Immune) > len(that.Immune)
        return cmpVal
    
    # There is likely a bug here. This method is really janky (weird behavior if there is more than one entry in the vulnerable lists)
    # This is only used if using the key=cmp_to_key method of sorting.
    def cmp(this, that):
        cmpVal = 0
        for type in this.Vulnerable:
            for type2 in that.Vulnerable:
                cmpVal = -1 if issubclass(type,type2) and type != type2 else cmpVal
                cmpVal = 1 if issubclass(type2, type) and type != type2 else cmpVal
        # If specified vulnerabilities are not subclasses of either, then prioritize hits with immunities.
        if cmpVal == 0:
            cmpVal = len(that.Immune) - len(this.Immune)
        return cmpVal
