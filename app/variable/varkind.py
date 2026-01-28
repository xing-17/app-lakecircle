from __future__ import annotations

from enum import Enum
from typing import Any


class VarKind(str, Enum):
    """
    Enumeration of supported variable types.

    Attrs:
        INTEGER: Integer type.
        FLOAT: Float type.
        STRING: String type.
        BOOLEAN: Boolean type.
        LIST: List type.
        DICT: Dict type.

    Methods:
        from_str(string): Parse kind from string (case-insensitive).
        from_any(value): Resolve kind from supported inputs.

    Example:
    ```python
        kind = VarKind.from_str("boolean")
        assert kind == VarKind.BOOLEAN

        kind2 = VarKind.from_any("List")
        assert kind2 == VarKind.LIST
    ```
    """

    INTEGER = "Integer"
    FLOAT = "Float"
    STRING = "String"
    BOOLEAN = "Boolean"
    LIST = "List"
    DICT = "Dict"

    @classmethod
    def _missing_(cls, value) -> VarKind | None:
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return VarKind.STRING

    @classmethod
    def from_str(cls, string: str) -> VarKind:
        """
        Desc:
            - Parse VarKind from string (case-insensitive).
        Args:
            - string[str], String representation of the kind.
        Returns:
            - VarKind, Parsed kind or STRING as default.
        """
        for dkind in VarKind:
            if dkind.value.lower() == string.lower():
                return dkind
        return VarKind.STRING

    @classmethod
    def from_any(cls, value: Any) -> VarKind:
        """
        Desc:
            - Resolve VarKind from any supported input type.
        Args:
            - value[Any], VarKind instance or string.
        Returns:
            - VarKind, Resolved kind.
        """
        if isinstance(value, VarKind):
            return value
        if isinstance(value, str):
            return cls.from_str(value)
        return VarKind.STRING

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return super().__eq__(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
