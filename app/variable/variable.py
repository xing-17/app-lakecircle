from __future__ import annotations

import json
from abc import ABC
from typing import Any

from .varkind import VarKind


class Variable(ABC):
    """
    Abstract base class for variable-like objects.

    Attrs:
        name: Variable name.
        kind: Variable kind (String/Integer/Float/Boolean/List/Dict).
        default: Default value if no value is provided by the subclass.
        description: Human-readable description.
        choice: Optional list of valid values.
        value: Current value (if applicable).

    Methods:
        from_dict(data): Create a Variable instance from a dictionary.
        get_value(): Get the current value (subclasses implement).
        describe(): Produce a compact description dict.
        to_dict(): Serialize all fields into a dict.

    Example:
    ```python
        class MyVar(Variable):
            def get_value(self):
                return self.default

        v = MyVar(name="MY_VAR", kind="Integer", default=1)
        assert v.get_value() == 1
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Variable:
        """
        Desc:
            - Create a Variable instance from a dictionary.
        Args:
            - data[dict[str, Any]], Dictionary containing variable fields.
        Returns:
            - Variable, New Variable instance.
        """
        return cls(
            name=data.get("name"),
            kind=data.get("kind"),
            default=data.get("default"),
            description=data.get("description"),
            choice=data.get("choice"),
            value=data.get("value"),
        )

    def __init__(
        self,
        name: str,
        kind: str | VarKind | None = None,
        default: Any = None,
        description: str | None = None,
        choice: list[Any] | None = None,
        value: Any = None,
    ) -> None:
        self.name = self._resolve_name(name)
        self.kind = self._resolve_kind(kind)
        self.default = default
        self.description = description
        self.choice = self._resolve_choice(choice)
        self.value = value

    def _resolve_name(
        self,
        name: str,
    ) -> str:
        if not name or not isinstance(name, str):
            msg = f"Invalid variable name: {name!r}."
            raise ValueError(msg)
        return name

    def _resolve_kind(
        self,
        kind: str | VarKind | None,
    ) -> VarKind:
        if kind is None:
            return VarKind.STRING
        if isinstance(kind, VarKind):
            return kind
        if isinstance(kind, str):
            return VarKind.from_str(kind)
        return VarKind.STRING

    def _resolve_choice(
        self,
        choice: list[Any] | None,
    ) -> list[Any] | None:
        return [item for item in choice if item is not None] if choice else None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, kind={self.kind!r})"

    def _parse_string(
        self,
        raw: Any,
    ) -> str:
        return str(raw).strip()

    def _parse_boolean(
        self,
        raw: Any,
    ) -> bool:
        if isinstance(raw, bool):
            return raw
        raw = str(raw).strip().lower()
        if raw in ("0", "false", "no", "n", "off"):
            return False
        if raw in ("1", "true", "yes", "y", "on"):
            return True
        msg = f"Invalid boolean value: {raw!r}."
        raise ValueError(msg)

    def _parse_int(
        self,
        raw: Any,
    ) -> int:
        if isinstance(raw, int):
            return raw
        try:
            return int(raw)
        except (TypeError, ValueError) as e:
            msg = f"Invalid integer value: {raw!r}."
            raise ValueError(msg) from e

    def _parse_float(
        self,
        raw: Any,
    ) -> float:
        if isinstance(raw, float):
            return raw
        try:
            return float(raw)
        except (TypeError, ValueError) as e:
            msg = f"Invalid float value: {raw!r}."
            raise ValueError(msg) from e

    def _parse_list(
        self,
        raw: Any,
    ) -> list[str]:
        if isinstance(raw, list):
            return [str(item) for item in raw]
        raw = str(raw).strip()
        if not raw:
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    def _parse_dict(
        self,
        raw: Any,
    ) -> dict[str, Any]:
        if isinstance(raw, dict):
            return {str(k): v for k, v in raw.items()}
        raw = str(raw).strip()
        try:
            return json.loads(raw)
        except (TypeError, ValueError) as e:
            msg = f"Invalid dict value: {raw!r}."
            raise ValueError(msg) from e

    def _parse_by_kind(
        self,
        raw: Any,
    ) -> Any:
        if self.kind == VarKind.STRING:
            value = self._parse_string(raw)
        elif self.kind == VarKind.INTEGER:
            value = self._parse_int(raw)
        elif self.kind == VarKind.FLOAT:
            value = self._parse_float(raw)
        elif self.kind == VarKind.BOOLEAN:
            value = self._parse_boolean(raw)
        elif self.kind == VarKind.LIST:
            value = self._parse_list(raw)
        elif self.kind == VarKind.DICT:
            value = self._parse_dict(raw)
        else:
            supported = [k.value for k in VarKind]
            msg = f"Unsupported variable kind: {self.kind!r}. Supported kinds: {supported}"
            raise TypeError(msg)
        if self.choice is not None and value not in self.choice:
            msg = f"Value {value!r} not in choice {self.choice!r}."
            raise ValueError(msg)
        return value

    def get_value(
        self,
    ) -> Any:
        """
        Desc:
            - Get the current value (must be implemented by subclasses).
        Returns:
            - Any, The current value.
        """
        raise NotImplementedError()

    def describe(
        self,
    ) -> dict[str, Any]:
        """
        Desc:
            - Produce a compact description dictionary.
        Returns:
            - dict[str, Any], Description containing name, kind, and optional fields.
        """
        result = {
            "name": self.name,
            "kind": str(self.kind),
        }
        if self.default is not None:
            result["default"] = self.default
        if self.description is not None:
            result["description"] = self.description
        if self.choice is not None:
            result["choice"] = self.choice
        if self.value is not None:
            result["value"] = self.value
        return result

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Desc:
            - Serialize all fields into a dictionary.
        Returns:
            - dict[str, Any], Dictionary containing all variable fields.
        """
        return {
            "name": self.name,
            "kind": str(self.kind),
            "default": self.default,
            "description": self.description,
            "choice": self.choice,
            "value": self.value,
        }
