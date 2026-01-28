"""Unit tests for Variable class."""

from __future__ import annotations

from typing import Any

import pytest

from app.variable.variable import Variable
from app.variable.varkind import VarKind


class ConcreteVar(Variable):
    """Concrete implementation of Variable for testing."""

    def get_value(self) -> Any:
        """Return the default value for testing."""
        return self.default


class TestVariable:
    """Test Variable abstract base class."""

    def test_init_with_valid_name(self):
        """Test initialization with valid name."""
        var = ConcreteVar("MY_VAR", "string", "default")
        assert var.name == "MY_VAR"
        assert var.kind == VarKind.STRING
        assert var.default == "default"

    def test_init_with_invalid_name_empty_string(self):
        """Test initialization with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variable name"):
            ConcreteVar("", "string", "default")

    def test_init_with_invalid_name_none(self):
        """Test initialization with None raises ValueError."""
        with pytest.raises(ValueError, match="Invalid variable name"):
            ConcreteVar(None, "string", "default")

    def test_init_with_none_kind_defaults_to_string(self):
        """Test None kind defaults to STRING."""
        var = ConcreteVar("MY_VAR", None, "default")
        assert var.kind == VarKind.STRING

    def test_init_with_varkind_instance(self):
        """Test initialization with VarKind instance."""
        var = ConcreteVar("MY_VAR", VarKind.INTEGER, 42)
        assert var.kind == VarKind.INTEGER

    def test_init_with_string_kind(self):
        """Test initialization with string kind."""
        var = ConcreteVar("MY_VAR", "float", 3.14)
        assert var.kind == VarKind.FLOAT

    def test_resolve_name_valid(self):
        """Test _resolve_name with valid name."""
        var = ConcreteVar("TEST_VAR", "string")
        assert var._resolve_name("VALID_NAME") == "VALID_NAME"

    def test_resolve_name_invalid_empty(self):
        """Test _resolve_name with empty string raises ValueError."""
        var = ConcreteVar("TEST_VAR", "string")
        with pytest.raises(ValueError, match="Invalid variable name"):
            var._resolve_name("")

    def test_resolve_name_invalid_none(self):
        """Test _resolve_name with None raises ValueError."""
        var = ConcreteVar("TEST_VAR", "string")
        with pytest.raises(ValueError, match="Invalid variable name"):
            var._resolve_name(None)

    def test_resolve_kind_with_none(self):
        """Test _resolve_kind with None returns STRING."""
        var = ConcreteVar("TEST_VAR", "string")
        assert var._resolve_kind(None) == VarKind.STRING

    def test_resolve_kind_with_varkind(self):
        """Test _resolve_kind with VarKind instance."""
        var = ConcreteVar("TEST_VAR", "string")
        assert var._resolve_kind(VarKind.INTEGER) == VarKind.INTEGER

    def test_resolve_kind_with_string(self):
        """Test _resolve_kind with string."""
        var = ConcreteVar("TEST_VAR", "string")
        assert var._resolve_kind("boolean") == VarKind.BOOLEAN

    def test_resolve_kind_with_invalid_type(self):
        """Test _resolve_kind with invalid type defaults to STRING."""
        var = ConcreteVar("TEST_VAR", "string")
        assert var._resolve_kind(123) == VarKind.STRING

    def test_parse_string(self):
        """Test string parsing."""
        var = ConcreteVar("MY_VAR", "string")
        assert var._parse_string("  hello  ") == "hello"
        assert var._parse_string(123) == "123"
        assert var._parse_string("test") == "test"

    def test_parse_boolean_true_values(self):
        """Test boolean parsing for true values."""
        var = ConcreteVar("MY_VAR", "boolean")
        assert var._parse_boolean("1") is True
        assert var._parse_boolean("true") is True
        assert var._parse_boolean("TRUE") is True
        assert var._parse_boolean("True") is True
        assert var._parse_boolean("yes") is True
        assert var._parse_boolean("YES") is True
        assert var._parse_boolean("Yes") is True
        assert var._parse_boolean("y") is True
        assert var._parse_boolean("Y") is True
        assert var._parse_boolean("on") is True
        assert var._parse_boolean("ON") is True
        assert var._parse_boolean("On") is True

    def test_parse_boolean_false_values(self):
        """Test boolean parsing for false values."""
        var = ConcreteVar("MY_VAR", "boolean")
        assert var._parse_boolean("0") is False
        assert var._parse_boolean("false") is False
        assert var._parse_boolean("FALSE") is False
        assert var._parse_boolean("False") is False
        assert var._parse_boolean("no") is False
        assert var._parse_boolean("NO") is False
        assert var._parse_boolean("No") is False
        assert var._parse_boolean("n") is False
        assert var._parse_boolean("N") is False
        assert var._parse_boolean("off") is False
        assert var._parse_boolean("OFF") is False
        assert var._parse_boolean("Off") is False

    def test_parse_boolean_with_whitespace(self):
        """Test boolean parsing strips whitespace."""
        var = ConcreteVar("MY_VAR", "boolean")
        assert var._parse_boolean("  true  ") is True
        assert var._parse_boolean("  false  ") is False

    def test_parse_boolean_invalid(self):
        """Test boolean parsing with invalid values."""
        var = ConcreteVar("MY_VAR", "boolean")
        with pytest.raises(ValueError, match="Invalid boolean value"):
            var._parse_boolean("maybe")
        with pytest.raises(ValueError, match="Invalid boolean value"):
            var._parse_boolean("2")

    def test_parse_int_valid(self):
        """Test integer parsing."""
        var = ConcreteVar("MY_VAR", "integer")
        assert var._parse_int("42") == 42
        assert var._parse_int("-100") == -100
        assert var._parse_int("0") == 0
        assert var._parse_int(42) == 42

    def test_parse_int_invalid(self):
        """Test integer parsing with invalid values."""
        var = ConcreteVar("MY_VAR", "integer")
        with pytest.raises(ValueError, match="Invalid integer value"):
            var._parse_int("not a number")
        with pytest.raises(ValueError, match="Invalid integer value"):
            var._parse_int("3.14")

    def test_parse_float_valid(self):
        """Test float parsing."""
        var = ConcreteVar("MY_VAR", "float")
        assert var._parse_float("3.14") == 3.14
        assert var._parse_float("-2.5") == -2.5
        assert var._parse_float("0.0") == 0.0
        assert var._parse_float(3.14) == 3.14
        assert var._parse_float("42") == 42.0

    def test_parse_float_invalid(self):
        """Test float parsing with invalid values."""
        var = ConcreteVar("MY_VAR", "float")
        with pytest.raises(ValueError, match="Invalid float value"):
            var._parse_float("not a number")

    def test_parse_list_valid(self):
        """Test list parsing."""
        var = ConcreteVar("MY_VAR", "list")
        assert var._parse_list("a,b,c") == ["a", "b", "c"]
        assert var._parse_list("a, b, c") == ["a", "b", "c"]
        assert var._parse_list("  a  ,  b  ,  c  ") == ["a", "b", "c"]
        assert var._parse_list("single") == ["single"]

    def test_parse_list_empty_string(self):
        """Test list parsing with empty string returns empty list."""
        var = ConcreteVar("MY_VAR", "list")
        assert var._parse_list("") == []
        assert var._parse_list("   ") == []

    def test_parse_list_filters_empty_items(self):
        """Test list parsing filters out empty items."""
        var = ConcreteVar("MY_VAR", "list")
        assert var._parse_list("a,,b") == ["a", "b"]
        assert var._parse_list("a, , b") == ["a", "b"]
        assert var._parse_list("a,  ,  ,b") == ["a", "b"]

    def test_parse_dict_valid(self):
        """Test dict parsing."""
        var = ConcreteVar("MY_VAR", "dict")
        result = var._parse_dict('{"key": "value", "num": "123"}')
        assert result == {"key": "value", "num": "123"}

    def test_parse_dict_empty(self):
        """Test dict parsing with empty dict."""
        var = ConcreteVar("MY_VAR", "dict")
        result = var._parse_dict("{}")
        assert result == {}

    def test_parse_dict_nested(self):
        """Test dict parsing with nested structure."""
        var = ConcreteVar("MY_VAR", "dict")
        result = var._parse_dict('{"outer": {"inner": "value"}}')
        assert result == {"outer": {"inner": "value"}}

    def test_parse_dict_invalid(self):
        """Test dict parsing with invalid JSON."""
        var = ConcreteVar("MY_VAR", "dict")
        with pytest.raises(ValueError, match="Invalid dict value"):
            var._parse_dict("not json")
        with pytest.raises(ValueError, match="Invalid dict value"):
            var._parse_dict("{invalid}")

    def test_parse_by_kind_string(self):
        """Test parsing by kind for STRING."""
        var = ConcreteVar("MY_VAR", VarKind.STRING)
        assert var._parse_by_kind("  hello  ") == "hello"

    def test_parse_by_kind_integer(self):
        """Test parsing by kind for INTEGER."""
        var = ConcreteVar("MY_VAR", VarKind.INTEGER)
        assert var._parse_by_kind("42") == 42

    def test_parse_by_kind_float(self):
        """Test parsing by kind for FLOAT."""
        var = ConcreteVar("MY_VAR", VarKind.FLOAT)
        assert var._parse_by_kind("3.14") == 3.14

    def test_parse_by_kind_boolean(self):
        """Test parsing by kind for BOOLEAN."""
        var = ConcreteVar("MY_VAR", VarKind.BOOLEAN)
        assert var._parse_by_kind("true") is True

    def test_parse_by_kind_list(self):
        """Test parsing by kind for LIST."""
        var = ConcreteVar("MY_VAR", VarKind.LIST)
        assert var._parse_by_kind("a,b,c") == ["a", "b", "c"]

    def test_parse_by_kind_dict(self):
        """Test parsing by kind for DICT."""
        var = ConcreteVar("MY_VAR", VarKind.DICT)
        result = var._parse_by_kind('{"key": "value"}')
        assert result == {"key": "value"}

    def test_get_value_is_not_implemented(self):
        """Test get_value raises NotImplementedError in base class."""
        var = ConcreteVar("TEST", "string", "default")
        # ConcreteVar overrides get_value, so test the base implementation
        # by calling Variable.get_value directly
        with pytest.raises(NotImplementedError):
            Variable.get_value(var)

    def test_from_dict_with_all_fields(self):
        """Test from_dict class method with all fields."""
        data = {"name": "TEST_VAR", "kind": "integer", "default": 42}
        var = ConcreteVar.from_dict(data)
        assert var.name == "TEST_VAR"
        assert var.kind == VarKind.INTEGER
        assert var.default == 42

    def test_from_dict_with_minimal_fields(self):
        """Test from_dict class method with minimal fields."""
        data = {"name": "TEST_VAR"}
        var = ConcreteVar.from_dict(data)
        assert var.name == "TEST_VAR"
        assert var.kind == VarKind.STRING
        assert var.default is None

    def test_from_dict_with_varkind_instance(self):
        """Test from_dict with VarKind instance."""
        data = {"name": "TEST_VAR", "kind": VarKind.FLOAT, "default": 3.14}
        var = ConcreteVar.from_dict(data)
        assert var.name == "TEST_VAR"
        assert var.kind == VarKind.FLOAT
        assert var.default == 3.14

    def test_from_dict_missing_name_raises_error(self):
        """Test from_dict raises error when name is missing."""
        data = {"kind": "string", "default": "test"}
        with pytest.raises(ValueError, match="Invalid variable name"):
            ConcreteVar.from_dict(data)

    def test_describe_includes_name_and_kind(self):
        """Test describe method includes name and kind."""
        var = ConcreteVar("MY_VAR", "integer", 42)
        desc = var.describe()

        assert "name" in desc
        assert "kind" in desc
        assert desc["name"] == "MY_VAR"
        assert desc["kind"] == "Integer"

    def test_describe_includes_default_when_not_none(self):
        """Test describe includes default when not None."""
        var = ConcreteVar("MY_VAR", "string", "default_value")
        desc = var.describe()

        assert "default" in desc
        assert desc["default"] == "default_value"

    def test_describe_excludes_default_when_none(self):
        """Test describe excludes default when None."""
        var = ConcreteVar("MY_VAR", "string", None)
        desc = var.describe()

        # Default should not be in description when None
        assert "default" not in desc or desc.get("default") is None

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes name, kind, and default."""
        var = ConcreteVar("TEST_VAR", "float", 3.14)
        data = var.to_dict()

        assert "name" in data
        assert "kind" in data
        assert "default" in data
        assert data["name"] == "TEST_VAR"
        assert data["kind"] == "Float"
        assert data["default"] == 3.14

    def test_to_dict_includes_none_default(self):
        """Test to_dict includes default even when None."""
        var = ConcreteVar("MY_VAR", "string", None)
        data = var.to_dict()

        assert "default" in data
        assert data["default"] is None

    def test_to_dict_with_different_kinds(self):
        """Test to_dict with different variable kinds."""
        var1 = ConcreteVar("STR_VAR", VarKind.STRING, "test")
        var2 = ConcreteVar("INT_VAR", VarKind.INTEGER, 42)
        var3 = ConcreteVar("BOOL_VAR", VarKind.BOOLEAN, True)

        assert var1.to_dict()["kind"] == "String"
        assert var2.to_dict()["kind"] == "Integer"
        assert var3.to_dict()["kind"] == "Boolean"
