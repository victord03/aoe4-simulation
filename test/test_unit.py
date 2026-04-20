import pytest

from src.unit import Unit
from src.unit_types import UnitTypes
from test.conftest import Spearman


class TestUnit:

    def test_instance(self, create_spearman) -> None:
        """Test correct instantiation of the object"""

        assert isinstance(create_spearman, Unit)

    def test_correct_values(self, create_spearman) -> None:
        """Test correct values stored in the attributes"""

        new_value = 1
        test_data = create_spearman
        test_data.melee_armor = new_value

        assert test_data.melee_armor == new_value

    @pytest.mark.parametrize(
        "class_attribute_to_test, new_value",
        [
            # ("name", 105.5),
            ("current_health", "N/A"),
            ("melee_armor", "N/A"),
            ("ranged_armor", "N/A"),
            # ("attack_type", 58),
            ("attack_value", "N/A"),
            ("attack_speed", "N/A"),
            # ("unit_types", "N/A"),
            # ("unit_line", "N/A");
            # ("food_cost", "N/A"),
            # ("wood_cost", "N/A"),
            # ("gold_cost", "N/A"),
            # ("production_time", "N/A")
        ],
        ids=[
            # "Incorrect name",
            "Incorrect current_health",
            "Incorrect melee_armor",
            "Incorrect ranged_armor",
            # "Incorrect attack_type",
            "Incorrect attack_value",
            "Incorrect attack_speed",
            # "Incorrect unit_types",
            # "Incorrect unit_line",
            #
            #
            #
            #
        ]
    )  # TODO Need to find a way to still test for the values that can still be coerced in __init__
    def test_handle_incorrect_data_types(self, class_attribute_to_test, new_value) -> None:
        """Tests incorrect data type for each attribute raises ValueError"""

        test_data = Spearman.copy()
        test_data[class_attribute_to_test] = new_value

        with pytest.raises(ValueError):
            Unit(**test_data)

    def test_damage_bonuses(self, create_spearman, create_archer):

        assert create_spearman.unit_damage_bonuses.damage_bonuses[UnitTypes.CAVALRY] == 17
        assert create_archer.unit_damage_bonuses.damage_bonuses[UnitTypes.LMI] == 4

