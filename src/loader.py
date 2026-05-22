

import pandas as pd
from pathlib import Path
from src.unit import Unit
from src.unit_types import UnitTypes, BONUS_DAMAGE, add_parent_unit_types as aput

BASE_DIR = Path(__file__).parent.parent

units_file = "2026-05-22_AoeIV-Excel-Data-Masterfile.xlsx"
maps_file = "Maps.xlsx"

def open_excel(file_name: str, sheet_name: str, main_column: str) -> pd.DataFrame:
    """Read any sheet from and return it as a DataFrame, removing empty rows of the selected 'main_column'."""
    df = pd.read_excel(BASE_DIR / "data" / file_name, sheet_name=sheet_name)
    return df.dropna(subset=[main_column])


def debug_prints(data_frame: pd.DataFrame) -> None:
    """Print diagnostic information about the raw DataFrame — columns, shape, dtypes."""

    data_frame.head()

    print("\nColumns: ", data_frame.columns)

    print("\nShape: ", data_frame.shape)

    print("\nColumn data types", data_frame.dtypes)

    print("\nInfo")

    data_frame.info()


def load_units(file, sheet, column) -> dict[str, Unit]:
    """Load all units from the Excel file and return them as a dict keyed by unit name.

    Rows with a missing 'Type' cell are skipped (e.g. units whose data has not yet
    been populated). Bonus damage entries from `BONUS_DAMAGE` are wired in by unit-line
    after each Unit is constructed.
    """
    df = open_excel(file, sheet, column)
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

    """dict_units = load_units(units_file, "Units", "Name")
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
    )"""


