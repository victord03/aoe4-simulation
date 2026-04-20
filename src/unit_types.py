from enum import Enum



class UnitTypes(Enum):

    # TRIPLE CATEGORIES
    LMI = "Light Melee Infantry"
    LRI = "Light Ranged Infantry"
    HMI = "Heavy Melee Infantry"
    LMC = "Light Melee Cavalry"
    LRC = "Light Ranged Cavalry"
    HMC = "Heavy Melee Cavalry"
    LGI = "Light Gunpowder Infantry"

    # DOUBLE CATEGORIES
    MI = "Melee Infantry"

    # SINGLE CATEGORIES
    ELEPHANT = "Elephant"
    WORKER_ELEPHANT = "Worker Elephant"
    CAVALRY = "Cavalry"
    INFANTRY = "Infantry"
    RANGED = "Ranged"
    MELEE = "Melee"
    HEAVY = "Heavy"
    LIGHT = "Light"
    GUNPOWDER = "Gunpowder"
    SIEGE = "Siege"
    SHIP = "Ship"



BONUS_DAMAGE = {
    "Archer": {UnitTypes.LMI: 4, UnitTypes.LGI: 4},
    "Crossbowman": {UnitTypes.HEAVY: 9},
    "Horseman": {UnitTypes.RANGED: 9, UnitTypes.SIEGE: 9},
    "Spearman": {UnitTypes.CAVALRY: 17, UnitTypes.ELEPHANT: 3, UnitTypes.WORKER_ELEPHANT: 20},
    "Springald": {UnitTypes.MI: 12, UnitTypes.SHIP: 65},
    "Mangonel": {UnitTypes.SHIP: 30, UnitTypes.RANGED: 10},
    "Bombard": {UnitTypes.SHIP: 410, UnitTypes.INFANTRY: 50, UnitTypes.ELEPHANT: 50},
    "Counterweight Trebuchet": {UnitTypes.SHIP: 200}
}



class UnitDamageBonuses:
    damage_bonuses: dict[UnitTypes, int]

    def __init__(self) -> None:
        self.damage_bonuses = dict()

    def add_damage_bonus(self, data_dict: dict[UnitTypes, int]) -> None:
        """Register a bonus damage amount against a given UnitTypes tag.

        {UnitTypes.RANGED: 9, UnitTypes.SIEGE: 9}

        """

        for key, value in data_dict.items():
            self.damage_bonuses[key] = value

    def display_udb(self) -> str:

        text_version = ""

        for key, value in self.damage_bonuses.items():
            text_version += f"{key}: {value} "

        return text_version.strip()




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

    parent_types = {position_map[unit_type[0]], position_map[unit_type[1]], position_map[unit_type[2]]}

    if UnitTypes.MELEE in parent_types and UnitTypes.INFANTRY in parent_types:
        parent_types.add(UnitTypes.MI)

    return parent_types
