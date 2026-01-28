from __future__ import annotations

from typing import Any

from app.base import Component
from app.variable.constant import Constant
from app.variable.environ import Environ
from app.variable.variable import Variable
from app.variable.varkind import VarKind


class Setting(Component):
    """
    Configuration container for environment variables and constants.

    Attributes:
        parent: Optional parent component for logging inheritance.
        logformat: Custom log format for this setting instance.
        variables: Dictionary mapping variable names to Environ instances.
        constants: Dictionary mapping constant names to Constant instances.
        context: Resolved configuration dictionary with all values.

    Methods:
        add_variable(name, kind, default): Add environment variable definition.
        add_constant(name, value, kind): Add constant definition.
        get(name, default): Retrieve value by name.
        get_context(): Get complete configuration dictionary.
        list_variables(): List all Environ instances.
        list_constants(): List all Constant instances.
        list_all(): List all configuration items.
        build(): Build resolved configuration context.
        describe(): Get structured description of all settings.
        to_dict(): Serialize to dictionary format.
        from_dict(data): Create Setting from dictionary (class method).
        __contains__(name): Check if name exists in configuration.
        __getitem__(name): Access configuration value by name.
        __len__(): Get total count of variables and constants.

    Example:
    ```python
        setting = Setting(
            variables=[{"name": "APP_LEVEL", "kind": "string", "default": "INFO"}],
            constants=[{"name": "APP_NAME", "kind": "string", "value": "finbatch"}],
        )
        level = setting.get("APP_LEVEL")
        name = setting["APP_NAME"]
        all_config = setting.context
    ```
    """

    def __init__(
        self,
        parent: Component | None = None,
        logformat: Any = None,
        variables: list[Environ | dict[str, Any]] | None = None,
        constants: list[Constant | dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            parent=parent,
            logformat=logformat,
        )
        self.variables = self._resolve_variables(variables)
        self.constants = self._resolve_constants(constants)
        self.context = self.build()

    def _resolve_variables(
        self,
        variables: list[Environ | dict[str, Any]] | None = None,
    ) -> dict[str, Environ]:
        if variables is None:
            return {}
        result: dict[str, Environ] = {}
        for var in variables:
            if isinstance(var, Environ):
                result[var.name] = var
            elif isinstance(var, dict):
                env = Environ.from_dict(var)
                result[env.name] = env
            else:
                msg = f"Invalid variable type: {type(var)!r}."
                raise TypeError(msg)
        return result

    def _resolve_constants(
        self,
        constants: list[Constant | dict[str, Any]] | None = None,
    ) -> dict[str, Constant]:
        if constants is None:
            return {}
        result: dict[str, Constant] = {}
        for const in constants:
            if isinstance(const, Constant):
                result[const.name] = const
            elif isinstance(const, dict):
                constant = Constant.from_dict(const)
                result[constant.name] = constant
            else:
                msg = f"Invalid constant type: {type(const)!r}."
                raise TypeError(msg)
        return result

    def build(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for variable in self.variables.values():
            result[variable.name] = variable.value
        for constant in self.constants.values():
            result[constant.name] = constant.value
        return result

    def get(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        if name in self.variables:
            return self.variables[name].value
        if name in self.constants:
            return self.constants[name].value
        return default

    def get_context(self) -> dict[str, Any]:
        return self.context

    def list_variables(
        self,
    ) -> list[Environ]:
        return list(self.variables.values())

    def list_constants(
        self,
    ) -> list[Constant]:
        return list(self.constants.values())

    def list_all(
        self,
    ) -> list[Variable]:
        result: list[Variable] = []
        result.extend(self.list_variables())
        result.extend(self.list_constants())
        return result

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return name in self.variables or name in self.constants

    def __len__(
        self,
    ) -> int:
        return len(self.variables) + len(self.constants)

    def describe(
        self,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "variables": [],
            "constants": [],
        }
        for variable in self.variables.values():
            result["variables"].append(variable.describe())
        for constant in self.constants.values():
            result["constants"].append(constant.describe())
        return result

    def add_variable(
        self,
        name: str,
        kind: str | VarKind | None = None,
        default: Any = None,
    ) -> None:
        environ = Environ(name=name, kind=kind, default=default)
        self.variables[name] = environ
        self.context = self.build()

    def add_constant(
        self,
        name: str,
        value: Any,
        kind: str | VarKind | None = None,
    ) -> None:
        constant = Constant(name=name, value=value, kind=kind)
        self.constants[name] = constant
        self.context = self.build()

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Setting:
        return cls(
            variables=data.get("variables"),
            constants=data.get("constants"),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "variables": [],
            "constants": [],
        }
        for variable in self.variables.values():
            result["variables"].append(variable.to_dict())
        for constant in self.constants.values():
            result["constants"].append(constant.to_dict())
        return result

    def __getitem__(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name].value
        if name in self.constants:
            return self.constants[name].value
        msg = f"Name not found: {name!r}"
        raise KeyError(msg)
