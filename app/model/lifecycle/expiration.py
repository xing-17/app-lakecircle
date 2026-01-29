from __future__ import annotations

from datetime import date
from typing import Any, Union

from app.model.lifecycle.common import S3Configuration


class Expiration(S3Configuration):
    """
    Description:
    - Defines when S3 objects should be permanently deleted
    - Supports expiration by date, days after creation, or delete markers
    - Maps to AWS S3 Expiration action in lifecycle rules

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - date: Specific date when objects expire (date object or None)
    - days: Number of days after creation when objects expire (int or None)
    - expired_object_delete_marker: Remove delete markers (bool or None)

    Example:
    ```python
    from app.model.lifecycle.expiration import Expiration
    from datetime import date

    # Expire after 30 days
    exp1 = Expiration(days=30)

    # Expire on specific date
    exp2 = Expiration(date="2026-12-31")

    # Remove expired delete markers
    exp3 = Expiration(expired_object_delete_marker=True)
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Expiration:
        return cls(
            date=data.get("Date") or data.get("date"),
            days=data.get("Days") or data.get("days"),
            expired_object_delete_marker=(
                data.get("ExpiredObjectDeleteMarker") or data.get("expiredobjectdeletemarker")
            ),
        )

    def __init__(
        self,
        date: date | str | None = None,
        days: int | None = None,
        expired_object_delete_marker: bool | None = None,
    ) -> None:
        self.date = self.resolve_date(date)
        self.days = self.resolve_days(days)
        self.expired_object_delete_marker = expired_object_delete_marker

    def describe(self) -> dict[str, Union[str, int, bool]]:
        result = {}
        if self.date:
            result["date"] = self.date.strftime("%Y-%m-%d")
        if self.days is not None:
            result["days"] = self.days
        if self.expired_object_delete_marker is not None:
            result["expired_object_delete_marker"] = self.expired_object_delete_marker
        return result

    def to_payload(self):
        result = {}
        if self.date:
            result["Date"] = self.date
        if self.days is not None:
            result["Days"] = self.days
        if self.expired_object_delete_marker is not None:
            result["ExpiredObjectDeleteMarker"] = self.expired_object_delete_marker
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "days": self.days,
            "expired_object_delete_marker": self.expired_object_delete_marker,
        }
        return result
