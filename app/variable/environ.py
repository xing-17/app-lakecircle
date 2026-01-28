from __future__ import annotations

import os
from typing import Any

from .variable import Variable
from .varkind import VarKind


class Environ(Variable):
    """
    Environment variable with default fallback.

    Attrs:
        name: Environment variable name.
        kind: Variable kind used for parsing.
        default: Fallback value when the environment variable is not set.
        description: Human-readable description.
        choice: Optional list of valid values.
        value: Parsed value read from environment (or default).

    Methods:
        get_value(): Read and parse environment value.
        from_dict(data): Build an instance from a dictionary.

    Example:
    ```python
        # Suppose os.environ["MY_FLAG"] = "true"
        v = Environ(name="MY_FLAG", kind="Boolean", default=False)
        assert v.value is True
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Variable:
        """
        Desc:
            - Build an Environ instance from a dictionary.
        Args:
            - data[dict[str, Any]], Dictionary containing environ fields.
        Returns:
            - Variable, New Environ instance.
        """
        return cls(
            name=data.get("name"),
            kind=data.get("kind"),
            default=data.get("default"),
            description=data.get("description"),
            choice=data.get("choice"),
        )

    def __init__(
        self,
        name: str,
        kind: str | VarKind | None = None,
        default: Any = None,
        description: str | None = None,
        choice: list[Any] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            kind=kind,
            default=default,
            description=description,
            choice=choice,
        )
        self.value = self.get_value()

    def get_value(
        self,
    ) -> Any:
        """
        Desc:
            - Read and parse environment value.
        Returns:
            - Any, Parsed value from environment or default.
        """
        raw = os.environ.get(self.name)
        if raw is None:
            return self.default
        return self._parse_by_kind(raw)
