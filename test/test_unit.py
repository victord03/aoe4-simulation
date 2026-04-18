import pytest

from src.unit import Unit, Spearman
from src.unit_types import UnitTypes


class TestUnit:

    def test_instance(self) -> None:
        """Test correct instantiation of the object"""

        a = Unit(**Spearman)
        assert isinstance(a, Unit)

    def test_correct_values(self) -> None:
        """Test correct values stored in the attributes"""

        new_value = 1
        test_data = Spearman.copy()
        test_data["melee_armor"] = new_value
        a = Unit(**test_data)

        assert a.melee_armor == new_value

    @pytest.mark.parametrize(
        "class_attribute_to_test",
        [
            "current_health",
            "melee_armor",
            "ranged_armor",
            "attack_value",
            "attack_speed"
        ]
    )
    def test_handle_incorrect_data_types(self, class_attribute_to_test) -> None:
        """Tests incorrect data type for each attribute raises ValueError"""

        new_value = "cannot be coerced into an int"
        test_data = Spearman.copy()
        test_data[class_attribute_to_test] = new_value

        with pytest.raises(ValueError):
            Unit(**test_data)

    def test_complete_unit_instance_with_damage_bonuses_set(self, create_spearman, create_archer):

        assert create_spearman.unit_damage_bonuses.damage_bonuses[UnitTypes.CAVALRY] == 17
        assert create_archer.unit_damage_bonuses.damage_bonuses[UnitTypes.LMI] == 4

