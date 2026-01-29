from __future__ import annotations

from typing import Any

from app.model.lifecycle.common import S3Configuration


class AbortIncompleteMultipartUpload(S3Configuration):
    """
    Description:
    - Defines automatic cleanup for incomplete multipart uploads
    - Removes incomplete uploads after specified days of initiation
    - Helps reduce storage costs from abandoned uploads
    - Maps to AWS S3 AbortIncompleteMultipartUpload action

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - daysafterinitiation: Days after upload start to abort (int or None)

    Example:
    ```python
    from app.model.lifecycle.abortincompletemultipartupload import AbortIncompleteMultipartUpload

    # Abort incomplete uploads after 7 days
    abort = AbortIncompleteMultipartUpload(daysafterinitiation=7)

    # Use in lifecycle rule
    rule = LifecycleRule(
        id="cleanup-uploads",
        status="Enabled",
        abort_incomplete_multipart_upload=abort
    )
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> AbortIncompleteMultipartUpload:
        return cls(
            daysafterinitiation=(data.get("DaysAfterInitiation") or data.get("daysafterinitiation")),
        )

    def __init__(
        self,
        daysafterinitiation: int | str | None = None,
    ) -> None:
        self.daysafterinitiation: int | None = self.resolve_days(daysafterinitiation)

    def describe(self) -> dict[str, Any]:
        result = {}
        if self.daysafterinitiation is not None:
            result["daysafterinitiation"] = self.daysafterinitiation
        return result

    def to_payload(self) -> dict[str, Any]:
        result = {}
        if self.daysafterinitiation is not None:
            result["DaysAfterInitiation"] = self.daysafterinitiation
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "daysafterinitiation": self.daysafterinitiation,
        }
        return result
