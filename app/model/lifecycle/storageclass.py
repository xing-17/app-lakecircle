from __future__ import annotations

from enum import Enum
from typing import Any, Literal

StorageClassLiteral = Literal[
    "STANDARD",
    "GLACIER",
    "STANDARD_IA",
    "ONEZONE_IA",
    "INTELLIGENT_TIERING",
    "DEEP_ARCHIVE",
    "GLACIER_IR",
]


class StorageClass(str, Enum):
    """
    Enumeration of supported storage types.

    Attrs:
        # ------ non-transitable storage classes ----- #
        STANDARD: Standard storage class.
        # ------ transitable storage classes ----- #
        GLACIER: Glacier storage class.
        STANDARD_IA: Standard-Infrequent Access storage class.
        ONEZONE_IA: One Zone-Infrequent Access storage class.
        INTELLIGENT_TIERING: Intelligent Tiering storage class.
        DEEP_ARCHIVE: Deep Archive storage class.
        GLACIER_IR: Glacier Instant Retrieval storage class.

    Methods:
        from_str(string): Parse kind from string (case-insensitive).
        from_any(value): Resolve kind from supported inputs.

    Example:
    ```python
        kind = StorageClass.from_str("STANDARD")
        assert kind == StorageClass.STANDARD

        kind2 = StorageClass.from_any("GLACIER")
        assert kind2 == StorageClass.GLACIER
    ```
    """

    STANDARD = "STANDARD"

    GLACIER = "GLACIER"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    GLACIER_IR = "GLACIER_IR"

    @classmethod
    def from_str(cls, string: str) -> StorageClass:
        for kind in StorageClass:
            if kind.value.lower() == string.lower():
                return kind
        return StorageClass.STANDARD

    @classmethod
    def from_any(cls, value: Any) -> StorageClass:
        if isinstance(value, StorageClass):
            return value
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return StorageClass.STANDARD

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

    def __hash__(self) -> int:
        return super().__hash__()

    def is_transitable(self) -> bool:
        transitable_classes = [
            StorageClass.GLACIER,
            StorageClass.STANDARD_IA,
            StorageClass.ONEZONE_IA,
            StorageClass.INTELLIGENT_TIERING,
            StorageClass.DEEP_ARCHIVE,
            StorageClass.GLACIER_IR,
        ]
        return self in transitable_classes

    def is_non_transitable(self) -> bool:
        return self == StorageClass.STANDARD
