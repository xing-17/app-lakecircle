from __future__ import annotations

from typing import Any

from app.model.lifecycle.common import S3Configuration
from app.model.lifecycle.storageclass import StorageClass


class NoncurrentVersionTransition(S3Configuration):
    """
    Description:
    - Defines storage class transitions for noncurrent object versions
    - Moves noncurrent versions to cheaper storage classes over time
    - Optionally keeps a minimum number of newer noncurrent versions
    - Maps to AWS S3 NoncurrentVersionTransition action

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - noncurrentdays: Days after becoming noncurrent to transition (int or None)
    - storageclass: Target StorageClass enum value
    - newernoncurrentversions: Number of newer noncurrent versions to retain (int or None)

    Example:
    ```python
    from app.model.lifecycle.noncurrentversiontransition import NoncurrentVersionTransition

    # Transition noncurrent versions to Glacier after 30 days
    trans1 = NoncurrentVersionTransition(
        noncurrentdays=30,
        storageclass="GLACIER"
    )

    # Keep 2 newer versions, transition older to Deep Archive after 90 days
    trans2 = NoncurrentVersionTransition(
        noncurrentdays=90,
        storageclass="DEEP_ARCHIVE",
        newernoncurrentversions=2
    )
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> NoncurrentVersionTransition:
        return cls(
            noncurrentdays=data.get("NoncurrentDays") or data.get("noncurrentdays"),
            newernoncurrentversions=data.get("NewerNoncurrentVersions") or data.get("newernoncurrentversions"),
            storageclass=data.get("StorageClass") or data.get("storageclass"),
        )

    def __init__(
        self,
        noncurrentdays: int | str | None = None,
        newernoncurrentversions: int | str | None = None,
        storageclass: StorageClass | str | None = None,
    ) -> None:
        self.noncurrentdays: int | None = self.resolve_days(noncurrentdays)
        self.newernoncurrentversions: int | None = self.resolve_days(newernoncurrentversions)
        self.storageclass: StorageClass | None = self.resolve_storageclass(storageclass)

    def describe(self) -> dict[str, Any]:
        result = {}
        if self.noncurrentdays is not None:
            result["noncurrentdays"] = self.noncurrentdays
        if self.newernoncurrentversions is not None:
            result["newernoncurrentversions"] = self.newernoncurrentversions
        if self.storageclass:
            result["storageclass"] = self.storageclass.value
        return result

    def to_payload(self) -> dict[str, Any]:
        result = {}
        if self.noncurrentdays is not None:
            result["NoncurrentDays"] = self.noncurrentdays
        if self.newernoncurrentversions is not None:
            result["NewerNoncurrentVersions"] = self.newernoncurrentversions
        if self.storageclass:
            result["StorageClass"] = self.storageclass.value
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "noncurrentdays": self.noncurrentdays,
            "newernoncurrentversions": self.newernoncurrentversions,
            "storageclass": self.storageclass.value if self.storageclass else None,
        }
        return result
