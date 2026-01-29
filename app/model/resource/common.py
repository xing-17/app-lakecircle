from __future__ import annotations

from datetime import date, datetime

import boto3

from app.base.component import Component


class S3Component(Component):
    """
    Description:
    - Base class for AWS S3 runtime components (Account, Bucket)
    - Extends Component with S3-specific attributes (account, region, client)
    - Supports parent-child hierarchy for configuration inheritance
    - Automatically resolves boto3 client if not provided

    Methods:
    - resolve_date(value): Convert value to date object
    - describe(): Return dict with account and region info
    - to_dict(): Return serializable dict representation

    Attrs:
    - account: AWS account ID
    - region: AWS region name
    - client: boto3 S3 client instance
    - parent: Optional parent S3Component for inheritance

    Example:
    ```python
    from app.model.resource.common import S3Component

    component = S3Component(
        account="123456789012",
        region="us-west-2"
    )
    print(component.describe())
    # {'account': '123456789012', 'region': 'us-west-2'}
    ```
    """

    def __init__(
        self,
        account: str | None = None,
        region: str | None = None,
        client: object | None = None,
        parent: Component | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.account = self._resolve_account(account)
        self.region = self._resolve_region(region)
        self.client = self._resolve_client(client)

    def _resolve_account(
        self,
        account: str | None,
    ):
        if account:
            return account
        if self.parent:
            if hasattr(self.parent, "account"):
                return getattr(self.parent, "account")
        if not account or not isinstance(account, str):
            msg = f"Provided account invalid: {account}"
            self.error(msg)
            raise ValueError(msg)
        return account

    def _resolve_region(
        self,
        region: str | None,
    ):
        if region:
            return region
        if self.parent:
            if hasattr(self.parent, "region"):
                return getattr(self.parent, "region")
        if not region or not isinstance(region, str):
            msg = f"Provided region invalid: {region}"
            self.error(msg)
            raise ValueError(msg)
        return region

    def _resolve_client(
        self,
        client: object | None = None,
    ):
        if client and isinstance(client, object):
            return client
        if self.parent:
            if hasattr(self.parent, "client"):
                return getattr(self.parent, "client")
        client = boto3.client("s3")
        return client

    def resolve_date(
        self,
        value: date | str | None,
    ) -> date | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            resolved = datetime.strptime(value, "%Y-%m-%d").date()  # YYYY-MM-DD
            return resolved
        else:
            msg = f"Invalid date value: {value!r}."
            self.error(msg)
            raise ValueError(msg)

    def describe(self) -> dict[str, str]:
        result = {}
        if self.account:
            result["account"] = self.account
        if self.region:
            result["region"] = self.region
        return result

    def to_dict(self) -> dict[str, str]:
        result = {
            "account": self.account,
            "region": self.region,
        }
        return result
