from __future__ import annotations

import pytest

from app.variable.constant import Constant
from app.variable.environ import Environ
from app.variable.setting import Setting
from app.variable.varkind import VarKind


class TestSettingInitialization:
    """Test Setting initialization."""

    def test_init_empty(self):
        """Test initialization with no arguments."""
        setting = Setting()

        assert len(setting.variables) == 0
        assert len(setting.constants) == 0

    def test_init_with_environ_instances(self):
        """Test initialization with Environ instances."""
        var1 = Environ("VAR1", "string", "default1")
        var2 = Environ("VAR2", "integer", 42)

        setting = Setting(variables=[var1, var2])

        assert len(setting.variables) == 2
        assert "VAR1" in setting.variables
        assert "VAR2" in setting.variables
        assert setting.variables["VAR1"] is var1
        assert setting.variables["VAR2"] is var2

    def test_init_with_constant_instances(self):
        """Test initialization with Constant instances."""
        const1 = Constant("CONST1", "value1", "string")
        const2 = Constant("CONST2", 100, "integer")

        setting = Setting(constants=[const1, const2])

        assert len(setting.constants) == 2
        assert "CONST1" in setting.constants
        assert "CONST2" in setting.constants
        assert setting.constants["CONST1"] is const1
        assert setting.constants["CONST2"] is const2

    def test_init_with_variable_dicts(self):
        """Test initialization with variable dictionaries."""
        var_dicts = [
            {"name": "VAR1", "kind": "string", "default": "test"},
            {"name": "VAR2", "kind": "integer", "default": 10},
        ]

        setting = Setting(variables=var_dicts)

        assert len(setting.variables) == 2
        assert isinstance(setting.variables["VAR1"], Environ)
        assert isinstance(setting.variables["VAR2"], Environ)
        assert setting.variables["VAR1"].name == "VAR1"
        assert setting.variables["VAR2"].name == "VAR2"

    def test_init_with_constant_dicts(self):
        """Test initialization with constant dictionaries."""
        const_dicts = [
            {"name": "CONST1", "value": "val1", "kind": "string"},
            {"name": "CONST2", "value": 50, "kind": "integer"},
        ]

        setting = Setting(constants=const_dicts)

        assert len(setting.constants) == 2
        assert isinstance(setting.constants["CONST1"], Constant)
        assert isinstance(setting.constants["CONST2"], Constant)
        assert setting.constants["CONST1"].value == "val1"
        assert setting.constants["CONST2"].value == 50

    def test_init_with_mixed_types(self):
        """Test initialization with both instances and dicts."""
        var_instance = Environ("VAR1", "string", "default")
        var_dict = {"name": "VAR2", "kind": "integer"}

        const_instance = Constant("CONST1", "value", "string")
        const_dict = {"name": "CONST2", "value": 99}

        setting = Setting(
            variables=[var_instance, var_dict],
            constants=[const_instance, const_dict],
        )

        assert len(setting.variables) == 2
        assert len(setting.constants) == 2
        assert setting.variables["VAR1"] is var_instance
        assert isinstance(setting.variables["VAR2"], Environ)
        assert setting.constants["CONST1"] is const_instance
        assert isinstance(setting.constants["CONST2"], Constant)

    def test_init_with_invalid_variable_type(self):
        """Test initialization with invalid variable type raises error."""
        with pytest.raises(TypeError, match="Invalid variable type"):
            Setting(variables=["invalid"])

    def test_init_with_invalid_constant_type(self):
        """Test initialization with invalid constant type raises error."""
        with pytest.raises(TypeError, match="Invalid constant type"):
            Setting(constants=[123])


class TestSettingFromDict:
    """Test Setting.from_dict factory method."""

    def test_from_dict_empty(self):
        """Test from_dict with empty dictionary."""
        setting = Setting.from_dict({})

        assert len(setting.variables) == 0
        assert len(setting.constants) == 0

    def test_from_dict_with_variables(self):
        """Test from_dict with variables."""
        data = {
            "variables": [
                {"name": "VAR1", "kind": "string", "default": "test"},
                {"name": "VAR2", "kind": "integer", "default": 42},
            ]
        }

        setting = Setting.from_dict(data)

        assert len(setting.variables) == 2
        assert "VAR1" in setting.variables
        assert "VAR2" in setting.variables

    def test_from_dict_with_constants(self):
        """Test from_dict with constants."""
        data = {
            "constants": [
                {"name": "CONST1", "value": "value1", "kind": "string"},
                {"name": "CONST2", "value": 100, "kind": "integer"},
            ]
        }

        setting = Setting.from_dict(data)

        assert len(setting.constants) == 2
        assert "CONST1" in setting.constants
        assert "CONST2" in setting.constants

    def test_from_dict_with_both(self):
        """Test from_dict with both variables and constants."""
        data = {
            "variables": [{"name": "VAR1", "kind": "string"}],
            "constants": [{"name": "CONST1", "value": "val1"}],
        }

        setting = Setting.from_dict(data)

        assert len(setting.variables) == 1
        assert len(setting.constants) == 1


class TestSettingAddMethods:
    """Test add_variable and add_constant methods."""

    def test_add_variable(self):
        """Test adding a variable."""
        setting = Setting()
        setting.add_variable("NEW_VAR", "string", "default_value")

        assert "NEW_VAR" in setting.variables
        assert isinstance(setting.variables["NEW_VAR"], Environ)
        assert setting.variables["NEW_VAR"].name == "NEW_VAR"
        assert setting.variables["NEW_VAR"].kind == VarKind.STRING
        assert setting.variables["NEW_VAR"].default == "default_value"

    def test_add_variable_with_varkind(self):
        """Test adding variable with VarKind instance."""
        setting = Setting()
        setting.add_variable("INT_VAR", VarKind.INTEGER, 42)

        assert "INT_VAR" in setting.variables
        assert setting.variables["INT_VAR"].kind == VarKind.INTEGER

    def test_add_variable_overwrites_existing(self):
        """Test adding variable overwrites existing one."""
        setting = Setting()
        setting.add_variable("VAR", "string", "first")
        setting.add_variable("VAR", "integer", 99)

        assert len(setting.variables) == 1
        assert setting.variables["VAR"].kind == VarKind.INTEGER
        assert setting.variables["VAR"].default == 99

    def test_add_constant(self):
        """Test adding a constant."""
        setting = Setting()
        setting.add_constant("NEW_CONST", "constant_value", "string")

        assert "NEW_CONST" in setting.constants
        assert isinstance(setting.constants["NEW_CONST"], Constant)
        assert setting.constants["NEW_CONST"].name == "NEW_CONST"
        assert setting.constants["NEW_CONST"].value == "constant_value"
        assert setting.constants["NEW_CONST"].kind == VarKind.STRING

    def test_add_constant_with_varkind(self):
        """Test adding constant with VarKind instance."""
        setting = Setting()
        setting.add_constant("BOOL_CONST", True, VarKind.BOOLEAN)

        assert "BOOL_CONST" in setting.constants
        assert setting.constants["BOOL_CONST"].kind == VarKind.BOOLEAN
        assert setting.constants["BOOL_CONST"].value is True

    def test_add_constant_overwrites_existing(self):
        """Test adding constant overwrites existing one."""
        setting = Setting()
        setting.add_constant("CONST", "first", "string")
        setting.add_constant("CONST", 100, "integer")

        assert len(setting.constants) == 1
        assert setting.constants["CONST"].value == 100
        assert setting.constants["CONST"].kind == VarKind.INTEGER

    def test_add_multiple_variables_and_constants(self):
        """Test adding multiple variables and constants."""
        setting = Setting()
        setting.add_variable("VAR1", "string")
        setting.add_variable("VAR2", "integer", 10)
        setting.add_constant("CONST1", "val1")
        setting.add_constant("CONST2", 20, "integer")

        assert len(setting.variables) == 2
        assert len(setting.constants) == 2


class TestSettingGetMethods:
    """Test get, get_variable, and get_constant methods."""

    def test_get_from_variable(self, monkeypatch):
        """Test get retrieves from variable."""
        monkeypatch.setenv("TEST_VAR", "env_value")
        setting = Setting()
        setting.add_variable("TEST_VAR", "string")

        value = setting.get("TEST_VAR")

        assert value == "env_value"

    def test_get_from_constant(self):
        """Test get retrieves from constant."""
        setting = Setting()
        setting.add_constant("TEST_CONST", "const_value")

        value = setting.get("TEST_CONST")

        assert value == "const_value"

    def test_get_prefers_variable_over_constant(self, monkeypatch):
        """Test get prefers variable when name exists in both."""
        monkeypatch.setenv("SHARED_NAME", "from_env")
        setting = Setting()
        setting.add_variable("SHARED_NAME", "string")
        setting.add_constant("SHARED_NAME", "from_const")

        value = setting.get("SHARED_NAME")

        assert value == "from_env"

    def test_get_returns_default_when_not_found(self):
        """Test get returns default when name not found."""
        setting = Setting()

        value = setting.get("NONEXISTENT", "default_value")

        assert value == "default_value"

    def test_get_returns_none_when_not_found_and_no_default(self):
        """Test get returns None when not found and no default."""
        setting = Setting()
        value = setting.get("NONEXISTENT")
        assert value is None

    def test_get_variable_returns_environ_instance(self):
        """Test get_variable returns Environ instance."""
        setting = Setting()
        setting.add_variable("VAR", "string", "default")
        var = setting.get("VAR")
        assert var == "default"

    def test_get_variable_returns_none_when_not_found(self):
        """Test get_variable returns None when not found."""
        setting = Setting()

        var = setting.get("NONEXISTENT")

        assert var is None

    def test_get_constant_returns_constant_instance(self):
        """Test get_constant returns Constant instance."""
        setting = Setting()
        setting.add_constant("CONST", "value")
        const = setting.get("CONST")
        assert const == "value"

    def test_get_constant_returns_none_when_not_found(self):
        """Test get_constant returns None when not found."""
        setting = Setting()

        const = setting.get("NONEXISTENT")

        assert const is None


class TestSettingContainerProtocol:
    """Test __contains__, __getitem__, and __len__ methods."""

    def test_contains_with_variable(self):
        """Test 'in' operator with variable."""
        setting = Setting()
        setting.add_variable("VAR", "string")

        assert "VAR" in setting
        assert "OTHER" not in setting

    def test_contains_with_constant(self):
        """Test 'in' operator with constant."""
        setting = Setting()
        setting.add_constant("CONST", "value")

        assert "CONST" in setting
        assert "OTHER" not in setting

    def test_contains_with_both(self):
        """Test 'in' operator with both variable and constant."""
        setting = Setting()
        setting.add_variable("VAR", "string")
        setting.add_constant("CONST", "value")

        assert "VAR" in setting
        assert "CONST" in setting
        assert "OTHER" not in setting

    def test_getitem_with_variable(self, monkeypatch):
        """Test subscript access with variable."""
        monkeypatch.setenv("VAR", "env_value")
        setting = Setting()
        setting.add_variable("VAR", "string")

        value = setting["VAR"]

        assert value == "env_value"

    def test_getitem_with_constant(self):
        """Test subscript access with constant."""
        setting = Setting()
        setting.add_constant("CONST", "const_value")

        value = setting["CONST"]

        assert value == "const_value"

    def test_getitem_raises_keyerror_when_not_found(self):
        """Test subscript access raises KeyError when not found."""
        setting = Setting()

        with pytest.raises(KeyError, match="Name not found: 'NONEXISTENT'"):
            _ = setting["NONEXISTENT"]

    def test_len_empty(self):
        """Test len with empty setting."""
        setting = Setting()

        assert len(setting) == 0

    def test_len_with_variables_only(self):
        """Test len with variables only."""
        setting = Setting()
        setting.add_variable("VAR1", "string")
        setting.add_variable("VAR2", "integer")

        assert len(setting) == 2

    def test_len_with_constants_only(self):
        """Test len with constants only."""
        setting = Setting()
        setting.add_constant("CONST1", "val1")
        setting.add_constant("CONST2", "val2")

        assert len(setting) == 2

    def test_len_with_both(self):
        """Test len with both variables and constants."""
        setting = Setting()
        setting.add_variable("VAR1", "string")
        setting.add_variable("VAR2", "integer")
        setting.add_constant("CONST1", "val1")

        assert len(setting) == 3


class TestSettingDescribeAndToDict:
    """Test describe and to_dict methods."""

    def test_describe_empty(self):
        """Test describe with empty setting."""
        setting = Setting()
        desc = setting.describe()

        assert "variables" in desc
        assert "constants" in desc
        assert len(desc["variables"]) == 0
        assert len(desc["constants"]) == 0

    def test_describe_with_variables(self):
        """Test describe includes variable descriptions."""
        setting = Setting()
        setting.add_variable("VAR1", "string", "default")
        setting.add_variable("VAR2", "integer", 42)

        desc = setting.describe()

        assert len(desc["variables"]) == 2
        assert any(v["name"] == "VAR1" for v in desc["variables"])
        assert any(v["name"] == "VAR2" for v in desc["variables"])

    def test_describe_with_constants(self):
        """Test describe includes constant descriptions."""
        setting = Setting()
        setting.add_constant("CONST1", "value1")
        setting.add_constant("CONST2", 100, "integer")

        desc = setting.describe()

        assert len(desc["constants"]) == 2
        assert any(c["name"] == "CONST1" for c in desc["constants"])
        assert any(c["name"] == "CONST2" for c in desc["constants"])

    def test_to_dict_empty(self):
        """Test to_dict with empty setting."""
        setting = Setting()
        data = setting.to_dict()

        assert "variables" in data
        assert "constants" in data
        assert len(data["variables"]) == 0
        assert len(data["constants"]) == 0

    def test_to_dict_with_variables(self):
        """Test to_dict includes complete variable data."""
        setting = Setting()
        setting.add_variable("VAR1", "string", "default")

        data = setting.to_dict()

        assert len(data["variables"]) == 1
        var_data = data["variables"][0]
        assert var_data["name"] == "VAR1"
        assert "kind" in var_data
        assert "default" in var_data

    def test_to_dict_with_constants(self):
        """Test to_dict includes complete constant data."""
        setting = Setting()
        setting.add_constant("CONST1", "value1")

        data = setting.to_dict()

        assert len(data["constants"]) == 1
        const_data = data["constants"][0]
        assert const_data["name"] == "CONST1"
        assert "value" in const_data
        assert const_data["value"] == "value1"

    def test_to_dict_roundtrip(self):
        """Test to_dict can be used to recreate setting."""
        setting1 = Setting()
        setting1.add_variable("VAR", "string", "default")
        setting1.add_constant("CONST", "value")

        data = setting1.to_dict()
        setting2 = Setting.from_dict(data)

        assert len(setting2.variables) == 1
        assert len(setting2.constants) == 1
        assert "VAR" in setting2.variables
        assert "CONST" in setting2.constants


class TestSettingEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_name_handling(self):
        """Test that empty string names are rejected."""
        setting = Setting()
        # Empty names should raise ValueError
        with pytest.raises(ValueError, match="Invalid variable name"):
            setting.add_variable("", "string", "value")

    def test_special_character_names(self):
        """Test configuration names with special characters."""
        setting = Setting()
        special_names = [
            "VAR-WITH-DASHES",
            "VAR_WITH_UNDERSCORES",
            "VAR.WITH.DOTS",
            "VAR::WITH::COLONS",
        ]

        for name in special_names:
            setting.add_variable(name, "string", "test")
            assert name in setting

    def test_numeric_variable_names(self):
        """Test variables with numeric names."""
        setting = Setting()
        setting.add_variable("123", "string", "numeric_name")
        setting.add_constant("456", "value", "string")

        assert "123" in setting
        assert "456" in setting
        assert setting["123"] == "numeric_name"
        assert setting["456"] == "value"

    def test_large_configuration(self):
        """Test setting with large number of items."""
        setting = Setting()

        # Add 100 variables and constants
        for i in range(100):
            setting.add_variable(f"VAR{i}", "integer", i)
            setting.add_constant(f"CONST{i}", i * 2, "integer")

        assert len(setting) == 200
        assert setting["VAR50"] == 50
        assert setting["CONST50"] == 100

    def test_none_values_in_constants(self):
        """Test constants with None values."""
        setting = Setting()
        setting.add_constant("NULL_CONST", None)

        assert "NULL_CONST" in setting
        assert setting["NULL_CONST"] is None

    def test_complex_types_in_constants(self):
        """Test constants with complex data types."""
        setting = Setting()
        setting.add_constant("DICT_CONST", {"key": "value"}, "dict")
        setting.add_constant("LIST_CONST", "1,2,3", "list")

        assert setting["DICT_CONST"] == {"key": "value"}
        # List is parsed from comma-separated string
        assert setting["LIST_CONST"] == ["1", "2", "3"]

    def test_rebuild_context_after_modifications(self):
        """Test context rebuilds after each modification."""
        setting = Setting()
        initial_context = setting.context.copy()

        setting.add_variable("NEW_VAR", "string", "value1")
        assert "NEW_VAR" in setting.context
        assert setting.context != initial_context

        setting.add_constant("NEW_CONST", "value2")
        assert "NEW_CONST" in setting.context

    def test_override_variable_with_constant_name(self):
        """Test adding constant with same name as variable."""
        setting = Setting()
        setting.add_variable("SHARED", "string", "from_var")
        setting.add_constant("SHARED", "from_const")

        # Both should exist independently
        assert "SHARED" in setting.variables
        assert "SHARED" in setting.constants
        # get() prefers variables
        assert setting.get("SHARED") == "from_var"

    def test_case_sensitivity(self):
        """Test that names are case-sensitive."""
        setting = Setting()
        setting.add_variable("var", "string", "lowercase")
        setting.add_variable("VAR", "string", "uppercase")
        setting.add_variable("Var", "string", "mixedcase")

        assert len(setting.variables) == 3
        assert setting["var"] == "lowercase"
        assert setting["VAR"] == "uppercase"
        assert setting["Var"] == "mixedcase"

    def test_unicode_names_and_values(self):
        """Test Unicode characters in names and values."""
        setting = Setting()
        setting.add_variable("变量", "string", "中文")
        setting.add_constant("🔧", "emoji_value", "string")

        assert "变量" in setting
        assert "🔧" in setting
        assert setting["变量"] == "中文"
        assert setting["🔧"] == "emoji_value"

    def test_whitespace_in_names(self):
        """Test names with whitespace."""
        setting = Setting()
        setting.add_variable("VAR WITH SPACES", "string", "value")

        assert "VAR WITH SPACES" in setting
        assert setting["VAR WITH SPACES"] == "value"

    def test_context_immutability(self):
        """Test that modifying returned context doesn't affect internal state."""
        setting = Setting()
        setting.add_constant("CONST", "original")

        context = setting.get_context()
        context["CONST"] = "modified"

        # Original should be unchanged
        assert setting["CONST"] == "original"

    def test_list_methods_return_copies(self):
        """Test that list methods return new lists."""
        setting = Setting()
        setting.add_variable("VAR", "string")

        list1 = setting.list_variables()
        list2 = setting.list_variables()

        assert list1 is not list2
        assert list1 == list2

    def test_describe_structure(self):
        """Test describe returns expected structure."""
        setting = Setting()
        setting.add_variable("VAR", "string", "default")
        setting.add_constant("CONST", "value")

        desc = setting.describe()

        assert isinstance(desc, dict)
        assert "variables" in desc
        assert "constants" in desc
        assert isinstance(desc["variables"], list)
        assert isinstance(desc["constants"], list)
        assert len(desc["variables"]) == 1
        assert len(desc["constants"]) == 1

    def test_to_dict_structure(self):
        """Test to_dict returns expected structure."""
        setting = Setting()
        setting.add_variable("VAR", "string")
        setting.add_constant("CONST", "value")

        data = setting.to_dict()

        assert isinstance(data, dict)
        assert "variables" in data
        assert "constants" in data
        assert isinstance(data["variables"], list)
        assert isinstance(data["constants"], list)

    def test_from_dict_with_partial_data(self):
        """Test from_dict with only variables or only constants."""
        # Only variables
        setting1 = Setting.from_dict({"variables": [{"name": "VAR", "kind": "string"}]})
        assert len(setting1.variables) == 1
        assert len(setting1.constants) == 0

        # Only constants
        setting2 = Setting.from_dict({"constants": [{"name": "CONST", "value": "val"}]})
        assert len(setting2.variables) == 0
        assert len(setting2.constants) == 1

    def test_from_dict_with_extra_keys(self):
        """Test from_dict ignores extra keys."""
        data = {
            "variables": [{"name": "VAR", "kind": "string"}],
            "constants": [{"name": "CONST", "value": "val"}],
            "extra_key": "should_be_ignored",
        }

        setting = Setting.from_dict(data)
        assert len(setting.variables) == 1
        assert len(setting.constants) == 1

    def test_parent_component_inheritance(self):
        """Test Setting inherits from parent component."""
        from app.base import Component

        parent = Component(name="parent", level="ERROR")
        assert parent.level == "ERROR"

        setting = Setting(parent=parent)
        assert setting.parent is parent
        assert setting.level == "ERROR"
        assert setting.get_root() is parent

    def test_logging_methods_available(self):
        """Test Setting has inherited logging methods."""
        setting = Setting()
        assert hasattr(setting, "log")
        assert hasattr(setting, "info")
        assert hasattr(setting, "debug")
        assert hasattr(setting, "warning")
        assert hasattr(setting, "error")


class TestSettingIntegration:
    """Integration tests for Setting class."""

    def test_complex_configuration(self, monkeypatch):
        """Test complex configuration scenario."""
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("PORT", "8080")

        data = {
            "variables": [
                {"name": "APP_ENV", "kind": "string", "default": "development"},
                {"name": "PORT", "kind": "integer", "default": 3000},
                {"name": "DEBUG", "kind": "boolean", "default": False},
            ],
            "constants": [
                {"name": "APP_NAME", "value": "MyApp", "kind": "string"},
                {"name": "VERSION", "value": "1.0.0", "kind": "string"},
                {"name": "MAX_CONNECTIONS", "value": 100, "kind": "integer"},
            ],
        }

        setting = Setting.from_dict(data)

        # Test variables read from environment
        assert setting["APP_ENV"] == "production"
        assert setting["PORT"] == 8080
        assert setting["DEBUG"] is False  # Uses default

        # Test constants
        assert setting["APP_NAME"] == "MyApp"
        assert setting["VERSION"] == "1.0.0"
        assert setting["MAX_CONNECTIONS"] == 100

        # Test container protocol
        assert len(setting) == 6
        assert "APP_ENV" in setting
        assert "MAX_CONNECTIONS" in setting

    def test_dynamic_configuration_building(self):
        """Test building configuration dynamically."""
        setting = Setting()

        # Add database settings
        setting.add_constant("DB_HOST", "localhost")
        setting.add_constant("DB_PORT", 5432, "integer")
        setting.add_variable("DB_NAME", "string", "mydb")
        setting.add_variable("DB_USER", "string", "admin")

        # Add API settings
        setting.add_constant("API_VERSION", "v1")
        setting.add_variable("API_KEY", "string")

        assert len(setting) == 6
        assert setting.get("DB_HOST") == "localhost"
        assert setting.get("DB_PORT") == 5432

        # Test describe
        desc = setting.describe()
        assert len(desc["variables"]) == 3
        assert len(desc["constants"]) == 3

    def test_configuration_export_and_import(self):
        """Test exporting and importing configuration."""
        # Create initial setting
        setting1 = Setting()
        setting1.add_variable("VAR1", "string", "default1")
        setting1.add_variable("VAR2", "integer", 42)
        setting1.add_constant("CONST1", "value1")
        setting1.add_constant("CONST2", 99, "integer")

        # Export to dict
        exported = setting1.to_dict()

        # Create new setting from exported data
        setting2 = Setting.from_dict(exported)

        # Verify all data transferred
        assert len(setting2.variables) == 2
        assert len(setting2.constants) == 2
        assert "VAR1" in setting2.variables
        assert "VAR2" in setting2.variables
        assert "CONST1" in setting2.constants
        assert "CONST2" in setting2.constants

        # Verify values
        assert setting2.get("VAR1") == "default1"
        assert setting2.get("VAR2") == 42
        assert setting2.get("CONST1") == "value1"
        assert setting2.get("CONST2") == 99
