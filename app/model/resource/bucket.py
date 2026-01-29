from __future__ import annotations

import traceback
from typing import Any

from botocore.exceptions import ClientError

from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.lifecycle.lifecyclerule import LifecycleRule
from app.model.resource.common import S3Component


class Bucket(S3Component):
    """
    Description:
    - Represents an AWS S3 bucket with lifecycle configuration management
    - Provides CRUD operations for bucket lifecycle rules
    - Supports loading, updating, and modifying lifecycle configurations

    Methods:
    - load(): Fetch and store current lifecycle configuration from AWS
    - get_lifecycle_configuration(): Retrieve lifecycle config from S3
    - put_lifecycle_configuration(config): Update lifecycle config in S3
    - add_rule(rule): Add a lifecycle rule to the bucket
    - delete_rule(rule): Remove a lifecycle rule from the bucket
    - describe(): Return bucket info with lifecycle configuration
    - to_dict(): Serialize bucket to dict format

    Attrs:
    - name: S3 bucket name
    - account: AWS account ID (inherited)
    - region: AWS region name (inherited)
    - client: boto3 S3 client (inherited)
    - lifecycle_configuration: LifecycleConfiguration object or None

    Example:
    ```python
    from app.model.resource.bucket import Bucket
    from app.model.lifecycle.lifecyclerule import LifecycleRule

    bucket = Bucket(
        name="my-bucket",
        account="123456789012",
        region="us-west-2"
    )
    bucket.load()

    # Add a new rule
    rule = LifecycleRule(id="archive", status="Enabled", expiration={"days": 30})
    bucket.add_rule(rule)
    ```
    """

    def __init__(
        self,
        name: str,
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
        self.name: str = name
        self.lifecycle_configuration: LifecycleConfiguration | None = None
        self.load()

    def load(self) -> None:
        self.lifecycle_configuration = self.get_lifecycle_configuration()

    def get_lifecycle_configuration(self) -> LifecycleConfiguration:
        try:
            response = self.client.get_bucket_lifecycle_configuration(
                Bucket=self.name,
            )
            return LifecycleConfiguration.from_dict(response)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchLifecycleConfiguration":
                return LifecycleConfiguration()
            msg = f"Failed to get lifecycle configuration for '{self.name}': {e}"
            self.warning(msg)
            return LifecycleConfiguration()
        except Exception as e:
            msg = f"Failed to get lifecycle configuration for '{self.name}': {e}"
            self.warning(msg)
            return LifecycleConfiguration()

    def put_lifecycle_configuration(
        self,
        lifecycle_configuration: LifecycleConfiguration,
    ) -> None:
        payload = lifecycle_configuration.to_payload()
        lifecycle_config_param = payload.get("LifecycleConfiguration", {})

        # If no rules, delete the lifecycle configuration instead of putting empty config
        if not lifecycle_config_param or not lifecycle_config_param.get("Rules"):
            try:
                self.client.delete_bucket_lifecycle(Bucket=self.name)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                # Ignore if there was no configuration to delete
                if error_code != "NoSuchLifecycleConfiguration":
                    msg = f"Failed to delete lifecycle configuration for '{self.name}': {e}"
                    self.error(msg)
                    raise RuntimeError(msg) from e
            return

        try:
            self.client.put_bucket_lifecycle_configuration(
                Bucket=self.name,
                LifecycleConfiguration=lifecycle_config_param,
            )
        except Exception:
            error_trackback = traceback.format_exc()
            msg = f"Failed to put lifecycle configuration for '{self.name}'"
            self.error(
                msg,
                context={"traceback": error_trackback.splitlines()},
            )
            raise RuntimeError(msg)

    def remove_rule(
        self,
        rule: LifecycleRule | dict,
    ) -> None:
        if isinstance(rule, dict):
            rule = LifecycleRule.from_dict(rule)
        if not isinstance(rule, LifecycleRule):
            msg = "rule must be an instance of LifecycleRule or dict"
            raise ValueError(msg)
        if not self.lifecycle_configuration:
            self.load()
        if self.lifecycle_configuration:
            self.lifecycle_configuration.remove_rule(rule, strict=False)
            self.put_lifecycle_configuration(self.lifecycle_configuration)

    def add_rule(
        self,
        rule: LifecycleRule | dict,
    ) -> None:
        if isinstance(rule, dict):
            rule = LifecycleRule.from_dict(rule)
        if not isinstance(rule, LifecycleRule):
            msg = "rule must be an instance of LifecycleRule or dict"
            raise ValueError(msg)
        if not self.lifecycle_configuration:
            self.load()
        if self.lifecycle_configuration:
            self.lifecycle_configuration.add_rule(rule, strict=False)
            self.put_lifecycle_configuration(self.lifecycle_configuration)

    def describe(self) -> dict[str, Any]:
        result = super().describe()
        result["name"] = self.name
        if self.lifecycle_configuration:
            result["lifecycle_configuration"] = self.lifecycle_configuration.describe()
        return result

    def to_dict(self) -> dict[str, Any]:
        if self.lifecycle_configuration:
            lcc = self.lifecycle_configuration.to_dict()
        else:
            lcc = None
        return {
            "name": self.name,
            "account": self.account,
            "region": self.region,
            "lifecycle_configuration": lcc,
        }
