from __future__ import annotations

from app.base.component import Component
from app.interface.payload import Payload
from app.model.definition.account import AccountDefinition
from app.model.definition.bucket import BucketDefinition
from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.resource.account import Account
from app.model.resource.bucket import Bucket


class SyncWork(Component):
    def __init__(
        self,
        parent: Component,
        payload: Payload,
    ) -> None:
        super().__init__(
            parent=parent,
        )
        self.parent = parent
        self.payload = payload

    def run(self) -> None:
        uri: str = self.payload.get("endpoint.definition")
        account: str = self.payload.get("aws.account")
        region: str = self.payload.get("aws.region")

        # Load manual account definitions
        account_def: AccountDefinition = AccountDefinition(
            uri=uri,
            account=account,
            region=region,
            parent=self,
        )
        account_def.load()

        # Load account resources
        account: Account = Account(
            account=account,
            region=region,
            parent=self,
        )
        account.load()

        # Find overlapping buckets
        bucketnames: list[str] = list(set(account_def.buckets.keys()) & set(account.buckets.keys()))
        self.info(f"Found {len(bucketnames)} overlapping buckets", context={"bucketnames": bucketnames})

        # Sync lifecycle configurations
        for bucketname in bucketnames:
            bucket_def: BucketDefinition = account_def.buckets[bucketname]
            bucket_def_lcc: LifecycleConfiguration = bucket_def.lifecycle_configuration
            bucket_res: Bucket = account.buckets[bucketname]
            bucket_res_lcc: LifecycleConfiguration = bucket_res.lifecycle_configuration
            diff_lcc = bucket_def_lcc.difference(bucket_res_lcc)
            diff_added_lcc = diff_lcc.get("added", [])
            diff_removed_lcc = diff_lcc.get("removed", [])
            self.info(
                f"Syncing lifecycle configuration for bucket '{bucketname}'",
                context={
                    "added": [rule.id for rule in diff_added_lcc],
                    "removed": [rule.id for rule in diff_removed_lcc],
                },
            )

            # Apply additions
            for rule in diff_added_lcc:
                try:
                    bucket_res.add_rule(rule)
                    self.info(f"Added rule '{rule.id}' to bucket '{bucketname}'")
                except Exception as e:
                    msg = f"Failed to add rule '{rule.id}' to bucket '{bucketname}': {e}"
                    self.warning(msg)
                    continue

            # Apply removals
            for rule in diff_removed_lcc:
                try:
                    bucket_res.remove_rule(rule)
                    self.info(f"Removed rule '{rule.id}' from bucket '{bucketname}'")
                except Exception as e:
                    msg = f"Failed to remove rule '{rule.id}' from bucket '{bucketname}': {e}"
                    self.warning(msg)
                    continue
