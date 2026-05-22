import copy

from types import SimpleNamespace

from src.unit import Unit
from random import randint

from src.loader import load_units


def compile_results(
        army_a_name: str,
        army_a_original: list[Unit],
        army_a_remaining: list[Unit],
        army_b_name: str,
        army_b_original: list[Unit],
        army_b_remaining: list[Unit],
        winning_army_name: str,
        losing_army_name: str,
        nb_of_attacks_winning_army: int,
        nb_of_attacks_losing_army: int,
) -> SimpleNamespace:

    results = dict()

    winning_army_original = army_a_original if winning_army_name == army_a_name else army_b_original
    winning_army_remaining = army_a_remaining if winning_army_name == army_a_name else army_b_remaining

    # Resources
    results["resources"] = dict()

    # Resources army_a
    results["resources"][army_a_name] = dict()
    total_resources_team_a = calculate_resources(army_a_original)
    results["resources"][army_a_name]["food"] = total_resources_team_a["food"]
    results["resources"][army_a_name]["wood"] = total_resources_team_a["wood"]
    results["resources"][army_a_name]["gold"] = total_resources_team_a["gold"]
    results["resources"][army_a_name]["stone"] = total_resources_team_a["stone"]
    results["resources"][army_a_name]["sum"] = total_resources_team_a["sum"]

    # Resources army_b
    results["resources"][army_b_name] = dict()
    total_resources_team_b = calculate_resources(army_b_original)
    results["resources"][army_b_name]["food"] = total_resources_team_b["food"]
    results["resources"][army_b_name]["wood"] = total_resources_team_b["wood"]
    results["resources"][army_b_name]["gold"] = total_resources_team_b["gold"]
    results["resources"][army_b_name]["stone"] = total_resources_team_b["stone"]
    results["resources"][army_b_name]["sum"] = total_resources_team_b["sum"]

    # Winning army name
    results["winning_army_name"] = winning_army_name

    # Winning army full Unit list
    results["winning_army_original"] = winning_army_original

    # Losing army name
    results["losing_army_name"] = army_b_name if winning_army_name == army_a_name else army_a_name

    # Losing army full Unit list
    results["losing_army_units"] = army_b_original if winning_army_name == army_a_name else army_a_original

    # Document the total number of attacks for both armies
    results["total_attacks"] = dict()
    results["total_attacks"]["winning_army"] = nb_of_attacks_winning_army
    results["total_attacks"]["losing_army"] = nb_of_attacks_losing_army

    # Calculate total resource costs
    results["resources"]["winning_army"] = results["resources"][winning_army_name]
    results["resources"]["losing_army"] = results["resources"][losing_army_name]

    """# Delete duplicate keys
    del results["total_attacks"][army_a_name]
    del results["total_attacks"][army_b_name]
    del results["resources"][army_a_name]
    del results["resources"][army_b_name]"""

    # Post-combat analysis
    results["post_combat_analysis"] = dict()

    # PCA Winning army remaining Unit list
    results["post_combat_analysis"]["winning_army_units_remaining"] = winning_army_remaining

    # PCA Winning army units remaining count
    results["post_combat_analysis"]["winning_army_number_of_units"] = len(winning_army_remaining)


    # PCA Winning army wounded Unit list
    wounded_units = [unit for unit in winning_army_remaining if unit.current_health < unit.health]
    results["post_combat_analysis"]["winning_army_wounded_units"] = wounded_units


    total_hp_remaining_percentage = calculate_surviving_army_hp_percentage_remaining(
        surviving_army=army_a_remaining if winning_army_name == army_a_name else army_b_remaining,
        initial_army=army_a_original if winning_army_name == army_a_name else army_b_original
    )

    results["post_combat_analysis"]["total_hp_remaining_percentage"] = total_hp_remaining_percentage

    return SimpleNamespace(**results)


def build_army(unit: Unit, count: int) -> list[Unit]:
    """Return a list of `count` independent deep-copies of `unit`.

    Each copy has its own HP state, so damage in one fight never bleeds into another.
    """
    return [copy.deepcopy(unit) for _ in range(count)]


def calculate_surviving_army_hp_percentage_remaining(surviving_army: list[Unit], initial_army: list[Unit]) -> float:

    initial_total_army_hp = sum(unit.health for unit in initial_army)
    total_hp_remaining_percentage = round((sum(unit.current_health for unit in surviving_army) / initial_total_army_hp) * 100)

    return total_hp_remaining_percentage


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

def check_for_ranged_extra_attack(attacking_army: list[Unit], defending_army: list[Unit]) -> bool:

    for unit in attacking_army:

        if unit.attack_type == "Ranged":

            for unit_b in defending_army:

                if unit_b.attack_type == "Melee":
                    return True

    return False

def assign_damage(
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
        unit.attack(defender_unit)
        unit.attack_counter -= 1.0
        attack_count += 1

        if defender_unit.current_health <= 0 and defender_unit not in dead:
            dead.append(defender_unit)

    return dead, attack_count

def check_for_win(
        defending_team: list[Unit],
   ) -> bool:
    """Returns True if the defending team has been eliminated, False otherwise."""

    if len(defending_team) == 0:
        return True

    return False


def play_combat_step(
        attack_group_copy: list[Unit],
        defending_group_copy: list[Unit],
        total_attacks: dict,
        attacking_group_name: str,
        ranged_only: bool = False,
) -> bool:
    """Execute one combat step: every unit in `attack_group_copy` attacks a random defender.

    If `ranged_only` is True, only units with attack_type "Ranged" fire — used for the
    one-time free turn granted to ranged units before melee contact. After that single
    free turn, all subsequent calls use the default ranged_only=False.

    Returns True if the defending team is eliminated, False otherwise.
    """
    combat_end = False

    units_to_fire = [u for u in attack_group_copy if u.attack_type == "Ranged"] if ranged_only else attack_group_copy

    for unit in units_to_fire:

        dead_in_defending, attacks = assign_damage(
            unit=unit,
            defending_team=defending_group_copy,
        )

        total_attacks[attacking_group_name] += attacks

        for dead in dead_in_defending:
            defending_group_copy.remove(dead)

        combat_end = check_for_win(defending_team=defending_group_copy)

        if combat_end:
            break

    return combat_end


def group_fight(
        group_a: list[Unit],
        group_b: list[Unit],
        army_a_name: str,
        army_b_name: str
) -> SimpleNamespace:

    group_fight_results = SimpleNamespace()

    group_a_copy = copy.deepcopy(group_a)
    group_b_copy = copy.deepcopy(group_b)

    total_attacks = {army_a_name: 0, army_b_name: 0}

    # One-time free turn for ranged units before melee contact
    if check_for_ranged_extra_attack(group_a_copy, group_b_copy):
        if play_combat_step(group_a_copy, group_b_copy, total_attacks, army_a_name, ranged_only=True):
            return compile_results(
                army_a_original=group_a, army_a_remaining=group_a_copy, army_a_name=army_a_name,
                army_b_original=group_b, army_b_remaining=group_b_copy, army_b_name=army_b_name,
                winning_army_name=army_a_name, losing_army_name=army_b_name,
                nb_of_attacks_winning_army=total_attacks[army_a_name],
                nb_of_attacks_losing_army=total_attacks[army_b_name],
            )

    if check_for_ranged_extra_attack(group_b_copy, group_a_copy):
        if play_combat_step(group_b_copy, group_a_copy, total_attacks, army_b_name, ranged_only=True):
            return compile_results(
                army_a_original=group_a, army_a_remaining=group_a_copy, army_a_name=army_a_name,
                army_b_original=group_b, army_b_remaining=group_b_copy, army_b_name=army_b_name,
                winning_army_name=army_b_name, losing_army_name=army_a_name,
                nb_of_attacks_winning_army=total_attacks[army_b_name],
                nb_of_attacks_losing_army=total_attacks[army_a_name],
            )

    while group_a_copy and group_b_copy:

        combat_end = play_combat_step(
            attack_group_copy=group_a_copy,
            defending_group_copy=group_b_copy,
            total_attacks=total_attacks,
            attacking_group_name=army_a_name,
        )


        if combat_end:

            group_fight_results = compile_results(
                army_a_original=group_a,
                army_a_remaining=group_a_copy,
                army_a_name=army_a_name,
                army_b_original=group_b,
                army_b_remaining=group_b_copy,
                army_b_name=army_b_name,
                winning_army_name=army_a_name,
                losing_army_name=army_b_name,
                nb_of_attacks_winning_army=total_attacks[army_a_name],
                nb_of_attacks_losing_army=total_attacks[army_b_name]
            )
            break

        combat_end = play_combat_step(
            attack_group_copy=group_b_copy,
            defending_group_copy=group_a_copy,
            total_attacks=total_attacks,
            attacking_group_name=army_b_name,
        )

        if combat_end:

            group_fight_results = compile_results(
                army_a_original=group_a,
                army_a_remaining=group_a_copy,
                army_a_name=army_a_name,
                army_b_original=group_b,
                army_b_remaining=group_b_copy,
                army_b_name=army_b_name,
                winning_army_name=army_b_name,
                losing_army_name=army_a_name,
                nb_of_attacks_winning_army=total_attacks[army_b_name],
                nb_of_attacks_losing_army=total_attacks[army_a_name]
            )
            break


    return group_fight_results

# TODO new func, implement
def show_damage(attacker, defender) -> int:
    """Returns a flat number which is the amount of damage the attacker would inflict on the defender"""
    ...


if __name__ == "__main__":

    all_units = load_units()

    army_1 = build_army(all_units["Spearman"], 8)
    army_name_1 = "Spearmen"
    army_2 = build_army(all_units["Archer"], 7)
    army_name_2 = "Archers"

    # TODO run simulations twice, swapping the armies, as 'army_a' always attacks first programmatically
    # TODO need to document remaining hp (flat, %) on the winning army. This indicates how 'close' the battle was.


    battle_results = group_fight(
        group_a=army_1,
        group_b=army_2,
        army_a_name=army_name_1,
        army_b_name=army_name_2
    )

    print("Result dict keys:", list(battle_results.keys()))

    print(
        f"Winning army: {battle_results.winning_army}"
    )
