from enum import Enum



class UnitTypes(Enum):
    LMI = "Light Melee Infantry"
    LRI = "Light Ranged Infantry"
    HMI = "Heavy Melee Infantry"
    LMC = "Light Melee Cavalry"
    LRC = "Light Ranged Cavalry"
    HMC = "Heavy Melee Cavalry"
    LGI = "Light Gunpowder Infantry"
    ELEPHANT = "Elephant"
    WORKER_ELEPHANT = "Worker Elephant"
    CAVALRY = "Cavalry"
    INFANTRY = "Infantry"
    RANGED = "Ranged"
    MELEE = "Melee"
    HEAVY = "Heavy"
    LIGHT = "Light"
    GUNPOWDER = "Gunpowder"



class UnitDamageBonuses:
    damage_bonuses: dict[UnitTypes, int]

    def __init__(self) -> None:
        self.damage_bonuses = dict()

    def add_damage_bonus(self, against_unit_type: UnitTypes, bonus_amount: int) -> None:
        """Register a bonus damage amount against a given UnitTypes tag."""
        self.damage_bonuses[against_unit_type] = bonus_amount




def add_parent_unit_types(unit_type: str) -> set[UnitTypes]:
    position_map = {
        "L": UnitTypes.LIGHT,
        "H": UnitTypes.HEAVY,
        "R": UnitTypes.RANGED,
        "M": UnitTypes.MELEE,
        "I": UnitTypes.INFANTRY,
        "C": UnitTypes.CAVALRY,
        "G": UnitTypes.GUNPOWDER
    }

    return {position_map[unit_type[0]], position_map[unit_type[1]], position_map[unit_type[2]]}
