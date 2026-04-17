from enum import Enum

class UnitTypes(Enum):
    LMI = "Light Melee Infantry"
    LRI = "Light Ranged Infantry"
    HMI = "Heavy Melee Infantry"
    LMC = "Light Melee Cavalry"
    LRC = "Light Ranged Cavalry"
    HMC = "Heavy Melee Cavalry"
    LGI = "Light Gunpowder Infantry"
    ELE = "Elephant"
    WRKELE = "Worker Elephant"
    CAV = "Cavalry"
    INF = "Infantry"
    RANG = "Ranged"
    HVY = "Heavy"

class UnitDamageBonuses:
    damage_bonuses: dict[UnitTypes, int]

    def __init__(self) -> None:
        self.damage_bonuses = dict()

    def add_damage_bonus(self, against_unit_type: UnitTypes, bonus_amount: int) -> None:
        """Register a bonus damage amount against a given UnitTypes tag."""
        self.damage_bonuses[against_unit_type] = bonus_amount
