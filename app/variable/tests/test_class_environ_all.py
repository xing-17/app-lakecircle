from __future__ import annotations

import pytest

from app.variable.environ import Environ
from app.variable.varkind import VarKind


class TestEnviron:
    def test_init_with_all_parameters(self):
        env = Environ("TEST_VAR", "integer", 42)
        assert env.name == "TEST_VAR"
        assert env.kind == VarKind.INTEGER
        assert env.default == 42

    def test_init_with_varkind_instance(self):
        env = Environ("TEST_VAR", VarKind.FLOAT, 3.14)
        assert env.name == "TEST_VAR"
        assert env.kind == VarKind.FLOAT
        assert env.default == 3.14

    def test_init_with_none_kind(self):
        env = Environ("TEST_VAR", None, "default")
        assert env.kind == VarKind.STRING

    def test_init_with_no_default(self):
        env = Environ("TEST_VAR", "string")
        assert env.name == "TEST_VAR"
        assert env.kind == VarKind.STRING
        assert env.default is None

    def test_get_value_with_default(self):
        env = Environ("NONEXISTENT_VAR", "string", "default_value")
        assert env.get_value() == "default_value"

    def test_get_value_returns_none_when_not_set_and_no_default(self):
        env = Environ("NONEXISTENT_VAR", "string")
        assert env.get_value() is None

    def test_get_value_with_env_var_string(self, monkeypatch):
        monkeypatch.setenv("TEST_STRING", "hello world")
        env = Environ("TEST_STRING", "string")
        assert env.get_value() == "hello world"

    def test_get_value_with_env_var_string_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv("TEST_STRING", "  hello  ")
        env = Environ("TEST_STRING", "string")
        assert env.get_value() == "hello"

    def test_get_value_with_env_var_integer(self, monkeypatch):
        monkeypatch.setenv("TEST_INT", "42")
        env = Environ("TEST_INT", "integer", 0)
        assert env.get_value() == 42
        assert isinstance(env.get_value(), int)

    def test_get_value_with_env_var_negative_integer(self, monkeypatch):
        monkeypatch.setenv("TEST_INT", "-100")
        env = Environ("TEST_INT", "integer")
        assert env.get_value() == -100

    def test_get_value_with_env_var_float(self, monkeypatch):
        monkeypatch.setenv("TEST_FLOAT", "3.14")
        env = Environ("TEST_FLOAT", "float", 0.0)
        assert env.get_value() == 3.14
        assert isinstance(env.get_value(), float)

    def test_get_value_with_env_var_boolean_true(self, monkeypatch):
        test_cases = ["true", "TRUE", "1", "yes", "YES", "y", "on", "ON"]
        for value in test_cases:
            monkeypatch.setenv("TEST_BOOL", value)
            env = Environ("TEST_BOOL", "boolean", False)
            assert env.get_value() is True, f"Failed for value: {value}"

    def test_get_value_with_env_var_boolean_false(self, monkeypatch):
        test_cases = ["false", "FALSE", "0", "no", "NO", "n", "off", "OFF"]
        for value in test_cases:
            monkeypatch.setenv("TEST_BOOL", value)
            env = Environ("TEST_BOOL", "boolean", True)
            assert env.get_value() is False, f"Failed for value: {value}"

    def test_get_value_with_env_var_list(self, monkeypatch):
        monkeypatch.setenv("TEST_LIST", "a,b,c")
        env = Environ("TEST_LIST", "list", [])
        assert env.get_value() == ["a", "b", "c"]

    def test_get_value_with_env_var_list_with_spaces(self, monkeypatch):
        monkeypatch.setenv("TEST_LIST", "a, b, c")
        env = Environ("TEST_LIST", "list", [])
        assert env.get_value() == ["a", "b", "c"]

    def test_get_value_with_env_var_empty_list(self, monkeypatch):
        monkeypatch.setenv("TEST_LIST", "")
        env = Environ("TEST_LIST", "list", ["default"])
        assert env.get_value() == []

    def test_get_value_with_env_var_dict(self, monkeypatch):
        monkeypatch.setenv("TEST_DICT", '{"key": "value"}')
        env = Environ("TEST_DICT", "dict", {})
        assert env.get_value() == {"key": "value"}

    def test_get_value_with_env_var_dict_complex(self, monkeypatch):
        monkeypatch.setenv("TEST_DICT", '{"key": "value", "num": "123", "nested": {"inner": "data"}}')
        env = Environ("TEST_DICT", "dict", {})
        result = env.get_value()
        assert result["key"] == "value"
        assert result["num"] == "123"
        assert result["nested"]["inner"] == "data"

    def test_get_value_none_kind_defaults_to_string(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "  some value  ")
        env = Environ("TEST_VAR", None)
        assert env.get_value() == "some value"

    def test_get_value_prefers_env_over_default(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "from_env")
        env = Environ("TEST_VAR", "string", "default_value")
        assert env.get_value() == "from_env"

    def test_get_value_invalid_integer_raises_error(self, monkeypatch):
        monkeypatch.setenv("TEST_INT", "not_a_number")
        with pytest.raises(ValueError, match="Invalid integer value"):
            Environ("TEST_INT", "integer")

    def test_get_value_invalid_float_raises_error(self, monkeypatch):
        monkeypatch.setenv("TEST_FLOAT", "not_a_number")
        with pytest.raises(ValueError, match="Invalid float value"):
            Environ("TEST_FLOAT", "float")

    def test_get_value_invalid_boolean_raises_error(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL", "maybe")
        with pytest.raises(ValueError, match="Invalid boolean value"):
            Environ("TEST_BOOL", "boolean")

    def test_get_value_invalid_dict_raises_error(self, monkeypatch):
        monkeypatch.setenv("TEST_DICT", "not json")
        with pytest.raises(ValueError, match="Invalid dict value"):
            Environ("TEST_DICT", "dict")

    def test_multiple_environ_instances(self, monkeypatch):
        monkeypatch.setenv("VAR1", "value1")
        monkeypatch.setenv("VAR2", "42")
        monkeypatch.setenv("VAR3", "true")
        env1 = Environ("VAR1", "string")
        env2 = Environ("VAR2", "integer")
        env3 = Environ("VAR3", "boolean")
        assert env1.get_value() == "value1"
        assert env2.get_value() == 42
        assert env3.get_value() is True

    def test_environ_inheritance_from_variable(self):
        from app.variable.variable import Variable

        env = Environ("TEST", "string")
        assert isinstance(env, Variable)

    def test_value_attribute_set_on_init(self):
        env = Environ("NONEXISTENT_VAR", "string", "default_value")
        assert hasattr(env, "value")
        assert env.value == "default_value"

    def test_value_attribute_with_env_var(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "42")
        env = Environ("TEST_VAR", "integer", 0)
        assert env.value == 42

    def test_value_attribute_updated_on_get_value(self, monkeypatch):
        monkeypatch.setenv("TEST_VAR", "hello")
        env = Environ("TEST_VAR", "string")
        assert env.value == env.get_value()
        assert env.value == "hello"

    def test_from_dict_creates_environ(self):
        data = {"name": "DB_PORT", "kind": "integer", "default": 5432}
        env = Environ.from_dict(data)
        assert isinstance(env, Environ)
        assert env.name == "DB_PORT"
        assert env.kind == VarKind.INTEGER
        assert env.default == 5432
        assert env.value == 5432

    def test_from_dict_with_env_var(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "localhost")
        data = {"name": "DB_HOST", "kind": "string", "default": "0.0.0.0"}
        env = Environ.from_dict(data)
        assert env.value == "localhost"
        assert env.get_value() == "localhost"

    def test_describe_includes_name_kind_default(self):
        env = Environ("TEST_VAR", "string", "default_value")
        desc = env.describe()

        assert "name" in desc
        assert "kind" in desc
        assert "default" in desc
        assert desc["name"] == "TEST_VAR"
        assert desc["kind"] == "String"
        assert desc["default"] == "default_value"

    def test_describe_includes_value(self, monkeypatch):
        monkeypatch.setenv("MY_VAR", "test_value")
        env = Environ("MY_VAR", "string")
        desc = env.describe()

        assert "value" in desc
        assert desc["value"] == "test_value"

    def test_describe_excludes_value_when_none(self):
        env = Environ("NONEXISTENT", "string")
        desc = env.describe()
        assert "value" not in desc or desc.get("value") is None

    def test_to_dict_includes_all_metadata(self):
        env = Environ("PORT", "integer", 8080)
        data = env.to_dict()
        assert "name" in data
        assert "kind" in data
        assert "default" in data
        assert "value" in data
        assert data["name"] == "PORT"
        assert data["kind"] == "Integer"
        assert data["default"] == 8080
        assert data["value"] == 8080

    def test_to_dict_with_env_var_override(self, monkeypatch):
        monkeypatch.setenv("OVERRIDDEN", "env_value")
        env = Environ("OVERRIDDEN", "string", "default_value")
        data = env.to_dict()
        assert data["default"] == "default_value"
        assert data["value"] == "env_value"

    def test_to_dict_with_none_value(self):
        env = Environ("NULLABLE", "string")
        data = env.to_dict()
        assert "value" in data
        assert data["value"] is None
