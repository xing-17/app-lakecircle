"""Unit tests for AccountDefinition class."""

from __future__ import annotations

import boto3
from moto import mock_aws

from app.model.definition.account import AccountDefinition
from app.model.definition.bucket import BucketDefinition


class TestAccountDefinition:
    """Test AccountDefinition configuration class."""

    @mock_aws
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert account_def.uri == "s3://config-bucket/definitions/"
        assert account_def.account == "123456789012"
        assert account_def.region == "us-west-2"
        assert account_def.client == client
        assert account_def.bucketname == "config-bucket"
        assert account_def.prefix == "definitions/"

    @mock_aws
    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="minimal-bucket")

        account_def = AccountDefinition(
            uri="s3://minimal-bucket/",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        assert account_def.uri == "s3://minimal-bucket/"
        assert account_def.account == "123456789012"
        assert account_def.region == "us-east-1"

    @mock_aws
    def test_resolve_bucketname_from_uri(self):
        """Test _resolve_bucketname extracts bucket name from URI."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="my-config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://my-config-bucket/path/to/configs/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert account_def.bucketname == "my-config-bucket"

    @mock_aws
    def test_resolve_prefix_from_uri(self):
        """Test _resolve_prefix extracts prefix from URI."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/path/to/configs/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert account_def.prefix == "path/to/configs/"

    @mock_aws
    def test_resolve_prefix_with_root_path(self):
        """Test _resolve_prefix with root path."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert account_def.prefix == ""

    @mock_aws
    def test_require_with_existing_key(self):
        """Test require method with existing key."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        data = {"bucket": {"name": "test-bucket"}, "rules": []}
        # Should not raise
        account_def.require(data, "bucket")
        account_def.require(data, "rules")

    @mock_aws
    def test_require_with_missing_key_strict_true(self):
        """Test require method with missing key in strict mode."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        data = {"rules": []}
        try:
            account_def.require(data, "bucket", strict=True)
            assert False, "Expected KeyError"
        except KeyError as e:
            assert "Missing required key 'bucket'" in str(e)

    @mock_aws
    def test_require_with_missing_key_strict_false(self):
        """Test require method with missing key in non-strict mode."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://config-bucket/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        data = {"rules": []}
        # Should not raise, just warn
        account_def.require(data, "bucket", strict=False)

    @mock_aws
    def test_load_with_no_toml_files(self):
        """Test load method with no TOML files in S3."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="empty-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://empty-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        assert len(account_def.buckets) == 0

    @mock_aws
    def test_load_with_single_toml_file(self):
        """Test load method with single TOML file."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload a TOML file
        toml_content = """
[bucket]
name = "test-bucket"

[[rules]]
ID = "rule-1"
Status = "Enabled"

[rules.Expiration]
Days = 30
"""
        client.put_object(Bucket="config-bucket", Key="definitions/test.toml", Body=toml_content.encode("utf-8"))

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        assert len(account_def.buckets) == 1
        assert "test-bucket" in account_def.buckets
        assert isinstance(account_def.buckets["test-bucket"], BucketDefinition)

    @mock_aws
    def test_load_with_multiple_toml_files(self):
        """Test load method with multiple TOML files."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload multiple TOML files
        toml1 = """
[bucket]
name = "bucket-1"

[lifecycleconfiguration.rules.1]
id = "rule-1"
status = "Enabled"
expiration = { days = 30 }
"""
        toml2 = """
[bucket]
name = "bucket-2"

[lifecycleconfiguration.rules.1]
status = "Enabled"
expiration = { days = 60 }

"""
        client.put_object(Bucket="config-bucket", Key="definitions/bucket1.toml", Body=toml1.encode("utf-8"))
        client.put_object(Bucket="config-bucket", Key="definitions/bucket2.toml", Body=toml2.encode("utf-8"))

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        assert len(account_def.buckets) == 2
        assert "bucket-1" in account_def.buckets
        assert "bucket-2" in account_def.buckets

    @mock_aws
    def test_load_merges_rules_for_same_bucket(self):
        """Test that load merges rules from multiple files for the same bucket."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload multiple TOML files
        toml1 = """
[bucket]
name = "shared-bucket"

[lifecycleconfiguration.rules.1]
id = "rule-1"
status = "Enabled"
expiration = { days = 30 }
"""
        toml2 = """
[bucket]
name = "shared-bucket"

[lifecycleconfiguration.rules.2]
id = "rule-2"
status = "Enabled"
expiration = { days = 60 }

"""
        client.put_object(Bucket="config-bucket", Key="definitions/shared1.toml", Body=toml1.encode("utf-8"))
        client.put_object(Bucket="config-bucket", Key="definitions/shared2.toml", Body=toml2.encode("utf-8"))

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        assert len(account_def.buckets) == 1
        assert "shared-bucket" in account_def.buckets

        bucket_def = account_def.buckets["shared-bucket"]
        # Should have both rules merged
        assert len(bucket_def.lifecycle_configuration.rules) == 2
        # Check that both rule IDs are present
        rule_ids = [rule.id for rule in bucket_def.lifecycle_configuration.rules.values()]
        assert "rule-1" in rule_ids
        assert "rule-2" in rule_ids

    @mock_aws
    def test_load_skips_non_toml_files(self):
        """Test that load skips non-TOML files."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload multiple TOML files
        toml1 = """
[bucket]
name = "bucket-1"

[lifecycleconfiguration.rules.1]
id = "rule-1"
status = "Enabled"
expiration = { days = 30 }
"""
        client.put_object(Bucket="config-bucket", Key="definitions/test.toml", Body=toml1.encode("utf-8"))
        client.put_object(Bucket="config-bucket", Key="definitions/readme.txt", Body=b"Not a TOML file")

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        assert len(account_def.buckets) == 1

    @mock_aws
    def test_load_handles_malformed_toml(self):
        """Test that load handles malformed TOML files gracefully."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload malformed TOML
        malformed_toml = "this is [ not valid toml"
        client.put_object(Bucket="config-bucket", Key="definitions/malformed.toml", Body=malformed_toml.encode("utf-8"))

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        # Should not raise, just log warning
        account_def.load()
        assert len(account_def.buckets) == 0

    @mock_aws
    def test_load_handles_missing_required_keys(self):
        """Test that load handles TOML files missing required keys."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Upload TOML missing 'rules' key
        incomplete_toml = """
[bucket]
name = "incomplete-bucket"
"""
        client.put_object(
            Bucket="config-bucket", Key="definitions/incomplete.toml", Body=incomplete_toml.encode("utf-8")
        )

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        # Should not raise, just log warning and skip
        account_def.load()
        assert len(account_def.buckets) == 1

    @mock_aws
    def test_describe_returns_correct_info(self):
        """Test describe method returns correct information."""
        client = boto3.client("s3", region_name="ap-southeast-2")
        client.create_bucket(
            Bucket="describe-bucket", CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"}
        )

        account_def = AccountDefinition(
            uri="s3://describe-bucket/configs/",
            account="999888777666",
            region="ap-southeast-2",
            client=client,
        )

        result = account_def.describe()
        assert isinstance(result, dict)
        assert result["account"] == "999888777666"
        assert result["region"] == "ap-southeast-2"
        assert result["uri"] == "s3://describe-bucket/configs/"
        assert result["bucketname"] == "describe-bucket"
        assert result["prefix"] == "configs/"

    @mock_aws
    def test_to_dict_returns_complete_structure(self):
        """Test to_dict method returns complete structure."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="dict-bucket")

        account_def = AccountDefinition(
            uri="s3://dict-bucket/path/",
            account="111222333444",
            region="us-east-1",
            client=client,
        )

        result = account_def.to_dict()
        assert result["account"] == "111222333444"
        assert result["region"] == "us-east-1"
        assert result["uri"] == "s3://dict-bucket/path/"
        assert result["bucketname"] == "dict-bucket"
        assert result["prefix"] == "path/"
        assert "buckets" in result
        assert isinstance(result["buckets"], dict)

    @mock_aws
    def test_account_definition_inheritance_from_s3component(self):
        """Test that AccountDefinition inherits from S3Component."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        account_def = AccountDefinition(
            uri="s3://test-bucket/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert hasattr(account_def, "describe")
        assert hasattr(account_def, "to_dict")
        assert hasattr(account_def, "resolve_date")

    @mock_aws
    def test_buckets_have_parent_reference(self):
        """Test that loaded bucket definitions have parent reference."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(Bucket="config-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        toml_content = """
[bucket]
name = "child-bucket"

[[rules]]
ID = "rule-1"
Status = "Enabled"

[rules.Expiration]
Days = 30
"""
        client.put_object(Bucket="config-bucket", Key="defs/child.toml", Body=toml_content.encode("utf-8"))

        account_def = AccountDefinition(
            uri="s3://config-bucket/defs/",
            account="123456789012",
            region="us-west-2",
            client=client,
        )

        account_def.load()
        bucket_def = account_def.buckets["child-bucket"]
        assert bucket_def.parent == account_def
        assert bucket_def.account == "123456789012"
        assert bucket_def.region == "us-west-2"

    @mock_aws
    def test_multiple_accounts_different_uris(self):
        """Test creating multiple AccountDefinition objects with different URIs."""
        client1 = boto3.client("s3", region_name="us-east-1")
        client2 = boto3.client("s3", region_name="eu-west-1")

        client1.create_bucket(Bucket="account1-config")
        client2.create_bucket(Bucket="account2-config", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"})

        account_def1 = AccountDefinition(
            uri="s3://account1-config/",
            account="111111111111",
            region="us-east-1",
            client=client1,
        )
        account_def2 = AccountDefinition(
            uri="s3://account2-config/",
            account="222222222222",
            region="eu-west-1",
            client=client2,
        )

        assert account_def1.bucketname == "account1-config"
        assert account_def2.bucketname == "account2-config"
        assert account_def1.account != account_def2.account
