from __future__ import annotations

from typing import Any, Union

from app.model.lifecycle.common import S3Configuration


class Filter(S3Configuration):
    """
    Description:
    - Defines filtering criteria for lifecycle rule application
    - Supports prefix matching, object size limits, and tag-based filtering
    - Allows AND combinations of multiple filter conditions
    - Maps to AWS S3 LifecycleRuleFilter structure

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - prefix: Object key prefix to match (str or None)
    - tag_key: Tag key for filtering (str or None)
    - tag_value: Tag value for filtering (str or None)
    - object_size_greater_than: Minimum object size in bytes (int or None)
    - object_size_less_than: Maximum object size in bytes (int or None)

    Example:
    ```python
    from app.model.lifecycle.filter import Filter

    # Simple prefix filter
    filter1 = Filter(prefix="logs/")

    # Size-based filter
    filter2 = Filter(object_size_greater_than=1024)  # Objects > 1KB

    # Tag filter
    filter3 = Filter(tag_key="archive", tag_value="true")

    # Prefix and size filter
    filter4 = Filter(
        prefix="archive/",
        object_size_greater_than=1048576  # > 1MB
    )
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Filter:
        prefix = data.get("Prefix") or data.get("prefix")
        tag_key = data.get("Tag", {}).get("Key") or data.get("tag", {}).get("key")
        tag_value = data.get("Tag", {}).get("Value") or data.get("tag", {}).get("value")
        object_size_less_than = data.get("ObjectSizeLessThan") or data.get("object_size_less_than")
        object_size_greater_than = data.get("ObjectSizeGreaterThan") or data.get("object_size_greater_than")
        return cls(
            prefix=prefix,
            tag_key=tag_key,
            tag_value=tag_value,
            object_size_greater_than=object_size_greater_than,
            object_size_less_than=object_size_less_than,
        )

    def __init__(
        self,
        prefix: str | None = None,
        tag_key: str | None = None,
        tag_value: str | None = None,
        object_size_greater_than: int | None = None,
        object_size_less_than: int | None = None,
    ) -> None:
        self.prefix = prefix
        self.tag_key = tag_key
        self.tag_value = tag_value
        self.object_size_greater_than = object_size_greater_than
        self.object_size_less_than = object_size_less_than

    def describe(self) -> dict[str, Union[str, int, bool]]:
        result = {}
        if self.prefix:
            result["prefix"] = self.prefix
        if self.tag_key and self.tag_value:
            result["tag"] = {"key": self.tag_key, "value": self.tag_value}
        if self.object_size_greater_than is not None:
            result["object_size_greater_than"] = self.object_size_greater_than
        if self.object_size_less_than is not None:
            result["object_size_less_than"] = self.object_size_less_than
        return result

    def to_payload(self):
        result = {}
        if self.prefix:
            result["Prefix"] = self.prefix
        if self.tag_key and self.tag_value:
            result["Tag"] = {"Key": self.tag_key, "Value": self.tag_value}
        if self.object_size_greater_than is not None:
            result["ObjectSizeGreaterThan"] = self.object_size_greater_than
        if self.object_size_less_than is not None:
            result["ObjectSizeLessThan"] = self.object_size_less_than
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "prefix": self.prefix,
            "tag": {"key": self.tag_key, "value": self.tag_value},
            "object_size_greater_than": self.object_size_greater_than,
            "object_size_less_than": self.object_size_less_than,
        }
        return result
