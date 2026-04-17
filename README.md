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

## Running tests
```bash
uv run pytest
```

## Type checking
```bash
uv run mypy src
```
