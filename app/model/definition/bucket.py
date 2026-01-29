from __future__ import annotations

from typing import Any

from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.resource.common import S3Component


class BucketDefinition(S3Component):
    """
    Description:
    - Represents a bucket's lifecycle configuration definition from TOML
    - Stores lifecycle rules without performing AWS API operations
    - Used by AccountDefinition to aggregate configurations

    Methods:
    - describe(): Return dict with bucket name and lifecycle config
    - to_dict(): Serialize definition to dict format

    Attrs:
    - name: S3 bucket name
    - account: AWS account ID (inherited)
    - region: AWS region name (inherited)
    - client: boto3 S3 client (inherited)
    - lifecycle_configuration: LifecycleConfiguration object or None

    Example:
    ```python
    from app.model.definition.bucket import BucketDefinition
    from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration

    bucket_def = BucketDefinition(
        name="my-bucket",
        account="123456789012",
        region="us-west-2",
        lifecycle_configuration={
            "LifecycleConfiguration": {
                "Rules": [{"ID": "rule1", "Status": "Enabled"}]
            }
        }
    )
    print(bucket_def.describe())
    ```
    """

    def __init__(
        self,
        name: str,
        account: str | None = None,
        region: str | None = None,
        client: object | None = None,
        parent: S3Component | None = None,
        lifecycle_configuration: LifecycleConfiguration | dict | None = None,
    ) -> None:
        super().__init__(
            account=account,
            region=region,
            client=client,
            parent=parent,
        )
        self.name: str = name
        self.lifecycle_configuration: LifecycleConfiguration | None = self._resolve_lifecycle_configuration(
            lifecycle_configuration,
        )

    def _resolve_lifecycle_configuration(
        self,
        lifecycle_configuration: LifecycleConfiguration | dict | None,
    ) -> LifecycleConfiguration | None:
        if lifecycle_configuration is None:
            return None
        if isinstance(lifecycle_configuration, dict):
            return LifecycleConfiguration.from_dict(lifecycle_configuration)
        if isinstance(lifecycle_configuration, LifecycleConfiguration):
            return lifecycle_configuration
        raise ValueError("Invalid lifecycle_configuration type")

    def describe(self) -> dict[str, Any]:
        result = super().describe()
        result["name"] = self.name
        if self.lifecycle_configuration:
            result["lifecycle_configuration"] = self.lifecycle_configuration.describe()
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "account": self.account,
            "region": self.region,
            "lifecycle_configuration": self.lifecycle_configuration.to_dict() if self.lifecycle_configuration else None,
        }
