"""Unit tests for BucketDefinition class."""

from __future__ import annotations

import boto3
from moto import mock_aws

from app.model.definition.bucket import BucketDefinition
from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.lifecycle.lifecyclerule import LifecycleRule


class TestBucketDefinition:
    """Test BucketDefinition configuration class."""

    @mock_aws
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        client = boto3.client("s3", region_name="us-west-2")
        config = LifecycleConfiguration(
            rules=[LifecycleRule(id="test-rule", status="Enabled", expiration={"days": 30})]
        )

        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
            lifecycle_configuration=config,
        )
        assert bucket_def.name == "test-bucket"
        assert bucket_def.account == "123456789012"
        assert bucket_def.region == "us-west-2"
        assert bucket_def.client == client
        assert bucket_def.lifecycle_configuration == config

    @mock_aws
    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        bucket_def = BucketDefinition(
            name="minimal-bucket",
            account="123456789012",
            region="us-east-1",
        )
        assert bucket_def.name == "minimal-bucket"
        assert bucket_def.account == "123456789012"
        assert bucket_def.region == "us-east-1"
        assert bucket_def.lifecycle_configuration is None

    @mock_aws
    def test_init_with_none_lifecycle_configuration(self):
        """Test initialization with None lifecycle_configuration."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=None,
        )
        assert bucket_def.lifecycle_configuration is None

    @mock_aws
    def test_init_with_dict_lifecycle_configuration(self):
        """Test initialization with dict lifecycle_configuration."""
        config_dict = {
            "LifecycleConfiguration": {"Rules": [{"ID": "dict-rule", "Status": "Enabled", "Expiration": {"Days": 60}}]}
        }
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config_dict,
        )
        assert isinstance(bucket_def.lifecycle_configuration, LifecycleConfiguration)
        assert len(bucket_def.lifecycle_configuration.rules) == 1
        # Check that a rule exists with the expected ID
        rule_ids = [rule.id for rule in bucket_def.lifecycle_configuration.rules.values()]
        assert "dict-rule" in rule_ids

    @mock_aws
    def test_init_with_lifecycle_configuration_object(self):
        """Test initialization with LifecycleConfiguration object."""
        config = LifecycleConfiguration(
            rules=[LifecycleRule(id="object-rule", status="Enabled", expiration={"days": 90})]
        )
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config,
        )
        assert bucket_def.lifecycle_configuration == config
        assert len(bucket_def.lifecycle_configuration.rules) == 1
        # Check that a rule exists with the expected ID
        rule_ids = [rule.id for rule in bucket_def.lifecycle_configuration.rules.values()]
        assert "object-rule" in rule_ids

    @mock_aws
    def test_resolve_lifecycle_configuration_with_none(self):
        """Test _resolve_lifecycle_configuration with None."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
        )
        result = bucket_def._resolve_lifecycle_configuration(None)
        assert result is None

    @mock_aws
    def test_resolve_lifecycle_configuration_with_dict(self):
        """Test _resolve_lifecycle_configuration with dict."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
        )
        config_dict = {"Rules": [{"ID": "test", "Status": "Enabled", "Expiration": {"Days": 30}}]}
        result = bucket_def._resolve_lifecycle_configuration(config_dict)
        assert isinstance(result, LifecycleConfiguration)

    @mock_aws
    def test_resolve_lifecycle_configuration_with_object(self):
        """Test _resolve_lifecycle_configuration with LifecycleConfiguration object."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
        )
        config = LifecycleConfiguration()
        result = bucket_def._resolve_lifecycle_configuration(config)
        assert result == config

    @mock_aws
    def test_resolve_lifecycle_configuration_with_invalid_type_raises_error(self):
        """Test _resolve_lifecycle_configuration with invalid type raises ValueError."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
        )
        try:
            bucket_def._resolve_lifecycle_configuration("invalid")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Invalid lifecycle_configuration type" in str(e)

    @mock_aws
    def test_describe_without_lifecycle_configuration(self):
        """Test describe without lifecycle_configuration."""
        bucket_def = BucketDefinition(
            name="describe-bucket",
            account="123456789012",
            region="ap-southeast-2",
        )
        result = bucket_def.describe()
        assert isinstance(result, dict)
        assert result["name"] == "describe-bucket"
        assert result["account"] == "123456789012"
        assert result["region"] == "ap-southeast-2"
        assert "lifecycle_configuration" not in result

    @mock_aws
    def test_describe_with_lifecycle_configuration(self):
        """Test describe with lifecycle_configuration."""
        config = LifecycleConfiguration(rules=[LifecycleRule(id="rule-1", status="Enabled", expiration={"days": 30})])
        bucket_def = BucketDefinition(
            name="describe-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config,
        )
        result = bucket_def.describe()
        assert isinstance(result, dict)
        assert result["name"] == "describe-bucket"
        assert "lifecycle_configuration" in result
        assert isinstance(result["lifecycle_configuration"], dict)

    @mock_aws
    def test_bucket_definition_inheritance_from_s3component(self):
        """Test that BucketDefinition inherits from S3Component."""
        bucket_def = BucketDefinition(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
        )
        assert hasattr(bucket_def, "describe")
        assert hasattr(bucket_def, "to_dict")
        assert hasattr(bucket_def, "resolve_date")

    @mock_aws
    def test_bucket_definition_with_parent(self):
        """Test BucketDefinition with parent S3Component."""
        from app.model.definition.account import AccountDefinition

        client = boto3.client("s3", region_name="us-east-1")
        # Create a mock S3 bucket for the definition storage
        client.create_bucket(Bucket="config-bucket")

        account_def = AccountDefinition(
            uri="s3://config-bucket/definitions/",
            account="parent-account",
            region="us-east-1",
            client=client,
        )

        bucket_def = BucketDefinition(
            name="child-bucket",
            account=None,
            region=None,
            parent=account_def,
        )

        # Should inherit from parent
        assert bucket_def.account == "parent-account"
        assert bucket_def.region == "us-east-1"
        assert bucket_def.parent == account_def

    @mock_aws
    def test_multiple_bucket_definitions(self):
        """Test creating multiple BucketDefinition objects."""
        client = boto3.client("s3", region_name="us-west-2")

        bucket_def1 = BucketDefinition(
            name="bucket-1",
            account="111111111111",
            region="us-west-2",
            client=client,
        )
        bucket_def2 = BucketDefinition(
            name="bucket-2",
            account="222222222222",
            region="us-east-1",
            client=client,
        )

        assert bucket_def1.name == "bucket-1"
        assert bucket_def2.name == "bucket-2"
        assert bucket_def1.account != bucket_def2.account

    @mock_aws
    def test_bucket_definition_name_with_special_characters(self):
        """Test BucketDefinition with various naming formats."""
        bucket_def = BucketDefinition(
            name="my-test-bucket-123",
            account="123456789012",
            region="us-east-1",
        )
        assert bucket_def.name == "my-test-bucket-123"

    @mock_aws
    def test_bucket_definition_with_complex_lifecycle_configuration(self):
        """Test BucketDefinition with complex lifecycle configuration."""
        config = LifecycleConfiguration(
            rules=[
                LifecycleRule(id="rule-1", status="Enabled", expiration={"days": 30}),
                LifecycleRule(id="rule-2", status="Enabled", expiration={"days": 60}),
                LifecycleRule(id="rule-3", status="Disabled", expiration={"days": 90}),
            ]
        )
        bucket_def = BucketDefinition(
            name="complex-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config,
        )
        assert len(bucket_def.lifecycle_configuration.rules) == 3
        # Check that all three rules exist with expected IDs
        rule_ids = [rule.id for rule in bucket_def.lifecycle_configuration.rules.values()]
        assert "rule-1" in rule_ids
        assert "rule-2" in rule_ids
        assert "rule-3" in rule_ids

    @mock_aws
    def test_bucket_definition_describe_returns_nested_lifecycle_config(self):
        """Test that describe returns nested lifecycle_configuration description."""
        rule = LifecycleRule(id="nested-rule", status="Enabled", expiration={"days": 45})
        config = LifecycleConfiguration(rules=[rule])
        bucket_def = BucketDefinition(
            name="nested-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config,
        )
        result = bucket_def.describe()
        assert "lifecycle_configuration" in result
        assert "lifecycleconfiguration" in result["lifecycle_configuration"]
        assert "rules" in result["lifecycle_configuration"]["lifecycleconfiguration"]

    @mock_aws
    def test_bucket_definition_with_empty_lifecycle_configuration(self):
        """Test BucketDefinition with empty LifecycleConfiguration."""
        config = LifecycleConfiguration()  # No rules
        bucket_def = BucketDefinition(
            name="empty-config-bucket",
            account="123456789012",
            region="us-west-2",
            lifecycle_configuration=config,
        )
        assert bucket_def.lifecycle_configuration is not None
        assert len(bucket_def.lifecycle_configuration.rules) == 0
