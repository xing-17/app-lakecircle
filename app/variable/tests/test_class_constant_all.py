from __future__ import annotations

import pytest

from app.variable.constant import Constant
from app.variable.varkind import VarKind


class TestConstant:
    def test_init_with_string_value(self):
        const = Constant("APP_NAME", "some-app", "string")
        assert const.name == "APP_NAME"
        assert const.kind == VarKind.STRING
        assert const.value == "some-app"

    def test_init_with_integer_value(self):
        const = Constant("MAX_RETRIES", 3, "integer")
        assert const.name == "MAX_RETRIES"
        assert const.kind == VarKind.INTEGER
        assert const.value == 3

    def test_init_with_float_value(self):
        const = Constant("PI", 3.1415926, "float")
        assert const.name == "PI"
        assert const.kind == VarKind.FLOAT
        assert const.value == 3.1415926

    def test_init_with_boolean_value(self):
        const = Constant("DEBUG_MODE", True, "boolean")
        assert const.name == "DEBUG_MODE"
        assert const.kind == VarKind.BOOLEAN
        assert const.value is True

    def test_init_with_list_value(self):
        const = Constant("SUPPORTED_FORMATS", ["csv", "json", "parquet"], "list")
        assert const.name == "SUPPORTED_FORMATS"
        assert const.kind == VarKind.LIST
        assert const.value == ["csv", "json", "parquet"]

    def test_init_with_dict_value(self):
        const = Constant("CONFIG", {"key": "value"}, "dict")
        assert const.name == "CONFIG"
        assert const.kind == VarKind.DICT
        assert const.value == {"key": "value"}

    def test_init_with_none_kind_defaults_to_string(self):
        const = Constant("MY_CONST", "value", None)
        assert const.kind == VarKind.STRING

    def test_init_with_varkind_instance(self):
        const = Constant("VERSION", "2.0.0", VarKind.STRING)
        assert const.kind == VarKind.STRING

    def test_init_without_kind_defaults_to_string(self):
        const = Constant("MY_CONST", "value")
        assert const.kind == VarKind.STRING

    def test_value_parsing_string_from_int(self):
        const = Constant("NUMBER_AS_STRING", 123, "string")
        assert const.value == "123"
        assert isinstance(const.value, str)

    def test_value_parsing_integer_from_string(self):
        const = Constant("PORT", "8080", "integer")
        assert const.value == 8080
        assert isinstance(const.value, int)

    def test_value_parsing_float_from_string(self):
        const = Constant("RATE", "0.95", "float")
        assert const.value == 0.95
        assert isinstance(const.value, float)

    def test_value_parsing_boolean_from_string_true(self):
        for value in ["true", "TRUE", "1", "yes", "y", "on"]:
            const = Constant("ENABLED", value, "boolean")
            assert const.value is True, f"Failed for value: {value}"

    def test_value_parsing_boolean_from_string_false(self):
        for value in ["false", "FALSE", "0", "no", "n", "off"]:
            const = Constant("ENABLED", value, "boolean")
            assert const.value is False, f"Failed for value: {value}"

    def test_value_parsing_list_from_string(self):
        const = Constant("ITEMS", "a,b,c", "list")
        assert const.value == ["a", "b", "c"]

    def test_value_parsing_list_filters_empty_items(self):
        const = Constant("ITEMS", "a,,b, ,c", "list")
        assert const.value == ["a", "b", "c"]

    def test_value_parsing_dict_from_string(self):
        const = Constant("SETTINGS", '{"key": "value"}', "dict")
        assert const.value == {"key": "value"}

    def test_get_value_returns_parsed_value(self):
        const = Constant("COUNT", "42", "integer")
        result = const.get_value("100")
        assert result == 100

    def test_get_value_parses_according_to_kind(self):
        const = Constant("ENABLED", "yes", "boolean")
        result = const.get_value("true")
        assert result is True

    def test_describe_includes_name_and_kind(self):
        const = Constant("VERSION", "2.0.0", "string")
        desc = const.describe()
        assert "name" in desc
        assert "kind" in desc
        assert desc["name"] == "VERSION"
        assert desc["kind"] == "String"

    def test_describe_includes_value_when_not_none(self):
        const = Constant("PORT", 8080, "integer")
        desc = const.describe()
        assert "value" in desc
        assert desc["value"] == 8080

    def test_describe_excludes_value_when_none(self):
        const = Constant("OPTIONAL", None, "string")
        desc = const.describe()
        assert "value" not in desc or desc.get("value") is None

    def test_to_dict_includes_all_fields(self):
        const = Constant("MAX_SIZE", 1000, "integer")
        data = const.to_dict()
        assert "name" in data
        assert "kind" in data
        assert "default" in data
        assert "value" in data
        assert data["name"] == "MAX_SIZE"
        assert data["value"] == 1000

    def test_to_dict_includes_none_value(self):
        const = Constant("NULLABLE", None, "string")
        data = const.to_dict()
        assert "value" in data
        assert data["value"] is None

    def test_constant_inheritance_from_varlike(self):
        from app.variable.variable import Variable

        const = Constant("TEST", "value", "string")
        assert isinstance(const, Variable)

    def test_constant_with_invalid_name_raises_error(self):
        with pytest.raises(ValueError, match="Invalid variable name"):
            Constant("", "value", "string")

    def test_constant_with_invalid_integer_raises_error(self):
        with pytest.raises(ValueError, match="Invalid integer value"):
            Constant("MAX_RETRIES", "not_a_number", "integer")

    def test_constant_with_invalid_float_raises_error(self):
        with pytest.raises(ValueError, match="Invalid float value"):
            Constant("RATE", "not_a_number", "float")

    def test_constant_with_invalid_boolean_raises_error(self):
        with pytest.raises(ValueError, match="Invalid boolean value"):
            Constant("ENABLED", "maybe", "boolean")

    def test_constant_with_invalid_dict_raises_error(self):
        with pytest.raises(ValueError, match="Invalid dict value"):
            Constant("CONFIG", "not json", "dict")

    def test_multiple_constants_with_different_types(self):
        const1 = Constant("NAME", "App", "string")
        const2 = Constant("VERSION", "1.0", "string")
        const3 = Constant("MAX_USERS", 100, "integer")
        const4 = Constant("ENABLED", True, "boolean")
        assert const1.value == "App"
        assert const2.value == "1.0"
        assert const3.value == 100
        assert const4.value is True

    def test_constant_value_immutability_concept(self):
        const = Constant("IMMUTABLE", "original", "string")
        value1 = const.value
        value2 = const.value
        assert value1 == value2 == "original"

    def test_from_dict_creates_constant(self):
        data = {"name": "API_VERSION", "kind": "string"}
        const = Constant.from_dict(data)
        assert isinstance(const, Constant)
        assert const.name == "API_VERSION"
        assert const.kind == VarKind.STRING

    def test_constant_with_complex_list(self):
        const = Constant("ENDPOINTS", ["api/v1", "api/v2", "health"], "list")
        assert len(const.value) == 3
        assert "api/v1" in const.value

    def test_constant_with_nested_dict(self):
        config = {"db": {"host": "localhost", "port": 5432}}
        const = Constant("DB_CONFIG", config, "dict")
        assert const.value["db"]["host"] == "localhost"
        assert const.value["db"]["port"] == 5432
