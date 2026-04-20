# aoe4-simulation
Headless CLI tool for simulating fights between Age of Empires IV units based on their stats (since their content editor is trash).

## What it does
- Models units with stats (HP, armor, attack value, attack speed) and unit type tags
- Resolves bonus damage based on unit type matchups (e.g. Spearman vs Cavalry)
- Simulates 1v1 and small group fights using an attack-speed ratio system — no time engine needed

## Project structure
```
src/
  unit.py                 # Unit class and hardcoded unit stat dicts
  unit_damage_bonuses.py  # UnitDamageBonuses class and UnitTypes enum
  combat.py               # Fight resolution logic
  loader.py               # Excel → Unit objects (in progress)
test/
  conftest.py             # Shared pytest fixtures
  test_unit.py
  test_combat.py
data/
  units.xlsx              # Unit stats and bonus damage tables
```

## Status
- [x] `Unit` class and core combat functions (`assign_damage`, `deals_bonus_damage`, `determine_attack_speed_ratio`)
- [x] `loader.py` — reads `units.xlsx` and constructs a `dict[str, Unit]` keyed by unit name
- [x] `unit_types.py` — `UnitTypes` enum, `UnitDamageBonuses` class, `add_parent_unit_types()` for automatic tag expansion
- [ ] Hardcode bonus damage per unit class in Python
- [ ] 1v1 and group fight simulation
- [ ] Resource-balanced army matchups
- [ ] CLI interface
- [ ] Composition Quiz mode (easy, medium, hard). Easy is the basic Feudal units triangle, Medium is Castle double comps and Hard is Imperial, all unit comps possible

## Design decisions
- Bonus damage is defined in Python, not in the Excel file — it's a unit-class-level property, not per-unit data, and encoding it in code avoids sync issues (missing rows, name mismatches) with the spreadsheet
- `units.xlsx` Sheet "Units" is the authoritative source for unit stats (HP, armor, attack, costs, etc); the "Unit Bonus Damage" sheet has been dropped in favour of the above approach
- Army fights will be balanced by total resource cost rather than unit count — e.g. 1000 food worth of Archers vs 1000 food worth of Knights — to ensure fair matchups (planned feature)

## Group fight simulation design (`simulate_fight`)
```
simulate_fight(army_a: list[Unit], army_b: list[Unit]) -> str:
    for each ranged unit in army_a and army_b:
        if enemy has cavalry: apply 1 free round of damage
        if enemy has infantry: apply 2 free rounds of damage
    while army_a and army_b are not empty:
        each unit in army_a attacks first living unit in army_b
        each unit in army_b attacks first living unit in army_a
        remove dead units from both sides
        increment round counter
    return winner + number of rounds
```

Round-based model: each round, every living unit on side A attacks one target on side B and vice versa simultaneously. Dead units are removed after each round. Repeat until one side is empty.

**Target assignment:** each attacker targets the first living unit in the opposing list, modelling focus-fire (the dominant AoE4 strategy).

**Attack speed:** not applied as a damage scalar in group fights. Instead, the number of rounds is reported as a simulation output — more rounds means more variance from real gameplay (attack speed differences compound over time). This is a useful diagnostic signal rather than a hidden distortion.

**Ranged vs melee compensation:** ranged units get 2 free rounds of damage before melee contact, reflecting the standard real-game dynamic where ranged armies consistently land shots before the enemy closes in.

**Deep-copy requirement:** each Unit instance in an army must be an independent copy so HP changes don't bleed across fights.

## Adding new unit type tags
- **3-letter compound types** (e.g. `LMI`, `HMC`): add to `UnitTypes` enum in `unit_types.py` — `add_parent_unit_types()` handles them automatically via the position map.
- **2-letter compound types** (e.g. `MI` — Melee Infantry): add to `UnitTypes` enum AND add a conditional in `add_parent_unit_types()` to assign the tag when both parent tags are present (e.g. `MELEE` + `INFANTRY` → `MI`). Required when a bonus damage entry targets the intersection of two categories rather than either one individually.

## Potential improvements
- `Unit.__init__` currently validates numeric fields but not `unit_types` — a runtime `isinstance` check against `UnitTypes` would catch type errors early. Longer term, migrating `Unit` to a `@dataclass` with `__post_init__` validation is the cleaner approach and worth considering once the class stabilises.

## Running tests
```bash
uv run pytest
```

## Type checking
```bash
uv run mypy src
```
