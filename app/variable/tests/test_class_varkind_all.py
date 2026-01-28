"""Unit tests for VarKind class."""

from __future__ import annotations

from app.variable.varkind import VarKind


class TestVarKind:
    """Test VarKind enumeration."""

    def test_from_str_case_insensitive(self):
        """Test case-insensitive string conversion."""
        assert VarKind.from_str("integer") == VarKind.INTEGER
        assert VarKind.from_str("INTEGER") == VarKind.INTEGER
        assert VarKind.from_str("Integer") == VarKind.INTEGER

    def test_from_str_defaults_to_string(self):
        """Test unknown strings default to STRING."""
        assert VarKind.from_str("unknown") == VarKind.STRING
        assert VarKind.from_str("") == VarKind.STRING

    def test_from_any_with_varkind(self):
        """Test from_any with VarKind instance."""
        assert VarKind.from_any(VarKind.INTEGER) == VarKind.INTEGER

    def test_from_any_with_string(self):
        """Test from_any with string."""
        assert VarKind.from_any("float") == VarKind.FLOAT

    def test_from_any_defaults_to_string(self):
        """Test from_any with invalid type defaults to STRING."""
        assert VarKind.from_any(123) == VarKind.STRING
        assert VarKind.from_any(None) == VarKind.STRING

    def test_str_representation(self):
        """Test string representation."""
        assert str(VarKind.INTEGER) == "Integer"
        assert str(VarKind.BOOLEAN) == "Boolean"

    def test_repr_representation(self):
        """Test repr representation."""
        assert repr(VarKind.INTEGER) == "VarKind.INTEGER"
        assert repr(VarKind.FLOAT) == "VarKind.FLOAT"

    def test_equality_with_string(self):
        """Test equality comparison with strings."""
        assert VarKind.INTEGER == "integer"
        assert VarKind.INTEGER == "INTEGER"
        assert VarKind.INTEGER == "Integer"

    def test_inequality_with_string(self):
        """Test inequality comparison with strings."""
        assert VarKind.INTEGER != "float"
        assert VarKind.BOOLEAN != "string"

    def test_all_enum_values(self):
        """Test all enum values are defined."""
        assert VarKind.INTEGER.value == "Integer"
        assert VarKind.FLOAT.value == "Float"
        assert VarKind.STRING.value == "String"
        assert VarKind.BOOLEAN.value == "Boolean"
        assert VarKind.LIST.value == "List"
        assert VarKind.DICT.value == "Dict"

    def test_missing_method_case_insensitive(self):
        """Test _missing_ method for case-insensitive lookup."""
        # Using VarKind() constructor triggers _missing_
        assert VarKind("integer") == VarKind.INTEGER
        assert VarKind("FLOAT") == VarKind.FLOAT
        assert VarKind("Boolean") == VarKind.BOOLEAN

    def test_missing_method_defaults_to_string(self):
        """Test _missing_ method defaults to STRING for unknown values."""
        assert VarKind("unknown") == VarKind.STRING
        assert VarKind("random") == VarKind.STRING
