import copy

from src.unit import Unit
from random import randint


def deals_bonus_damage(attacker: Unit, defender: Unit) -> tuple[bool, int]:
    """Return whether the attacker deals bonus damage to the defender, and the total bonus amount.

    Matches the attacker's damage bonus tags against the defender's unit_types set.
    Multiple matching tags stack (e.g. a unit with both CAV and RANG bonuses applies both
    if the defender carries both tags). Each tag in the attacker's bonus dict is counted once.
    """
    matching = attacker.unit_damage_bonuses.damage_bonuses.keys() & defender.unit_types
    total = sum(attacker.unit_damage_bonuses.damage_bonuses[tag] for tag in matching)
    return bool(matching), total


def assign_damage_with_attack_speed_ratio(attacker: Unit, defender: Unit) -> None:

    bonus, amount = deals_bonus_damage(attacker, defender)
    armor = defender.melee_armor if attacker.attack_type == "Melee" else defender.ranged_armor

    ratio = determine_attack_speed_ratio(attacker, defender)

    if ratio > 1:
        defender.current_health -= max(1, round(ratio * ((attacker.attack_value - armor) + (bonus * amount))))
    else:
        defender.current_health -= max(1, round((attacker.attack_value - armor) + (bonus * amount)))
        # round() is a no-op here (all-integer arithmetic) but kept for consistency with the ratio > 1 branch


def assign_damage(attacker: Unit, defender: Unit) -> None:

    bonus, amount = deals_bonus_damage(attacker, defender)
    armor = defender.melee_armor if attacker.attack_type == "Melee" else defender.ranged_armor
    defender.current_health -= max(1, round((attacker.attack_value - armor) + (bonus * amount)))




def determine_attack_speed_ratio(attacker: Unit, defender: Unit) -> float:
    return round(attacker.attack_speed / defender.attack_speed, 2)


def calculate_resources(unit_group: list[Unit]) -> dict[str, int]:
    total_resources = dict()
    total_resources["Food"] = 0
    total_resources["Wood"] = 0
    total_resources["Gold"] = 0
    total_resources["Sum"] = 0

    for unit in unit_group:
        total_resources["Food"] += unit.food_cost
        total_resources["Wood"] += unit.wood_cost
        total_resources["Gold"] += unit.gold_cost

    # why is sum() giving me a weird message ?
    total_resources["Sum"] = total_resources["Food"] + total_resources["Wood"] + total_resources["Gold"]

    return total_resources



def check_for_ranged_extra_attack(group_a: list[Unit], group_b: list[Unit]) -> tuple[bool, bool]:
    group_a_contains_ranged = False
    group_a_contains_melee = False

    group_b_contains_ranged = False
    group_b_contains_melee = False

    group_a_ranged_free_turns = False
    group_b_ranged_free_turns = False

    for unit in group_a:

        if unit.attack_type == "Ranged":
            group_a_contains_ranged = True
        if unit.attack_type == "Melee":
            group_a_contains_melee = True

    for unit in group_b:

        if unit.attack_type == "Ranged":
            group_b_contains_ranged = True
        if unit.attack_type == "Melee":
            group_b_contains_melee = True

    if group_a_contains_ranged and group_b_contains_melee:
        group_a_ranged_free_turns = True

    if group_b_contains_ranged and group_a_contains_melee:
        group_b_ranged_free_turns = True


    return group_a_ranged_free_turns, group_b_ranged_free_turns


def play_combat_step(
        unit: Unit,
        attacking_team: list[Unit],
        defending_team: list[Unit],
        results: dict,
        round_count: int
):
    unit.attack_counter += unit.attack_speed

    while unit.attack_counter >= 1.0:
        defender_unit = defending_team[randint(0, len(defending_team) - 1)]
        assign_damage(unit, defender_unit)
        unit.attack_counter -= 1.0

        if defender_unit.current_health <= 0:
            defending_team.remove(defender_unit)


def group_fight(group_a: list[Unit], group_b: list[Unit]) -> dict:
    """
    results_dict = {

            "Winning Army": list[Unit],

            "Combat turns": int,

            "Resources": {

                        "group_a": {
                                "food": int, "wood": int, "gold": int, "sum":
                        },

                        "group_b": {

                                "food": int, "wood": int, "gold": int
                        }
            },

    }
    """

    results = dict()

    total_resources_group_a = calculate_resources(group_a)
    total_resources_group_b = calculate_resources(group_b)

    results["Resources"] = {
        "Group A": total_resources_group_a,
        "Group B": total_resources_group_b
    }

    group_a_ranged_free_turns, group_b_ranged_free_turns = check_for_ranged_extra_attack(group_a, group_b)

    group_a_copy = copy.deepcopy(group_a)
    group_b_copy = copy.deepcopy(group_b)

    round_count = 0

    while group_a_copy and group_b_copy:

        if group_a_ranged_free_turns:

            for unit in group_a_copy:

                if unit.attack_type == "Ranged":

                    play_combat_step(
                        unit=unit,
                        attacking_team=group_a_copy,
                        defending_team=group_b_copy,
                        results=results,
                        round_count=round_count
                    )

                    group_a_ranged_free_turns = False

                    if len(group_b_copy) == 0:
                        results["Winner"] = group_a
                        results["Combat Turns"] = round_count + 1

                        break

        if group_b_ranged_free_turns:

            for unit in group_b_copy:

                if unit.attack_type == "Ranged":

                    play_combat_step(
                        unit=unit,
                        attacking_team=group_b_copy,
                        defending_team=group_a_copy,
                        results=results,
                        round_count=round_count
                    )

                    group_a_ranged_free_turns = False

                    if len(group_a_copy) == 0:
                        results["Winner"] = group_b
                        results["Combat Turns"] = round_count + 1

                        break

        dead_in_b = []
        for unit in group_a_copy:

            unit.attack_counter += unit.attack_speed
            while unit.attack_counter >= 1.0 and group_b_copy:
                defender_unit = group_b_copy[randint(0, len(group_b_copy) - 1)]
                assign_damage(unit, defender_unit)
                unit.attack_counter -= 1.0

                if defender_unit.current_health <= 0 and defender_unit not in dead_in_b:
                    dead_in_b.append(defender_unit)

        for dead in dead_in_b:
            group_b_copy.remove(dead)

        if len(group_b_copy) == 0:

            results["Winner"] = group_a
            results["Combat Turns"] = round_count + 1
            break

        dead_in_a = []
        for unit in group_b_copy:

            unit.attack_counter += unit.attack_speed
            while unit.attack_counter >= 1.0 and group_a_copy:
                defender_unit = group_a_copy[randint(0, len(group_a_copy) - 1)]
                assign_damage(unit, defender_unit)
                unit.attack_counter -= 1.0

                if defender_unit.current_health <= 0 and defender_unit not in dead_in_a:
                    dead_in_a.append(defender_unit)

        for dead in dead_in_a:
            group_a_copy.remove(dead)

        if len(group_a_copy) == 0:

            results["Winner"] = group_b
            results["Combat Turns"] = round_count
            break

        round_count += 1


        """each unit in army_a attacks first living unit in army_b
            each unit in army_b attacks first living unit in army_a
            remove dead units from both sides
            increment round counter
        return winner + number of rounds"""


    return results



