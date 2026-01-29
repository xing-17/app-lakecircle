from __future__ import annotations

from typing import Any, Literal, Union

from app.model.lifecycle.abortincompletemultipartupload import AbortIncompleteMultipartUpload
from app.model.lifecycle.common import S3Configuration
from app.model.lifecycle.expiration import Expiration
from app.model.lifecycle.filter import Filter
from app.model.lifecycle.noncurrentversionexpiration import NoncurrentVersionExpiration
from app.model.lifecycle.noncurrentversiontransition import NoncurrentVersionTransition
from app.model.lifecycle.transition import Transition


class LifecycleRule(S3Configuration):
    """
    Description:
    - Represents a single S3 lifecycle rule with all possible actions
    - Supports expiration, transitions, filters, and multipart upload abort
    - Automatically generates fingerprint for deduplication
    - Maps to AWS S3 lifecycle rule structure

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - id: Unique identifier for the rule
    - prefix: Object key prefix filter (deprecated, use filter instead)
    - status: Rule status ("Enabled" or "Disabled")
    - filter: Filter object for rule application criteria
    - expiration: Expiration object defining when to delete objects
    - transitions: List of Transition objects for storage class changes
    - noncurrent_transitions: List of transitions for noncurrent versions
    - noncurrent_expiration: Expiration settings for noncurrent versions
    - abort_incomplete_multipart_upload: Multipart upload cleanup settings
    - fingerprint: SHA256 hash for rule identification

    Example:
    ```python
    from app.model.lifecycle.lifecyclerule import LifecycleRule

    # Simple expiration rule
    rule = LifecycleRule(
        id="delete-old-logs",
        status="Enabled",
        prefix="logs/",
        expiration={"days": 30}
    )

    # Transition rule with filter
    rule2 = LifecycleRule(
        id="archive-to-glacier",
        status="Enabled",
        filter={"prefix": "archive/"},
        transitions=[{"days": 90, "storageclass": "GLACIER"}]
    )
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> LifecycleRule:
        return cls(
            id=data.get("ID") or data.get("id"),
            prefix=data.get("Prefix") or data.get("prefix"),
            status=data.get("Status") or data.get("status"),
            filter=data.get("Filter") or data.get("filter"),
            expiration=(data.get("Expiration") or data.get("expiration")),
            transitions=(data.get("Transitions") or data.get("transitions")),
            noncurrent_transitions=(data.get("NoncurrentVersionTransitions") or data.get("noncurrent_transitions")),
            noncurrent_expiration=(data.get("NoncurrentVersionExpiration") or data.get("noncurrent_expiration")),
            abort_incomplete_multipart_upload=(
                data.get("AbortIncompleteMultipartUpload") or data.get("abort_incomplete_multipart_upload")
            ),
        )

    def __init__(
        self,
        id: str | None = None,
        prefix: str | None = None,
        status: Literal["Enabled", "Disabled"] | None = None,
        filter: Filter | dict | None = None,
        expiration: Expiration | dict | None = None,
        transitions: list[Transition] | list[dict] | None = None,
        noncurrent_transitions: list[NoncurrentVersionTransition] | list[dict] | None = None,
        noncurrent_expiration: NoncurrentVersionExpiration | dict | None = None,
        abort_incomplete_multipart_upload: AbortIncompleteMultipartUpload | dict | None = None,
    ) -> None:
        self.prefix = prefix
        self.filter = self._resolve_filter(filter)
        self.status = status
        self.expiration = self._resolve_expiration(expiration)
        self.transitions = self._resolve_transitions(transitions)
        self.noncurrent_transitions = self._resolve_noncurrent_transitions(noncurrent_transitions)
        self.noncurrent_expiration = self._resolve_noncurrent_expiration(noncurrent_expiration)
        self.abort_incomplete_multipart_upload = self._resolve_abort_incomplete_multipart_upload(
            abort_incomplete_multipart_upload
        )
        self.fingerprint = self.get_fingerprint()
        self.id = id or self.fingerprint

    def _resolve_transitions(
        self,
        transitions: list[Transition] | list[dict] | None,
    ) -> list[Transition]:
        result: list[Transition] = []
        if transitions is None:
            return result
        for item in transitions:
            if isinstance(item, Transition):
                result.append(item)
            elif isinstance(item, dict):
                obj = Transition.from_dict(item)
                result.append(obj)
        return result

    def _resolve_noncurrent_transitions(
        self,
        noncurrent_transitions: list[NoncurrentVersionTransition] | list[dict] | None,
    ) -> list[NoncurrentVersionTransition]:
        result: list[NoncurrentVersionTransition] = []
        if noncurrent_transitions is None:
            return result
        for item in noncurrent_transitions:
            if isinstance(item, NoncurrentVersionTransition):
                result.append(item)
            elif isinstance(item, dict):
                obj = NoncurrentVersionTransition.from_dict(item)
                result.append(obj)
        return result

    def _resolve_expiration(
        self,
        expiration: Expiration | dict | None,
    ) -> Expiration | None:
        if expiration is None:
            return None
        if isinstance(expiration, Expiration):
            return expiration
        elif isinstance(expiration, dict):
            obj = Expiration.from_dict(expiration)
            return obj
        return None

    def _resolve_filter(
        self,
        filter: Filter | dict | None,
    ) -> Filter | None:
        if filter is None:
            return None
        if isinstance(filter, Filter):
            return filter
        elif isinstance(filter, dict):
            obj = Filter.from_dict(filter)
            return obj
        return None

    def _resolve_noncurrent_expiration(
        self,
        noncurrent_expiration: NoncurrentVersionExpiration | dict | None,
    ) -> NoncurrentVersionExpiration | None:
        if noncurrent_expiration is None:
            return None
        if isinstance(noncurrent_expiration, NoncurrentVersionExpiration):
            return noncurrent_expiration
        elif isinstance(noncurrent_expiration, dict):
            obj = NoncurrentVersionExpiration.from_dict(noncurrent_expiration)
            return obj
        return None

    def _resolve_abort_incomplete_multipart_upload(
        self,
        abort_incomplete_multipart_upload: AbortIncompleteMultipartUpload | dict | None,
    ) -> AbortIncompleteMultipartUpload | None:
        if abort_incomplete_multipart_upload is None:
            return None
        if isinstance(abort_incomplete_multipart_upload, AbortIncompleteMultipartUpload):
            return abort_incomplete_multipart_upload
        elif isinstance(abort_incomplete_multipart_upload, dict):
            obj = AbortIncompleteMultipartUpload.from_dict(abort_incomplete_multipart_upload)
            return obj
        return None

    def __str__(self):
        return self.id

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r})"

    def describe(self) -> dict[str, Union[str, int, bool]]:
        result = {}
        # if self.id:
        #     result["id"] = self.id
        if self.prefix:
            result["prefix"] = self.prefix
        if self.filter:
            result["filter"] = self.filter.describe()
        if self.status:
            result["status"] = self.status
        if self.expiration:
            result["expiration"] = self.expiration.describe()
        if self.transitions:
            result["transitions"] = [t.describe() for t in self.transitions]
        if self.noncurrent_transitions:
            result["noncurrent_transitions"] = [nct.describe() for nct in self.noncurrent_transitions]
        if self.noncurrent_expiration:
            result["noncurrent_expiration"] = self.noncurrent_expiration.describe()
        if self.abort_incomplete_multipart_upload:
            result["abort_incomplete_multipart_upload"] = self.abort_incomplete_multipart_upload.describe()
        return result

    def to_payload(self) -> dict[str, Any]:
        result = {}
        if self.id:
            result["ID"] = self.id
        # AWS requires either Prefix or Filter - default to empty Prefix if neither provided
        if self.filter:
            result["Filter"] = self.filter.to_payload()
        if self.prefix:
            result["Prefix"] = self.prefix
        if self.status:
            result["Status"] = self.status
        if self.expiration:
            result["Expiration"] = self.expiration.to_payload()
        if self.transitions:
            result["Transitions"] = [t.to_payload() for t in self.transitions]
        if self.noncurrent_transitions:
            result["NoncurrentVersionTransitions"] = [nct.to_payload() for nct in self.noncurrent_transitions]
        if self.noncurrent_expiration:
            result["NoncurrentVersionExpiration"] = self.noncurrent_expiration.to_payload()
        if self.abort_incomplete_multipart_upload:
            result["AbortIncompleteMultipartUpload"] = self.abort_incomplete_multipart_upload.to_payload()
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {}
        if self.id:
            result["id"] = self.id
        if self.prefix:
            result["prefix"] = self.prefix
        if self.filter:
            result["filter"] = self.filter.to_dict()
        if self.status:
            result["status"] = self.status
        if self.expiration:
            result["expiration"] = self.expiration.to_dict()
        if self.transitions:
            result["transitions"] = [t.to_dict() for t in self.transitions]
        if self.noncurrent_transitions:
            result["noncurrent_transitions"] = [nct.to_dict() for nct in self.noncurrent_transitions]
        if self.noncurrent_expiration:
            result["noncurrent_expiration"] = self.noncurrent_expiration.to_dict()
        if self.abort_incomplete_multipart_upload:
            result["abort_incomplete_multipart_upload"] = self.abort_incomplete_multipart_upload.to_dict()
        return result
