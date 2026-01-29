from __future__ import annotations

from typing import Any

from app.model.lifecycle.common import S3Configuration


class NoncurrentVersionExpiration(S3Configuration):
    """
    Description:
    - Defines expiration for noncurrent object versions in versioned buckets
    - Supports permanent deletion after specified days of noncurrency
    - Optionally keeps a minimum number of newer noncurrent versions
    - Maps to AWS S3 NoncurrentVersionExpiration action

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - noncurrentdays: Days after version becomes noncurrent to delete (int or None)
    - newernoncurrentversions: Number of newer noncurrent versions to retain (int or None)

    Example:
    ```python
    from app.model.lifecycle.noncurrentversionexpiration import NoncurrentVersionExpiration

    # Delete noncurrent versions after 90 days
    exp1 = NoncurrentVersionExpiration(noncurrentdays=90)

    # Keep 3 newer noncurrent versions, delete older after 30 days
    exp2 = NoncurrentVersionExpiration(
        noncurrentdays=30,
        newernoncurrentversions=3
    )
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> NoncurrentVersionExpiration:
        return cls(
            noncurrentdays=data.get("NoncurrentDays") or data.get("noncurrentdays"),
            newernoncurrentversions=data.get("NewerNoncurrentVersions") or data.get("newernoncurrentversions"),
        )

    def __init__(
        self,
        noncurrentdays: int | str | None = None,
        newernoncurrentversions: int | str | None = None,
    ) -> None:
        self.noncurrentdays: int | None = self.resolve_days(noncurrentdays)
        self.newernoncurrentversions: int | None = self.resolve_days(newernoncurrentversions)

    def describe(self) -> dict[str, Any]:
        result = {}
        if self.noncurrentdays is not None:
            result["noncurrentdays"] = self.noncurrentdays
        if self.newernoncurrentversions is not None:
            result["newernoncurrentversions"] = self.newernoncurrentversions
        return result

    def to_payload(self) -> dict[str, Any]:
        result = {}
        if self.noncurrentdays is not None:
            result["NoncurrentDays"] = self.noncurrentdays
        if self.newernoncurrentversions is not None:
            result["NewerNoncurrentVersions"] = self.newernoncurrentversions
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "noncurrentdays": self.noncurrentdays,
            "newernoncurrentversions": self.newernoncurrentversions,
        }
        return result
