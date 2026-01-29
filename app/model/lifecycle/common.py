from __future__ import annotations

import hashlib
import json
from abc import ABC
from datetime import date, datetime

from app.model.lifecycle.storageclass import StorageClass


class S3Configuration(ABC):
    """
    Description:
    - Abstract base class for AWS S3 lifecycle configuration components
    - Provides common utility methods for resolving dates, days, and storage classes
    - Defines interface for describe(), to_payload(), and to_dict() methods

    Methods:
    - resolve_days(value): Convert value to integer days
    - resolve_date(value): Convert value to date object
    - resolve_storageclass(value): Convert value to StorageClass enum
    - describe(): Return human-readable dict representation
    - get_fingerprint(): Generate SHA256 hash of configuration
    - to_payload(): Convert to AWS API payload format
    - to_dict(): Convert to serializable dict format

    Attrs:
    - None (abstract base class)

    Example:
    ```python
    class MyConfig(S3Configuration):
        def __init__(self, days: int | None = None):
            self.days = self.resolve_days(days)

        def to_payload(self) -> dict:
            return {"Days": self.days}
    ```
    """

    def resolve_days(
        self,
        value: int | None,
    ) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        else:
            msg = f"Invalid days value: {value!r}."
            raise ValueError(msg)

    def resolve_date(
        self,
        value: date | str | None,
    ) -> date | None:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            resolved = datetime.strptime(value, "%Y-%m-%d").date()  # YYYY-MM-DD
            return resolved
        else:
            msg = f"Invalid date value: {value!r}."
            raise ValueError(msg)

    def resolve_storageclass(
        self,
        storageclass: StorageClass | str | None,
    ) -> StorageClass | None:
        if storageclass is None:
            return None
        return StorageClass.from_any(storageclass)

    def describe(self) -> dict[str, str]:
        result = {}
        return result

    def get_fingerprint(self) -> str:
        dna: dict[str, str] = self.describe()
        dnaserial = json.dumps(dna, sort_keys=True, ensure_ascii=False)
        fingerprint = hashlib.sha256(dnaserial.encode()).hexdigest()
        return fingerprint

    def to_payload(self) -> dict[str, str]:
        raise NotImplementedError()

    def to_dict(self) -> dict[str, str]:
        result = {}
        return result
