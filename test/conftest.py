import pytest

from src.unit import Unit
from src.unit import Spearman, Archer
from src.unit_types import UnitTypes

@pytest.fixture
def create_spearman() -> Unit:
    a = Unit(**Spearman)
    a.unit_damage_bonuses.add_damage_bonus(against_unit_type=UnitTypes.CAVALRY, bonus_amount=17)
    a.unit_damage_bonuses.add_damage_bonus(against_unit_type=UnitTypes.ELEPHANT, bonus_amount=3)
    a.unit_damage_bonuses.add_damage_bonus(against_unit_type=UnitTypes.WORKER_ELEPHANT, bonus_amount=20)
    return a

@pytest.fixture
def create_archer() -> Unit:
    a = Unit(**Archer)
    a.unit_damage_bonuses.add_damage_bonus(against_unit_type=UnitTypes.LMI, bonus_amount=4)
    a.unit_damage_bonuses.add_damage_bonus(against_unit_type=UnitTypes.LGI, bonus_amount=4)
    return a
