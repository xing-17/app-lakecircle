from __future__ import annotations

from typing import Any

from .variable import Variable
from .varkind import VarKind


class Constant(Variable):
    """
    Constant value with type parsing and validation.

    Attrs:
        name: Constant name.
        kind: Variable kind used for parsing.
        description: Human-readable description.
        value: Parsed constant value.

    Methods:
        get_value(value): Parse and validate the provided value.
        from_dict(data): Build an instance from a dictionary.

    Example:
    ```python
        c = Constant(name="MAX_RETRIES", kind="Integer", value="3")
        assert c.value == 3
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Variable:
        """
        Desc:
            - Build a Constant instance from a dictionary.
        Args:
            - data[dict[str, Any]], Dictionary containing constant fields.
        Returns:
            - Variable, New Constant instance.
        """
        return cls(
            name=data.get("name"),
            kind=data.get("kind"),
            description=data.get("description"),
            value=data.get("value"),
        )

    def __init__(
        self,
        name: str,
        value: Any,
        kind: str | VarKind | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            kind=kind,
            description=description,
        )
        self.value = self.get_value(value)

    def get_value(
        self,
        value: Any,
    ) -> Any:
        """
        Desc:
            - Parse and validate the provided value.
        Args:
            - value[Any], Raw value to parse.
        Returns:
            - Any, Parsed value according to kind.
        """
        if value is None:
            return None
        return self._parse_by_kind(value)
