

import pandas as pd
from pathlib import Path
from src.unit import Unit
from src.unit_types import UnitTypes, BONUS_DAMAGE, add_parent_unit_types as aput

BASE_DIR = Path(__file__).parent.parent

file_name = "2026-04-24_AoeIV-Excel-Data-Masterfile.xlsx"

def open_excel() -> pd.DataFrame:
    """Read the 'Units' sheet from the master Excel file and return it as a DataFrame."""
    return pd.read_excel(BASE_DIR / "data" / file_name, sheet_name="Units")


def debug_prints() -> None:
    """Print diagnostic information about the raw DataFrame — columns, shape, dtypes, and unique Type values."""
    df = open_excel()

    df.head()

    print("\nColumns: ", df.columns)

    print("\nShape: ", df.shape)

    print("\nColumn data types", df.dtypes)

    print("\nInfo")

    df.info()

    print(df["Type"].unique())


def load_units() -> dict[str, Unit]:
    """Load all units from the Excel file and return them as a dict keyed by unit name.

    Rows with a missing 'Type' cell are skipped (e.g. units whose data has not yet
    been populated). Bonus damage entries from `BONUS_DAMAGE` are wired in by unit-line
    after each Unit is constructed.
    """
    df = open_excel()
    df = df.dropna(subset=["Type"])
    loaded_units = dict()

    for _, row in df.iterrows():
        loaded_units[row["Name"]] = Unit(
            name=row["Name"],
            health=row["Health"],
            melee_armor=row["Melee"],
            ranged_armor=row["Ranged"],
            attack_type=row["Attack Type"],
            attack_value=row["Attack"],
            attack_speed=row["Att. Sp."],
            unit_types={UnitTypes[row["Type"]]} | aput(row["Type"]),
            unit_line=row["Unit-line"],
            food_cost=row["Food"],
            wood_cost=row["Wood"],
            gold_cost=row["Gold"],
            stone_cost=row["Stone"],
            production_time=row["Time"]
        )

        bonuses = BONUS_DAMAGE.get(row["Unit-line"])

        if bonuses:
            loaded_units[row["Name"]].unit_damage_bonuses.add_damage_bonus(bonuses)


    return loaded_units



if __name__ == "__main__":

    dict_units = load_units()
    print("Dict len:", len(dict_units.keys()))
    print(
        f"Spearman\n\t UdB: '{dict_units['Spearman'].unit_damage_bonuses.display_udb()}'.")

    knight = dict_units["Knight"]

    print(
        f"Knight ({knight.food_cost}F / {knight.gold_cost}G), {knight.production_time} seconds."
    )

    handcannon = dict_units["Gilded Handcannoneer"]

    print(
        f"Gilded Handcannoneer Types:{handcannon.unit_types} \n {handcannon.unit_damage_bonuses.display_udb()}"
    )

    black_rider = dict_units["Black Rider"]

    print(
        f"Black rider types: {black_rider.unit_types}"
    )

