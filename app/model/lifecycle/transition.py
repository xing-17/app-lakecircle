from __future__ import annotations

from datetime import date
from typing import Any, Union

from app.model.lifecycle.common import S3Configuration
from app.model.lifecycle.storageclass import StorageClass


class Transition(S3Configuration):
    """
    Description:
    - Defines when and how to transition S3 objects to different storage classes
    - Supports transitions by date or days after object creation
    - Maps to AWS S3 Transition action in lifecycle rules

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - date: Specific date when transition occurs (date object or None)
    - days: Number of days after creation when transition occurs (int or None)
    - storageclass: Target StorageClass enum value

    Example:
    ```python
    from app.model.lifecycle.transition import Transition
    from app.model.lifecycle.storageclass import StorageClass

    # Transition to Glacier after 90 days
    trans1 = Transition(days=90, storageclass="GLACIER")

    # Transition to IA on specific date
    trans2 = Transition(date="2026-06-01", storageclass=StorageClass.STANDARD_IA)
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Transition:
        return cls(
            date=data.get("Date") or data.get("date"),
            days=data.get("Days") or data.get("days"),
            storageclass=data.get("StorageClass") or data.get("storageclass"),
        )

    def __init__(
        self,
        date: date | str | None = None,
        days: int | str | None = None,
        storageclass: StorageClass | str | None = None,
    ) -> None:
        self.date: date | None = self.resolve_date(date)
        self.days: int | None = self.resolve_days(days)
        self.storageclass: StorageClass | None = self.resolve_storageclass(storageclass)

    def describe(self) -> dict[str, Union[str, int]]:
        result = {}
        if self.date:
            result["date"] = self.date.strftime("%Y-%m-%d")
        if self.days is not None:
            result["days"] = self.days
        if self.storageclass:
            result["storageclass"] = self.storageclass.value
        return result

    def to_payload(self) -> dict[str, Union[date, str, int]]:
        result = {}
        if self.date:
            result["Date"] = self.date
        if self.days is not None:
            result["Days"] = self.days
        if self.storageclass:
            result["StorageClass"] = self.storageclass.value
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "days": self.days,
            "storageclass": self.storageclass.value if self.storageclass else None,
        }
        return result
