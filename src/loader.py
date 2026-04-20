

import pandas as pd
from pathlib import Path
from src.unit import Unit
from src.unit_types import UnitTypes, BONUS_DAMAGE, add_parent_unit_types as aput

BASE_DIR = Path(__file__).parent.parent

file_name = "2026-04-20_AoeIV-Excel-Data-Masterfile.xlsx"

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
