from __future__ import annotations

from typing import Any, Literal

from app.model.lifecycle.common import S3Configuration
from app.model.lifecycle.lifecyclerule import LifecycleRule


class LifecycleConfiguration(S3Configuration):
    """
    Description:
    - Top-level container for S3 bucket lifecycle rules
    - Manages collection of LifecycleRule objects indexed by fingerprint
    - Supports rule addition, deletion, and difference calculation
    - Maps to AWS S3 GetBucketLifecycleConfiguration API response

    Methods:
    - from_dict(data): Create from AWS API response or dict
    - add_rule(rule, strict): Add a lifecycle rule (skip duplicates if not strict)
    - delete_rule(rule, strict): Remove a lifecycle rule by fingerprint or object
    - difference(other): Calculate added/removed rules compared to another config
    - describe(): Return human-readable dict representation
    - to_payload(): Convert to AWS API request format
    - to_dict(): Serialize to dict format

    Attrs:
    - bucket: S3 bucket name (optional)
    - checksumalgorithm: Checksum algorithm (optional)
    - rules: Dict mapping rule fingerprints to LifecycleRule objects
    - expectedbucketowner: Expected bucket owner account (optional)
    - transitiondefaultminimumobjectsize: Minimum object size for transitions (optional)

    Example:
    ```python
    from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
    from app.model.lifecycle.lifecyclerule import LifecycleRule

    config = LifecycleConfiguration(
        bucket="my-bucket",
        rules=[
            LifecycleRule(id="archive", status="Enabled", expiration={"days": 90}),
            LifecycleRule(id="glacier", status="Enabled", transitions=[...])
        ]
    )

    payload = config.to_payload()
    # Use payload with boto3 put_bucket_lifecycle_configuration()
    ```
    """

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> LifecycleConfiguration:
        # Try to get Rules from nested LifecycleConfiguration first, then top level
        rules = (
            data.get("LifecycleConfiguration", {}).get("Rules")
            or data.get("lifecycleconfiguration", {}).get("rules")
            or data.get("Rules")
            or data.get("rules")
        )
        return cls(
            bucket=data.get("Bucket") or data.get("bucket"),
            checksumalgorithm=data.get("ChecksumAlgorithm") or data.get("checksumalgorithm"),
            rules=rules,
            expectedbucketowner=data.get("ExpectedBucketOwner") or data.get("expectedbucketowner"),
            transitiondefaultminimumobjectsize=data.get("TransitionDefaultMinimumObjectSize")
            or data.get("transitiondefaultminimumobjectsize"),
        )

    def __init__(
        self,
        bucket: str | None = None,
        checksumalgorithm: Literal["CRC32", "CRC32C", "SHA1", "SHA256"] | None = None,
        rules: list[LifecycleRule] | list[dict] | None = None,
        expectedbucketowner: str | None = None,
        transitiondefaultminimumobjectsize: Literal["varies_by_storage_class", "all_storage_classes_128K"]
        | None = None,
    ) -> None:
        self.bucket = bucket
        self.checksumalgorithm = checksumalgorithm
        self.rules: dict[str, LifecycleRule] = self._resolve_rules(rules)
        self.expectedbucketowner = expectedbucketowner
        self.transitiondefaultminimumobjectsize = transitiondefaultminimumobjectsize

    def _resolve_rules(
        self,
        rules: list[LifecycleRule] | list[dict] | None,
    ) -> dict[str, LifecycleRule]:
        result: dict[str, LifecycleRule] = {}
        if rules is None:
            return result
        for item in rules:
            if isinstance(item, LifecycleRule):
                result[item.fingerprint] = item
            elif isinstance(item, dict):
                item = LifecycleRule.from_dict(item)
                result[item.fingerprint] = item
        return result

    def difference(
        self,
        other: LifecycleConfiguration | dict[str, Any],
    ) -> dict[str, list[LifecycleRule]]:
        if isinstance(other, dict):
            other = LifecycleConfiguration.from_dict(other)
        added: list[LifecycleRule] = []
        removed: list[LifecycleRule] = []
        for fingerprint, rule in self.rules.items():
            if fingerprint not in other.rules:
                added.append(rule)
        for fingerprint, rule in other.rules.items():
            if fingerprint not in self.rules:
                removed.append(rule)
        return {"added": added, "removed": removed}

    def remove_rule(
        self,
        rule: LifecycleRule | str,
        strict: bool = False,
    ) -> None:
        if isinstance(rule, LifecycleRule):
            fingerprint = rule.fingerprint
        if isinstance(rule, str):
            fingerprint = rule
        try:
            del self.rules[fingerprint]
        except KeyError as e:
            if strict:
                raise e

    def add_rule(
        self,
        rule: LifecycleRule | dict,
        strict: bool = False,
    ) -> None:
        if isinstance(rule, LifecycleRule):
            fingerprint = rule.fingerprint
            rule = rule
        if isinstance(rule, dict):
            rule = LifecycleRule.from_dict(rule)
            fingerprint = rule.fingerprint
        if fingerprint in self.rules:
            if strict:
                raise ValueError(f"Rule with fingerprint {fingerprint} already exists.")
            else:
                return
        if rule is None:
            raise ValueError(f"Rule with fingerprint {fingerprint} not found.")
        self.rules[fingerprint] = rule

    def describe(self) -> dict[str, Any]:
        result = {}
        if self.bucket is not None:
            result["bucket"] = self.bucket
        if self.checksumalgorithm is not None:
            result["checksumalgorithm"] = self.checksumalgorithm
        if self.rules:
            result["lifecycleconfiguration"] = {"rules": [rule.describe() for rule in self.rules.values()]}
        if self.expectedbucketowner is not None:
            result["expectedbucketowner"] = self.expectedbucketowner
        if self.transitiondefaultminimumobjectsize is not None:
            result["transitiondefaultminimumobjectsize"] = self.transitiondefaultminimumobjectsize
        return result

    def to_payload(self) -> dict[str, Any]:
        result = {}
        if self.bucket is not None:
            result["Bucket"] = self.bucket
        if self.checksumalgorithm is not None:
            result["ChecksumAlgorithm"] = self.checksumalgorithm
        if self.rules:
            result["LifecycleConfiguration"] = {"Rules": [rule.to_payload() for rule in self.rules.values()]}
        if self.expectedbucketowner is not None:
            result["ExpectedBucketOwner"] = self.expectedbucketowner
        if self.transitiondefaultminimumobjectsize is not None:
            result["TransitionDefaultMinimumObjectSize"] = self.transitiondefaultminimumobjectsize
        return result

    def to_dict(self) -> dict[str, Any]:
        result = {
            "bucket": self.bucket,
            "checksumalgorithm": self.checksumalgorithm,
            "lifecycleconfiguration": {
                "rules": [rule.to_dict() for rule in self.rules.values()],
            },
            "expectedbucketowner": self.expectedbucketowner,
            "transitiondefaultminimumobjectsize": self.transitiondefaultminimumobjectsize,
        }
        return result
