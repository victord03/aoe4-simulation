import copy

from src.unit import Unit
from random import randint

from src.loader import load_units


def build_army(unit: Unit, count: int) -> list[Unit]:
    return [copy.deepcopy(unit) for _ in range(count)]

def deals_bonus_damage(attacker: Unit, defender: Unit) -> tuple[bool, int]:
    """Return whether the attacker deals bonus damage to the defender, and the total bonus amount.

    Matches the attacker's damage bonus tags against the defender's unit_types set.
    Multiple matching tags stack (e.g. a unit with both CAV and RANG bonuses applies both
    if the defender carries both tags). Each tag in the attacker's bonus dict is counted once.
    """
    matching = attacker.unit_damage_bonuses.damage_bonuses.keys() & defender.unit_types
    total = sum(attacker.unit_damage_bonuses.damage_bonuses[tag] for tag in matching)
    return bool(matching), total

def assign_damage(attacker: Unit, defender: Unit) -> None:

    bonus, amount = deals_bonus_damage(attacker, defender)
    armor = defender.melee_armor if attacker.attack_type == "Melee" else defender.ranged_armor
    defender.current_health -= max(1, round((attacker.attack_value - armor) + (bonus * amount)))

def calculate_resources(unit_group: list[Unit]) -> dict[str, int]:
    total_resources = dict()
    total_resources["food"] = 0
    total_resources["wood"] = 0
    total_resources["gold"] = 0
    total_resources["sum"] = 0

    for unit in unit_group:
        total_resources["food"] += unit.food_cost
        total_resources["wood"] += unit.wood_cost
        total_resources["gold"] += unit.gold_cost

    total_resources["sum"] = sum([total_resources["food"] + total_resources["wood"] + total_resources["gold"]])

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
        defending_team: list[Unit],
) -> tuple[list[Unit], int]:

    dead = list()
    attack_count = 0

    unit.attack_counter += 1 / unit.attack_speed

    while unit.attack_counter >= 1.0:
        defender_unit = defending_team[randint(0, len(defending_team) - 1)]
        assign_damage(unit, defender_unit)
        unit.attack_counter -= 1.0
        attack_count += 1

        if defender_unit.current_health <= 0 and defender_unit not in dead:
            dead.append(defender_unit)

    return dead, attack_count

def check_for_win(
        defending_team: list[Unit],
        attacking_team: list[Unit],
        attacking_team_name: str,
        defending_team_name: str,
        results: dict) -> bool:

    combat_ends = False

    if len(defending_team) == 0:

        # Winning army name and full Unit list
        results["winning_army_name"] = attacking_team_name
        results["winning_army_units"] = attacking_team

        # Losing army name and full Unit list
        results["losing_army_name"] = defending_team_name
        results["losing_army_units"] = defending_team

        # Relabel total_attacks keys to winning_army / losing_army then remove originals
        results["total_attacks"]["winning_army"] = results["total_attacks"][attacking_team_name]
        results["total_attacks"]["losing_army"] = results["total_attacks"][defending_team_name]
        del results["total_attacks"][attacking_team_name]
        del results["total_attacks"][defending_team_name]

        # Calculate total resource costs (winning army)
        results["resources"]["winning_army"] = results["resources"][attacking_team_name]

        # Calculate total resources costs (losing army)
        results["resources"]["losing_army"] = results["resources"][defending_team_name]

        # Delete duplicate keys
        del results["resources"][attacking_team_name]
        del results["resources"][defending_team_name]

        combat_ends = True

    return combat_ends

def group_fight(
        group_a: list[Unit],
        group_b: list[Unit],
        army_a_name: str,
        army_b_name: str
) -> dict:
    """
    results_dict = {
            "winning_army_name": str,
            "winning_army_units": list[Unit],
            "losing_army_name": str,
            "losing_army_units": list[Unit],
            "combat_turns": int,
            "resources": {
                        "winning_army": {
                                "food": int, "wood": int, "gold": int, "sum":
                        },
                        "losing_army": {
                                "food": int, "wood": int, "gold": int
                        }
            },

    }
    """

    results = dict()

    group_a_ranged_free_turns, group_b_ranged_free_turns = check_for_ranged_extra_attack(group_a, group_b)

    group_a_copy = copy.deepcopy(group_a)
    group_b_copy = copy.deepcopy(group_b)

    round_count = 0

    results["resources"] = {}

    total_resources_team_a = calculate_resources(group_a)

    results["resources"][army_a_name] = {}
    results["resources"][army_a_name]["food"] = total_resources_team_a["food"]
    results["resources"][army_a_name]["wood"] = total_resources_team_a["wood"]
    results["resources"][army_a_name]["gold"] = total_resources_team_a["gold"]
    results["resources"][army_a_name]["sum"] = total_resources_team_a["sum"]

    total_resources_team_b = calculate_resources(group_b)

    results["resources"][army_b_name] = {}
    results["resources"][army_b_name]["food"] = total_resources_team_b["food"]
    results["resources"][army_b_name]["wood"] = total_resources_team_b["wood"]
    results["resources"][army_b_name]["gold"] = total_resources_team_b["gold"]
    results["resources"][army_b_name]["sum"] = total_resources_team_b["sum"]

    combat_end = False
    results["total_attacks"] = {army_a_name: 0, army_b_name: 0}

    while group_a_copy and group_b_copy:

        # Grants 1 free attack to Ranged units in group_a vs Melee units in group_b
        if group_a_ranged_free_turns:

            for unit in group_a_copy:

                if unit.attack_type == "Ranged":

                    dead_in_b, attacks = play_combat_step(
                        unit=unit,
                        defending_team=group_b_copy,
                    )

                    results["total_attacks"][army_a_name] += attacks
                    group_a_ranged_free_turns = False

                    for dead in dead_in_b:
                        group_b_copy.remove(dead)

                    combat_end = check_for_win(
                        defending_team=group_b_copy,
                        attacking_team=group_a,
                        attacking_team_name=army_a_name,
                        defending_team_name=army_b_name,
                        results=results,
                    )

                    if combat_end:
                        break

            if combat_end:
                break

        # Grants 1 free attack to Ranged units in group_b vs Melee units in group_a
        if group_b_ranged_free_turns:

            for unit in group_b_copy:

                if unit.attack_type == "Ranged":

                    dead_in_a, attacks = play_combat_step(
                        unit=unit,
                        defending_team=group_a_copy,
                    )

                    results["total_attacks"][army_b_name] += attacks
                    group_b_ranged_free_turns = False

                    for dead in dead_in_a:
                        group_a_copy.remove(dead)

                    combat_end = check_for_win(
                        defending_team=group_a_copy,
                        attacking_team=group_b,
                        attacking_team_name=army_b_name,
                        defending_team_name=army_a_name,
                        results=results,
                    )

                    if combat_end:
                        break

            if combat_end:
                break

        # Main combat loop step A: each unit from group_a attacks a random unit from group_b
        dead_in_b = list()
        for unit in group_a_copy:

            dead, attacks = play_combat_step(
                unit=unit,
                defending_team=group_b_copy,
            )
            dead_in_b += dead
            results["total_attacks"][army_a_name] += attacks

        for dead in list(dict.fromkeys(dead_in_b)):
            group_b_copy.remove(dead)

        combat_end = check_for_win(
            defending_team=group_b_copy,
            attacking_team=group_a,
            attacking_team_name=army_a_name,
            defending_team_name=army_b_name,
            results=results,
        )

        if combat_end:
            break

        # Main combat loop step B: each unit from group_b attacks a random unit from group_a
        dead_in_a = list()
        for unit in group_b_copy:

            dead, attacks = play_combat_step(
                unit=unit,
                defending_team=group_a_copy,
            )
            dead_in_a += dead
            results["total_attacks"][army_b_name] += attacks

        for dead in list(dict.fromkeys(dead_in_a)):
            group_a_copy.remove(dead)

        combat_end = check_for_win(
            defending_team=group_a_copy,
            attacking_team=group_b,
            attacking_team_name=army_b_name,
            defending_team_name=army_a_name,
            results=results,
        )

        if combat_end:
            break

    return results


if __name__ == "__main__":

    all_units = load_units()

    spearman_army = build_army(all_units["Spearman"], 1)
    spearman_army_name = "Spearmen army"
    yeoman_army = build_army(all_units["Yeoman"], 2)
    yeoman_army_name = "Yeoman army"

    # TODO: divide the number of attacks by the number of units to get number of attacks per unit

    results_dict = group_fight(
        group_a=spearman_army,
        group_b=yeoman_army,
        army_a_name=spearman_army_name,
        army_b_name=yeoman_army_name
    )

    winning_army_name = results_dict["winning_army_name"]
    winning_army = results_dict["winning_army_units"]
    losing_army_name = results_dict["losing_army_name"]
    losing_army = results_dict["losing_army_units"]
    winning_army_attacks = results_dict["total_attacks"]["winning_army"]
    losing_army_attacks = results_dict["total_attacks"]["losing_army"]
    resources = results_dict["resources"]

    print(
        f"The winner is {winning_army_name} ({len(winning_army)} units total) !",
        "\n",
        f"'{winning_army_name}' landed {winning_army_attacks} attacks. '{losing_army_name}' landed {losing_army_attacks} attacks.",
        "\n",
        f"Total resources for '{winning_army_name}': {resources['winning_army']['sum']}",
        "\n",
        f"Total resources for '{losing_army_name}': {resources['losing_army']['sum']}",
    )
