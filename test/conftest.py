import pytest

from src.unit import Unit
from src.unit_types import UnitTypes, BONUS_DAMAGE


Spearman = {
    "name": "Spearman",
    "unit_types": {UnitTypes.LMI, UnitTypes.INFANTRY},
    "current_health": 125,
    "melee_armor": 0,
    "ranged_armor": 2,
    "attack_type": "Melee",
    "attack_value": 9,
    "attack_speed": 1.75,
    "unit_line": "Spearman",
}

Archer = {
    "name": "Archer",
    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
    "current_health": 70,
    "melee_armor": 0,
    "ranged_armor": 0,
    "attack_type": "Ranged",
    "attack_value": 5,
    "attack_speed": 1.62,
    "unit_line": "Archer"
}

Horseman = {
    "name": "Horseman",
    "unit_types": {UnitTypes.LMC, UnitTypes.CAVALRY},
    "current_health": 125,
    "melee_armor": 0,
    "ranged_armor": 2,
    "attack_type": "Melee",
    "attack_value": 9,
    "attack_speed": 1.75,
    "unit_line": "Horseman"
}

Crossbowman = {
    "name": "Crossbowman",
    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
    "current_health": 80,
    "melee_armor": 0,
    "ranged_armor": 0,
    "attack_type": "Ranged",
    "attack_value": 11,
    "attack_speed": 2.12,
    "unit_line": "Crossbowman"
}


Knight = {
    "name": "Knight",
    "unit_types": {UnitTypes.HMC, UnitTypes.HEAVY},
    "current_health": 230,
    "melee_armor": 4,
    "ranged_armor": 4,
    "attack_type": "Melee",
    "attack_value": 24,
    "attack_speed": 1.5,
    "unit_line": "Knight"
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
