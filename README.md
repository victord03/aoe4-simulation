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
- [x] `Unit` class with `Unit.attack(defender)` method — bonus damage lookup, armor selection, and minimum-1 damage enforced; `attack_type` validated against `{"Melee", "Ranged"}` on init
- [x] `loader.py` — reads `units.xlsx` and constructs a `dict[str, Unit]` keyed by unit name; skips incomplete rows via `dropna(subset=["Type"])`
- [x] `unit_types.py` — `UnitTypes` enum, `UnitDamageBonuses` class, `add_parent_unit_types()` for automatic tag expansion (3- and 4-letter codes), `BONUS_DAMAGE` dict
- [x] Bonus damage hardcoded in Python per unit line (`BONUS_DAMAGE`), wired into loader
- [x] `group_fight()` — round-based group combat simulation with attack speed counters, ranged free turns, and resource tracking
- [ ] **Post-fight analysis** — add `results["analysis"]` dict with: `"survivors"` (int), `"hp_percent_remaining"` (float, aggregate across all survivors), and `"wounded"` (list of `Unit` where `current_health < health`). Populated by a helper that iterates the winning army's post-battle copy (i.e. `group_a_copy`/`group_b_copy`, not the originals — originals don't carry HP damage). Enables clean/close/overwhelming classification.
- [ ] **Double-run + outcome qualifier** — `group_fight()` must be run twice (swapping attacker order) to neutralise first-strike advantage; the larger the army, the more units it can remove in round 1 before the enemy retaliates. Compare both results and assign a qualifier tag (see *Outcome classification* below).
- [ ] **Refactor `check_for_win` for CQS compliance** — currently violates Command-Query Separation by both mutating `results` and returning a bool. Preferred fix: either (1) return `tuple[bool, dict]` so the signature exposes both outputs explicitly, or (2) return `dict | None` (finalised results or None if fight isn't over) and drop the bool entirely — caller checks `if result := check_for_win(...)`. Option 2 is slightly cleaner. Natural moment to do this is when reworking `group_fight` for the double-run feature.
- [ ] `test_combat.py` — unit tests for `Unit.attack()`, `play_combat_step`, and `group_fight`
- [ ] `test_loader.py` — integration tests that load real data from Excel and validate resulting Unit objects
- [ ] Resource-balanced army matchups
- [ ] CLI interface
- [ ] Composition Quiz mode (easy, medium, hard). Easy is the basic Feudal units triangle, Medium is Castle double comps and Hard is Imperial, all unit comps possible
- [ ] Army cost calculator (input unit names + numbers and get total costs). Potentially also get how many vills / resource are needed to constantly produce (maybe number of production buildings is dynamically calculated - say a target of 3-4 min max for the whole army, therefore get the number of production buildings, therefore get the resources required per min and finally villager count per resource)
- [ ] Visuals using Reflex, displaying a unit image (for each army - maybe up to 3-4 different units, after that use a "several" variant) with a number below it. Then after the battle, display how many are left, a "winner" message above the winning army and "defeated" with "0" above the losing army. Finally display the odds assessment as an overall assessment

## Outcome classification
`group_fight()` is run twice per matchup (A attacks first, then B attacks first) to neutralise first-strike bias. The four possible outcomes:

| Run 1 (A first) | Run 2 (B first) | Qualifier |
|---|---|---|
| A wins | A wins | `"overwhelming"` or `"advantageous"` depending on HP remaining |
| B wins | B wins | same, in B's favour |
| A wins | B wins | **contested** — use `hp_percent_remaining` as tiebreaker; if delta < ~5%, tag as `"even"`, otherwise `"slight_advantage"` to the higher-HP side |

Resource cost is a secondary tiebreaker for the contested case: the army that spent fewer resources and still forced a split result made the better trade.

The threshold for `"even"` (~3–5% HP delta) is a named constant to keep it easy to tune.

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
- **3- or 4-letter compound types** (e.g. `LMI`, `HMC`, `HRGC`): add to `UnitTypes` enum in `unit_types.py` — `add_parent_unit_types()` iterates over every character in the string, so any length is handled automatically.
- **2-letter compound types** (e.g. `MI` — Melee Infantry): add to `UnitTypes` enum AND add a conditional in `add_parent_unit_types()` to assign the tag when both parent tags are present (e.g. `MELEE` + `INFANTRY` → `MI`). Required when a bonus damage entry targets the intersection of two categories rather than either one individually.

## Known limitations
- **Melee crowding:** the simulation assumes all units can attack simultaneously, ignoring the physical surface area constraint of real combat (typically 6-7 units can surround a single target). This is acceptable for the intended 5-15 unit scenarios, but results become increasingly unreliable at larger scales. Modelling this correctly would require positional geometry and is out of scope.

## Potential improvements
- `Unit.__init__` currently validates numeric fields but not `unit_types` — a runtime `isinstance` check against `UnitTypes` would catch type errors early. Longer term, migrating `Unit` to a `@dataclass` with `__post_init__` validation is the cleaner approach and worth considering once the class stabilises.
- `compile_results` currently returns a `SimpleNamespace` for dot-notation access, but IDE autocompletion and static type checking don't work since fields are set dynamically at runtime. Once the `CombatResults` structure stabilises (particularly `resources`), replacing it with a `@dataclass` would restore full tooling support — likely a nested set: `CombatResults`, `ResourceCosts`, `TotalAttacks`, `PostCombatAnalysis`.

## Testing scope and conscious omissions
- `attack_type` is validated against `{"Melee", "Ranged"}` in `Unit.__init__` — any other value silently breaks armor selection in `assign_damage`, making this a real failure mode worth guarding.
- `name`, `attack_type`, and `unit_line` accept any value coercible to `str` and are not tested for invalid input — no realistic bad value exists since the loader sources these from typed Excel cells.
- `food_cost`, `wood_cost`, `gold_cost`, `stone_cost` silently fall back to `0` when the cell is missing or NaN (intentional, many units have no cost in one or more resources). Testing the fallback would be testing Python's `math.isnan`, not application logic.

## Map Resource Dashboard

Browser-based dashboard (Streamlit + Plotly) for analysing AoE4 map resource distributions. Compares a selected map's resources against the median across all maps.

**Stack:** Streamlit, Plotly, pandas — data sourced from `data/Maps.xlsx`

```bash
streamlit run map_dashboard.py
```

### File structure
```
map_dashboard.py      # Streamlit app (entry point, project root)
data/
  Maps.xlsx           # Map resource data (sheet: "Map List")
```

### What's built
- [x] Sidebar map selector and resource category filter (All, Food, Gold, Stone)
- [x] Sidebar map info panel — styled dark box showing map archetype, Sacred Sites / Relics / Trade Posts (with median), Topographically Defensible Spawn, and conditional Water / Shoreline Fish / Deep Water Fish (only shown when present)
- [x] Sidebar map description panel — styled dark box with a free-text description of the map's feel and layout
- [x] Grouped bar chart — selected map vs median, filtered by category, with chart title
- [x] Rankings table — all maps ranked by total resource descending for the selected category
  - Columns: Rank, Name, Total, Median, Flat diff from Median, % diff from Median
  - Selected map pinned in a separate highlighted section above the full table
  - Selected map also highlighted in purple within the full ranked table
  - Thousands separators on all numeric columns

## Unit Upgrade Dashboard

Browser-based dashboard (Streamlit + Plotly) for visualising unit stat progression across upgrade tiers (base → Veteran → Elite). Data sourced from the "Unit Upgrades" sheet of the masterfile.

**Stack:** Streamlit, Plotly, pandas — data sourced from `data/2026-05-22_AoeIV-Excel-Data-Masterfile.xlsx`

```bash
streamlit run unit_upgrades_dashboard.py
```

### File structure
```
unit_upgrades_dashboard.py      # Streamlit app (entry point, project root)
data/
  2026-05-22_AoeIV-Excel-Data-Masterfile.xlsx  # Unit data (sheet: "Unit Upgrades")
```

### What's built
- [x] Sidebar unit selector
- [x] Percentage chart — grouped bars showing HP % and Damage % increase per upgrade tier (Veteran / Elite), with value labels and hover tooltips
- [x] Armor chart — grouped bars showing flat Melee and Ranged Armor increase per upgrade tier; replaced by a "No armor increase" placeholder when all values are zero
- [x] Both charts displayed side by side; units with only Veteran or only Elite upgrades render only the relevant bars
- [x] Median reference bars (Veteran and Elite) shown on both charts for cross-unit comparison
- [x] "No tier upgrades" info message for units with no Veteran or Elite variant

- [x] Radar chart — overlapping polygons for Veteran and Elite upgrade profiles across four axes (HP %, Damage %, Melee Armor, Ranged Armor); each axis normalised 0–100 relative to the maximum value for that stat across all units

### Planned features
- [ ] Line chart — stat gain per resource spent per upgrade tier, showing whether each upgrade is more or less efficient than the previous one
- [ ] Base → Elite overall comparison — additional chart or chart group showing the cumulative stat delta from base to Elite (bypassing the per-tier breakdown), giving a single "total upgrade value" view
- [ ] Flat HP and Damage chart — companion to the existing % chart, showing the absolute HP and damage increases in raw numbers rather than percentages

### Testing scope (`test/test_unit_upgrades_dashboard.py`)
Integration tests hitting the real Excel file — no Streamlit or Plotly calls.
- [ ] **Column existence** — assert that all constants (`VETERAN_PCT_COLS`, `ELITE_PCT_COLS`, `VETERAN_FLAT_COLS`, `ELITE_FLAT_COLS`) are present as actual column names in the loaded DataFrame; catches wrong column name typos silently serving incorrect data
- [ ] **Value extraction** — for a known unit (e.g. Spearman), assert that the extracted veteran HP % value matches the expected value from the spreadsheet; catches wrong column lookups returning plausible-looking but incorrect data
- [ ] **Tier detection** — assert that a Feudal unit (e.g. Spearman) has `veteran=True` and `elite=True`, and that a Castle-age unit with no Veteran row (e.g. Arbaletrier) has `veteran=False` and `elite=True`

## Running tests
```bash
uv run pytest
```

## Type checking
```bash
uv run mypy src
```
