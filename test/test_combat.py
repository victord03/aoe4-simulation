import pytest

# TODO pending

"""
from src.combat import deals_bonus_damage
from src.unit_types import UnitTypes, BONUS_DAMAGE
from src.unit import Unit

def test_deals_bonus_damage(create_archer, create_spearman):
    assert deals_bonus_damage(create_archer, create_spearman) == (True, 4)

@pytest.mark.parametrize(
    "attacker_dict, defender_dict, attacker_bonuses",
    [
        (
                {
                    "name": "Spearman",
                    "current_health": 125,
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
                    "production_time": 15
                },

                {

                    "name": "Archer",
                    "current_health": 70,
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
                    "production_time": 15
                },

                (UnitTypes.LMI, 4),
        ),

        (
                {
                    "name": "Archer",
                    "current_health": 70,
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
                    "production_time": 15
                },

                {
                    "name": "Horseman",
                    "current_health": 125,
                    "melee_armor": 0,
                    "ranged_armor": 7,
                    "attack_type": "Melee",
                    "attack_value": 9,
                    "attack_speed": 1.75,
                    "unit_types": {UnitTypes.LMC, UnitTypes.CAVALRY},
                    "unit_line": "Horseman",
                    "food_cost": 100,
                    "wood_cost": 20,
                    "gold_cost": 0,
                    "production_time": 23
                },

                (UnitTypes.LMI, 0)

        ),

        (
                {
                    "name": "Crossbowman",
                    "current_health": 80,
                    "melee_armor": 0,
                    "ranged_armor": 0,
                    "attack_type": "Ranged",
                    "attack_value": 11,
                    "attack_speed": 12.12,
                    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
                    "unit_line": "Crossbowman",
                    "food_cost": 80,
                    "wood_cost": 0,
                    "gold_cost": 40,
                    "production_time": 23
                },

                {
                    "name": "Knight",
                    "current_health": 230,
                    "melee_armor": 4,
                    "ranged_armor": 4,
                    "attack_type": "Melee",
                    "attack_value": 24,
                    "attack_speed": 1.5,
                    "unit_types": {UnitTypes.HMC, UnitTypes.HEAVY, UnitTypes.CAVALRY},
                    "unit_line": "Knight",
                    "food_cost": 140,
                    "wood_cost": 0,
                    "gold_cost": 100,
                    "production_time": 35
                },

                (UnitTypes.HEAVY, 10)

        ),

    ],
    ids=["Spearman vs Archer", "Archer vs Horseman", "Crossbowman vs Knight"]
)
def test_assign_damage(
        attacker_dict,
        defender_dict,
        attacker_bonuses
):

    attacker = Unit(**attacker_dict)

    bonuses = BONUS_DAMAGE.get(attacker.unit_line)

    if bonuses:
        attacker.unit_damage_bonuses.add_damage_bonus(bonuses)

    defender = Unit(**defender_dict)

    defender_starting_hp = defender.current_health

    bonus, amount = deals_bonus_damage(attacker, defender)

    armor = defender.melee_armor if attacker.attack_type == "Melee" else defender.ranged_armor
    ratio = determine_attack_speed_ratio(attacker, defender)

    assert ratio == round(attacker.attack_speed / defender.attack_speed, 2)

    if ratio > 1:
        assign_damage_with_attack_speed_ratio(attacker, defender)
        formula = max(1, round(ratio * ((attacker.attack_value - armor) + amount)))
        assert defender.current_health == defender_starting_hp - formula
    else:
        assign_damage_with_attack_speed_ratio(attacker, defender)
        formula = round((attacker.attack_value - armor) + (bonus * amount))
        assert defender.current_health == defender_starting_hp - max(1, formula)
"""