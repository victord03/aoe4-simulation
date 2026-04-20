from src.unit_types import UnitDamageBonuses as Udb
from src.unit_types import UnitTypes


class Unit:
    name: str
    unit_types: set[UnitTypes]
    current_health: int
    melee_armor: int
    ranged_armor: int
    attack_type: str
    attack_value: int
    attack_speed: float
    unit_damage_bonuses: Udb
    unit_line: str

    def __init__(
            self,
            name: str,
            unit_types: set[UnitTypes],
            current_health: int,
            melee_armor: int,
            ranged_armor: int,
            attack_type: str,
            attack_value: float,
            attack_speed: float,
            unit_line: str
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
        self.unit_line = unit_line
