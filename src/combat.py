from src.unit import Unit


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

    ratio = determine_attack_speed_ratio(attacker, defender)

    if ratio > 1:
        defender.current_health -= max(1, round(ratio * ((attacker.attack_value - armor) + (bonus * amount))))
    else:
        defender.current_health -= max(1, round((attacker.attack_value - armor) + (bonus * amount)))
        # round() is a no-op here (all-integer arithmetic) but kept for consistency with the ratio > 1 branch



def determine_attack_speed_ratio(attacker: Unit, defender: Unit) -> float:
    return round(attacker.attack_speed / defender.attack_speed, 2)
