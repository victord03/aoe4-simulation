import pytest

from src.unit import Unit
from src.unit_types import UnitTypes, BONUS_DAMAGE


Spearman = {
    "name": "Spearman",
    "health": 125,
    "melee_armor": 0,
    "ranged_armor": 2,
    "attack_type": "Melee",
    "attack_value": 9,
    "attack_speed": 1.75,
    "unit_types": {UnitTypes.LMI, UnitTypes.INFANTRY},
    "unit_line": "Spearman",
    "food_cost": 60,
    "wood_cost": 15,
    "gold_cost": 0,
    "stone_cost": 0,
    "production_time": 15
}

Archer = {
    "name": "Archer",
    "health": 70,
    "melee_armor": 0,
    "ranged_armor": 0,
    "attack_type": "Ranged",
    "attack_value": 5,
    "attack_speed": 1.62,
    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
    "unit_line": "Archer",
    "food_cost": 30,
    "wood_cost": 50,
    "gold_cost": 0,
    "stone_cost": 0,
    "production_time": 15
}



@pytest.fixture
def create_spearman() -> Unit:

    a = Unit(**Spearman)

    bonuses = BONUS_DAMAGE.get(a.unit_line)

    if bonuses:
        a.unit_damage_bonuses.add_damage_bonus(bonuses)
    return a

@pytest.fixture
def create_archer() -> Unit:

    a = Unit(**Archer)

    bonuses = BONUS_DAMAGE.get(a.unit_line)

    if bonuses:
        a.unit_damage_bonuses.add_damage_bonus(bonuses)
    return a
