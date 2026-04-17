from src.unit_damage_bonuses import UnitDamageBonuses as Udb
from src.unit_damage_bonuses import UnitTypes

Spearman = {
    "name": "Spearman",
    "unit_types": {UnitTypes.LMI, UnitTypes.INF},
    "current_health": 125,
    "melee_armor": 0,
    "ranged_armor": 2,
    "attack_type": "Melee",
    "attack_value": 9,
    "attack_speed": 1.75
}

Archer = {
    "name": "Archer",
    "unit_types": {UnitTypes.LRI, UnitTypes.RANG},
    "current_health": 70,
    "melee_armor": 0,
    "ranged_armor": 0,
    "attack_type": "Ranged",
    "attack_value": 5,
    "attack_speed": 1.62
}

Horseman = {
    "name": "Horseman",
    "unit_types": {UnitTypes.LMC, UnitTypes.CAV},
    "current_health": 125,
    "melee_armor": 0,
    "ranged_armor": 2,
    "attack_type": "Melee",
    "attack_value": 9,
    "attack_speed": 1.75
}

Crossbowman = {
    "name": "Crossbowman",
    "unit_types": {UnitTypes.LRI, UnitTypes.RANG},
    "current_health": 80,
    "melee_armor": 0,
    "ranged_armor": 0,
    "attack_type": "Ranged",
    "attack_value": 11,
    "attack_speed": 2.12
}


Knight = {
    "name": "Knight",
    "unit_types": {UnitTypes.HMC, UnitTypes.HVY},
    "current_health": 230,
    "melee_armor": 4,
    "ranged_armor": 4,
    "attack_type": "Melee",
    "attack_value": 24,
    "attack_speed": 1.5
}


class Unit:
    name: str
    unit_types: set[Udb]
    current_health: int
    melee_armor: int
    ranged_armor: int
    attack_type: str
    attack_value: int
    attack_speed: float
    unit_damage_bonuses: Udb

    def __init__(
            self,
            name: str,
            unit_types: set[Udb],
            current_health: int,
            melee_armor: int,
            ranged_armor: int,
            attack_type: str,
            attack_value: float,
            attack_speed: float,
    ) -> None:
        """Initialise a Unit. Numeric stats are coerced to their expected types,
        raising ValueError if the value cannot be converted."""

        self.name = str(name)
        self.unit_types = set(unit_types)
        self.current_health = int(current_health)
        self.melee_armor = int(melee_armor)
        self.ranged_armor = int(ranged_armor)
        self.attack_type = str(attack_type)
        self.attack_value = int(attack_value)
        self.attack_speed = float(attack_speed)
        self.unit_damage_bonuses = Udb()
