import math

from src.unit_types import UnitDamageBonuses as Udb
from src.unit_types import UnitTypes


class Unit:
    name: str

    # STATS
    health: int
    melee_armor: int
    ranged_armor: int
    attack_type: str
    attack_value: int
    attack_speed: float

    # UNIT TYPE
    unit_types: set[UnitTypes]
    unit_damage_bonuses: Udb
    unit_line: str

    # COST
    food_cost: int
    wood_cost: int
    gold_cost: int
    stone_cost: int
    production_time: int

    # COMBAT ATTRIBUTES
    attack_counter: float
    current_health: int

    def __init__(
            self,
            name: str,
            health: int,
            melee_armor: int,
            ranged_armor: int,
            attack_type: str,
            attack_value: float,
            attack_speed: float,
            unit_types: set[UnitTypes],
            unit_line: str,
            food_cost: int,
            wood_cost: int,
            gold_cost: int,
            stone_cost: int,
            production_time: int
    ) -> None:
        """Initialise a Unit. Numeric stats are coerced to their expected types,
        raising ValueError if the value cannot be converted."""

        self.name = str(name).strip()
        self.health = int(health)
        self.melee_armor = int(melee_armor)
        self.ranged_armor = int(ranged_armor)

        if attack_type not in {"Melee", "Ranged"}:
            raise ValueError(f"The `attack_type` has received a non-valid value (received: `{attack_type}`)")

        self.attack_type = str(attack_type).strip()
        self.attack_value = int(attack_value)
        self.attack_speed = float(attack_speed)

        self.unit_types = set(unit_types)
        self.unit_damage_bonuses = Udb()
        self.unit_line = unit_line

        if not isinstance(food_cost, (int, float)) or math.isnan(food_cost):
            food_cost = 0

        if not isinstance(wood_cost, (int, float)) or math.isnan(wood_cost):
            wood_cost = 0

        if not isinstance(gold_cost, (int, float)) or math.isnan(gold_cost):
            gold_cost = 0

        if not isinstance(stone_cost, (int, float)) or math.isnan(stone_cost):
            stone_cost = 0

        self.food_cost = int(food_cost)
        self.wood_cost = int(wood_cost)
        self.gold_cost = int(gold_cost)
        self.stone_cost = int(stone_cost)

        if not isinstance(production_time, (int, float)) or math.isnan(production_time):
            production_time = 0

        self.production_time = int(production_time)

        self.attack_counter = 0.0
        self.current_health = self.health

    def reset_health(self) -> None:
        """Restore current_health to its full value. Useful for re-using a Unit across multiple fights."""
        self.current_health = self.health
