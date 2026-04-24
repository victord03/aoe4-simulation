import copy

from src.unit import Unit
from random import randint

from src.loader import load_units


def build_army(unit: Unit, count: int) -> list[Unit]:
    """Return a list of `count` independent deep-copies of `unit`.

    Each copy has its own HP state, so damage in one fight never bleeds into another.
    """
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
    """Apply one attack's worth of damage from `attacker` to `defender`.

    Selects melee or ranged armor based on the attacker's attack type, adds any
    applicable bonus damage, and enforces a minimum of 1 damage per hit.
    Mutates `defender.current_health` in place.
    """
    bonus, amount = deals_bonus_damage(attacker, defender)
    armor = defender.melee_armor if attacker.attack_type == "Melee" else defender.ranged_armor
    defender.current_health -= max(1, round((attacker.attack_value - armor) + (bonus * amount)))

def calculate_resources(unit_group: list[Unit]) -> dict[str, int]:
    """Sum the resource costs of all units in `unit_group`.

    Returns a dict with keys "food", "wood", "gold", "stone", and "sum"
    (the total across all four resources). Intended to be called before combat
    starts, since units are removed from the list as they die.
    """
    total_resources = dict()
    total_resources["food"] = 0
    total_resources["wood"] = 0
    total_resources["gold"] = 0
    total_resources["stone"] = 0
    total_resources["sum"] = 0

    for unit in unit_group:
        total_resources["food"] += unit.food_cost
        total_resources["wood"] += unit.wood_cost
        total_resources["gold"] += unit.gold_cost
        total_resources["stone"] += unit.stone_cost

    total_resources["sum"] = sum(
        [
            total_resources["food"],
            total_resources["wood"],
            total_resources["gold"],
            total_resources["stone"]
        ]
    )

    return total_resources

def check_for_ranged_extra_attack(group_a: list[Unit], group_b: list[Unit]) -> tuple[bool, bool]:
    """Determine which groups are entitled to a free ranged attack before melee contact.

    A group earns a free attack turn when it contains at least one Ranged unit
    and the opposing group contains at least one Melee unit — reflecting the
    real-game dynamic where ranged armies land shots before the enemy closes in.

    Returns a (group_a_gets_free_turn, group_b_gets_free_turn) boolean tuple.
    """
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
    """Advance `unit`'s attack counter by one time step and fire any pending attacks.

    Each call increments the counter by `1 / attack_speed`. Whenever the counter
    reaches 1.0 or above, the unit attacks a random defender and the counter is
    decremented by 1.0 — allowing fast units to attack multiple times per step.

    Returns a tuple of (newly_dead, attacks_fired). The caller is responsible for
    removing dead units from the defending team after the full round completes.
    """
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
        attacking_team_name: str,
        defending_team_name: str,
        attacking_team: list[Unit],
        results: dict) -> bool:
    """Check whether the defending team has been eliminated and, if so, finalise results.

    When `defending_team` is empty, writes the winner/loser names, unit lists,
    attack counts, and resource costs into `results` under the canonical
    "winning_army" / "losing_army" keys, then deletes the army-name-keyed
    entries that were used during the fight.

    Returns True if combat is over, False otherwise.
    """
    combat_ends = False

    if len(defending_team) == 0:

        # Winning army name and full Unit list
        results["winning_army_name"] = attacking_team_name
        results["winning_army_units"] = attacking_team

        # Losing army name and full Unit list
        results["losing_army_name"] = defending_team_name
        results["losing_army_units"] = defending_team

        # Document the total number of attacks
        nb_of_attacks_attacking_team = results["total_attacks"][attacking_team_name]
        nb_of_attacks_defending_team = results["total_attacks"][defending_team_name]
        results["total_attacks"]["winning_army"] = nb_of_attacks_attacking_team
        results["total_attacks"]["losing_army"] = nb_of_attacks_defending_team

        # Calculate total resource costs
        results["resources"]["winning_army"] = results["resources"][attacking_team_name]
        results["resources"]["losing_army"] = results["resources"][defending_team_name]

        # Delete duplicate keys
        del results["total_attacks"][attacking_team_name]
        del results["total_attacks"][defending_team_name]
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
    results["resources"][army_a_name]["stone"] = total_resources_team_a["stone"]
    results["resources"][army_a_name]["sum"] = total_resources_team_a["sum"]

    total_resources_team_b = calculate_resources(group_b)

    results["resources"][army_b_name] = {}
    results["resources"][army_b_name]["food"] = total_resources_team_b["food"]
    results["resources"][army_b_name]["wood"] = total_resources_team_b["wood"]
    results["resources"][army_b_name]["gold"] = total_resources_team_b["gold"]
    results["resources"][army_b_name]["stone"] = total_resources_team_b["stone"]
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

    army_a = build_army(all_units["Handcannoneer"], 1)
    army_name_a = "Handcannoneers"
    army_b = build_army(all_units["Horseman"], 2)
    army_name_b = "Horsemen"

    # TODO run simulations twice, swapping the armies, as 'army_a' always attacks first programmatically
    # TODO need to document remaining hp (flat, %) on the winning army. This indicates how 'close' the battle was.

    results_dict = group_fight(
        group_a=army_a,
        group_b=army_b,
        army_a_name=army_name_a,
        army_b_name=army_name_b
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
