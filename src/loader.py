import pandas as pd
from pathlib import Path
from src.unit import Unit
from src.unit_types import UnitTypes, add_parent_unit_types as aput

BASE_DIR = Path(__file__).parent.parent

file_name = "2026-04-18_AoeIV-Excel-Data-Masterfile.xlsx"

def open_excel() -> pd.DataFrame:
    return pd.read_excel(BASE_DIR / "data" / file_name, sheet_name="Units")


def debug_prints() -> None:
    df = open_excel()

    df.head()

    print("\nColumns: ", df.columns)

    print("\nShape: ", df.shape)

    print("\nColumn data types", df.dtypes)

    print("\nInfo")

    df.info()

    print(df["Type"].unique())


def load_units() -> dict[str, Unit]:
    df = open_excel()
    loaded_units = dict()

    for _, row in df.iterrows():
        loaded_units[row["Name"]] = Unit(
            name=row["Name"],
            unit_types={UnitTypes[row["Type"]]} | aput(row["Type"]),
            current_health=row["Health"],
            melee_armor=row["Melee"],
            ranged_armor=row["Ranged"],
            attack_type="Ranged" if "R" in row["Type"][1] else "Melee",  # Patch due to missing column. Will be amended.
            attack_value=row["Attack"],
            attack_speed=row["Att. Sp."]
        )

    return loaded_units



if __name__ == "__main__":

    dict_units = load_units()
    print("Dict len:", len(dict_units.keys()))
    print(f"key=Crossbowman, HP is {dict_units['Crossbowman'].current_health} and Attack value is {dict_units['Crossbowman'].attack_value}. Attack type is {dict_units['Crossbowman'].attack_type}")
