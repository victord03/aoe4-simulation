import pytest

from src.combat import deals_bonus_damage, assign_damage, determine_attack_speed_ratio
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
                    "unit_types": {UnitTypes.LMI, UnitTypes.INFANTRY},
                    "current_health": 125,
                    "melee_armor": 0,
                    "ranged_armor": 2,
                    "attack_type": "Melee",
                    "attack_value": 9,
                    "attack_speed": 1.75,
                    "unit_line": "Spearman"
                },

                {

                    "name": "Archer",
                    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
                    "current_health": 70,
                    "melee_armor": 0,
                    "ranged_armor": 0,
                    "attack_type": "Ranged",
                    "attack_value": 5,
                    "attack_speed": 1.62,
                    "unit_line": "Archer"
                },

                (UnitTypes.LMI, 4),
        ),

        (
                {
                    "name": "Archer",
                    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
                    "current_health": 70,
                    "melee_armor": 0,
                    "ranged_armor": 0,
                    "attack_type": "Ranged",
                    "attack_value": 5,
                    "attack_speed": 1.62,
                    "unit_line": "Archer"
                },

                {
                    "name": "Horseman",
                    "unit_types": {UnitTypes.LMC, UnitTypes.CAVALRY},
                    "current_health": 125,
                    "melee_armor": 0,
                    "ranged_armor": 7,
                    "attack_type": "Melee",
                    "attack_value": 9,
                    "attack_speed": 1.75,
                    "unit_line": "Horseman"
                },

                (UnitTypes.LMI, 0)

        ),

        (
                {
                    "name": "Crossbowman",
                    "unit_types": {UnitTypes.LRI, UnitTypes.RANGED},
                    "current_health": 80,
                    "melee_armor": 0,
                    "ranged_armor": 0,
                    "attack_type": "Ranged",
                    "attack_value": 11,
                    "attack_speed": 12.12,
                    "unit_line": "Crossbowman"
                },

                {
                    "name": "Knight",
                    "unit_types": {UnitTypes.HMC, UnitTypes.HEAVY, UnitTypes.CAVALRY},
                    "current_health": 230,
                    "melee_armor": 4,
                    "ranged_armor": 4,
                    "attack_type": "Melee",
                    "attack_value": 24,
                    "attack_speed": 1.5,
                    "unit_line": "Knight"
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
        assign_damage(attacker, defender)
        formula = max(1, round(ratio * ((attacker.attack_value - armor) + amount)))
        assert defender.current_health == defender_starting_hp - formula
    else:
        assign_damage(attacker, defender)
        formula = round((attacker.attack_value - armor) + (bonus * amount))
        assert defender.current_health == defender_starting_hp - max(1, formula)
