from __future__ import annotations

import tomllib
from typing import Any
from urllib.parse import urlparse

from app.model.definition.bucket import BucketDefinition
from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.resource.common import S3Component


class AccountDefinition(S3Component):
    """
    Description:
    - Manages S3 bucket lifecycle definitions loaded from TOML files
    - Reads configuration files from an S3 URI prefix
    - Aggregates and merges lifecycle rules across multiple TOML files
    - Supports defining multiple buckets with their lifecycle policies

    Methods:
    - require(data, key, strict): Validate presence of required keys
    - load(): Parse all TOML files from S3 and build bucket definitions
    - describe(): Return summary with URI, bucket count, and metadata
    - to_dict(): Serialize definitions to dict with all bucket configs

    Attrs:
    - uri: S3 URI where TOML definition files are stored (s3://bucket/prefix/)
    - account: AWS account ID (inherited)
    - region: AWS region name (inherited)
    - client: boto3 S3 client (inherited)
    - bucketname: S3 bucket name parsed from uri
    - prefix: S3 key prefix parsed from uri
    - buckets: Dict mapping bucket names to BucketDefinition objects

    Example:
    ```python
    from app.model.definition.account import AccountDefinition

    account_def = AccountDefinition(
        uri="s3://config-bucket/lifecycle-rules/",
        account="123456789012",
        region="us-west-2"
    )
    account_def.load()

    print(f"Loaded {len(account_def.buckets)} bucket definitions")
    for name, bucket_def in account_def.buckets.items():
        print(f"Bucket: {name}")
    ```
    """

    def __init__(
        self,
        uri: str,
        account: str | None = None,
        region: str | None = None,
        client: object | None = None,
        parent: S3Component | None = None,
    ) -> None:
        super().__init__(
            account=account,
            region=region,
            client=client,
            parent=parent,
        )
        self.uri: str = uri
        self.bucketname = self._resolve_bucketname()
        self.prefix = self._resolve_prefix()
        self.buckets: dict[str, BucketDefinition] = {}

    def _resolve_bucketname(self) -> str:
        parsed_uri = urlparse(self.uri)
        bucket_name = parsed_uri.netloc
        return bucket_name

    def _resolve_prefix(self) -> str:
        parsed_uri = urlparse(self.uri)
        prefix = parsed_uri.path.lstrip("/")
        return prefix

    def require(
        self,
        data: dict,
        key: str,
        strict: bool = True,
    ) -> None:
        if key not in data:
            msg = f"Missing required key '{key}'"
            if strict:
                self.error(msg)
                raise KeyError(msg)
            else:
                self.warning(msg)

    def load(self) -> None:
        aggregated = {}
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=self.bucketname,
            Prefix=self.prefix,
        ):
            for obj in page.get("Contents", []):
                key = obj.get("Key", None)
                if not key or not key.endswith(".toml"):
                    continue

                # Read the object from S3
                try:
                    response = self.client.get_object(
                        Bucket=self.bucketname,
                        Key=key,
                    )
                except Exception as e:
                    msg = f"Failed to read '{key}' from '{self.bucketname}': {e}"
                    self.warning(msg)
                    continue

                # Parse the TOML content
                try:
                    content = response["Body"].read().decode("utf-8")
                    data = tomllib.loads(content)
                except Exception as e:
                    msg = f"Failed to parse TOML from '{key}' in '{self.bucketname}': {e}"
                    self.warning(msg)
                    continue

                # Check required keys
                try:
                    self.require(data, "bucket", strict=False)
                    self.require(data["bucket"], "name")
                    # self.require(data, 'lifecycleconfiguration')
                    # self.require(data['lifecycleconfiguration'], 'rules')
                except KeyError as e:
                    self.warning(f"Skipping '{key}' due to missing keys: {e}")
                    continue

                # Aggregate definitions
                target_bucket = data["bucket"]["name"]
                target_rules = []
                target_lifecycleconfiguration = data.get("lifecycleconfiguration", {})
                for _, rule in target_lifecycleconfiguration.get("rules", {}).items():
                    target_rules.append(rule)
                target_checksumalgorithm = data.get("checksumalgorithm")

                # Merge rules if bucket already exists
                if target_bucket not in aggregated:
                    aggregated[target_bucket] = LifecycleConfiguration.from_dict(
                        {
                            "bucket": target_bucket,
                            "lifecycleconfiguration": {
                                "rules": target_rules,
                            },
                            "checksumalgorithm": target_checksumalgorithm,
                        }
                    )
                else:
                    msg = f"bucket '{target_bucket}' already defined, merging rules from '{key}'"
                    self.warning(msg)
                    existing: LifecycleConfiguration = aggregated[target_bucket]
                    new: LifecycleConfiguration = LifecycleConfiguration.from_dict(
                        {
                            "bucket": target_bucket,
                            "lifecycleconfiguration": {
                                "rules": target_rules,
                            },
                            "checksumalgorithm": target_checksumalgorithm,
                        }
                    )
                    for rule in new.rules.values():
                        if rule.id in existing.rules:
                            msg = f"Rule ID '{rule.id}' already exists in bucket '{target_bucket}', skipped."
                            self.warning(msg)
                            continue
                        existing.add_rule(rule, strict=False)

        for target_bucket, lifecycle_configuration in aggregated.items():
            bucket_def = BucketDefinition(
                name=target_bucket,
                lifecycle_configuration=lifecycle_configuration,
                account=self.account,
                region=self.region,
                client=self.client,
                parent=self,
            )
            self.buckets[target_bucket] = bucket_def
        self.info(
            f"Loaded {len(self.buckets)} buckets from '{self.uri}'", context={"buckets": list(self.buckets.keys())}
        )

    def list_bucketnames(self) -> list[str]:
        return [bucket.name for bucket in self.buckets.values()]

    def describe(self) -> dict[str, Any]:
        result = super().describe()
        result["uri"] = self.uri
        result["bucketname"] = self.bucketname
        result["prefix"] = self.prefix
        if self.buckets:
            result["buckets"] = {name: bucket_def.describe() for name, bucket_def in self.buckets.items()}
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "account": self.account,
            "region": self.region,
            "uri": self.uri,
            "bucketname": self.bucketname,
            "prefix": self.prefix,
            "buckets": {name: bucket_def.to_dict() for name, bucket_def in self.buckets.items()},
        }
