from __future__ import annotations

from typing import Any

from app.model.resource.bucket import Bucket
from app.model.resource.common import S3Component


class Account(S3Component):
    """
    Description:
    - Represents an AWS account with S3 bucket listing capabilities
    - Automatically loads buckets in specified region upon initialization
    - Provides runtime access to AWS S3 buckets via boto3

    Methods:
    - list_buckets(): Retrieve list of Bucket objects in account region
    - describe(): Return account info with bucket count and names
    - to_dict(): Serialize account and buckets to dict

    Attrs:
    - account: AWS account ID (inherited)
    - region: AWS region name (inherited)
    - client: boto3 S3 client (inherited)
    - buckets: List of Bucket objects in this region

    Example:
    ```python
    from app.model.resource.account import Account

    account = Account(
        account="123456789012",
        region="us-west-2"
    )
    print(f"Found {len(account.buckets)} buckets")
    for bucket in account.buckets:
        print(bucket.name)
    ```
    """

    def __init__(
        self,
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
        self.buckets: dict[str, Bucket] = {}

    def load(self) -> None:
        for bucket in self.list_buckets():
            self.buckets[bucket.name] = bucket

    def list_buckets(self) -> list[Bucket]:
        buckets = []
        try:
            response = self.client.list_buckets()
        except Exception as e:
            msg = f"Failed to list buckets for account {self.account}: {e}"
            self.error(msg)
            raise RuntimeError(msg) from e

        for bucketmeta in response.get("Buckets", []):
            bucketname = bucketmeta.get("Name", None)
            if bucketname:
                bucket = Bucket(
                    name=bucketname,
                    account=self.account,
                    region=self.region,
                    client=self.client,
                    parent=self,
                )
                buckets.append(bucket)
        return buckets

    def list_bucketnames(self) -> list[str]:
        return [bucket.name for bucket in self.buckets.values()]

    def describe(self) -> dict[str, Any]:
        result = super().describe()
        result["buckets_count"] = len(self.buckets)
        result["bucket_names"] = [bucket.name for bucket in self.buckets.values()]
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "account": self.account,
            "region": self.region,
            "buckets": [bucket.describe() for bucket in self.buckets.values()],
        }
