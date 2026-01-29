"""Unit tests for Bucket class."""

from __future__ import annotations

import boto3
from moto import mock_aws
from botocore.exceptions import ClientError

from app.model.resource.bucket import Bucket
from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.lifecycle.lifecyclerule import LifecycleRule


class TestBucket:
    """Test Bucket configuration class."""

    @mock_aws
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert bucket.name == "test-bucket"
        assert bucket.account == "123456789012"
        assert bucket.region == "us-west-2"
        assert bucket.client == client
        assert bucket.lifecycle_configuration is not None

    @mock_aws
    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="minimal-bucket")
        
        bucket = Bucket(
            name="minimal-bucket",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        assert bucket.name == "minimal-bucket"
        assert bucket.account == "123456789012"
        assert bucket.region == "us-east-1"

    @mock_aws
    def test_load_method_loads_lifecycle_configuration(self):
        """Test that load method loads lifecycle configuration."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        bucket.load()
        assert bucket.lifecycle_configuration is not None
        assert isinstance(bucket.lifecycle_configuration, LifecycleConfiguration)

    @mock_aws
    def test_get_lifecycle_configuration_with_no_configuration(self):
        """Test get_lifecycle_configuration when bucket has no configuration."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        config = bucket.get_lifecycle_configuration()
        assert isinstance(config, LifecycleConfiguration)

    @mock_aws
    def test_get_lifecycle_configuration_with_existing_configuration(self):
        """Test get_lifecycle_configuration when bucket has configuration."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        # Put a lifecycle configuration
        client.put_bucket_lifecycle_configuration(
            Bucket="test-bucket",
            LifecycleConfiguration={
                "Rules": [
                    {
                        "ID": "test-rule",
                        "Status": "Enabled",
                        "Prefix": "logs/",
                        "Expiration": {"Days": 30}
                    }
                ]
            }
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        config = bucket.get_lifecycle_configuration()
        assert isinstance(config, LifecycleConfiguration)
        assert len(config.rules) > 0

    @mock_aws
    def test_get_lifecycle_configuration_handles_no_such_configuration(self):
        """Test that get_lifecycle_configuration handles NoSuchLifecycleConfiguration."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="no-config-bucket")
        
        bucket = Bucket(
            name="no-config-bucket",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        # Should return empty LifecycleConfiguration, not raise error
        config = bucket.get_lifecycle_configuration()
        assert isinstance(config, LifecycleConfiguration)

    @mock_aws
    def test_put_lifecycle_configuration(self):
        """Test put_lifecycle_configuration method."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        # Create a lifecycle configuration
        rule = LifecycleRule(id="test-rule", status="Enabled", expiration={"days": 30}, prefix="logs/")
        config = LifecycleConfiguration(rules=[rule])
        
        # Put the configuration
        bucket.put_lifecycle_configuration(config)
        
        # Verify it was set
        response = client.get_bucket_lifecycle_configuration(Bucket="test-bucket")
        assert "Rules" in response
        assert len(response["Rules"]) > 0

    @mock_aws
    def test_put_lifecycle_configuration_with_empty_config_deletes(self):
        """Test put_lifecycle_configuration with empty config deletes lifecycle."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        # First, put a configuration
        client.put_bucket_lifecycle_configuration(
            Bucket="test-bucket",
            LifecycleConfiguration={
                "Rules": [
                    {
                        "ID": "test-rule",
                        "Status": "Enabled",
                        "Prefix": "logs/",
                        "Expiration": {"Days": 30}
                    }
                ]
            }
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        # Put empty configuration (should delete)
        empty_config = LifecycleConfiguration()
        bucket.put_lifecycle_configuration(empty_config)
        
        # Verify it was deleted
        try:
            client.get_bucket_lifecycle_configuration(Bucket="test-bucket")
            assert False, "Expected NoSuchLifecycleConfiguration error"
        except ClientError as e:
            assert e.response["Error"]["Code"] == "NoSuchLifecycleConfiguration"

    @mock_aws
    def test_add_rule_with_lifecycle_rule_object(self):
        """Test add_rule with LifecycleRule object."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        rule = LifecycleRule(id="new-rule", status="Enabled", expiration={"days": 60}, prefix="logs/")
        bucket.add_rule(rule)
        
        # Verify the rule was added
        config = bucket.get_lifecycle_configuration()
        assert any(rule.id == "new-rule" for rule in config.rules.values())

    @mock_aws
    def test_add_rule_with_dict(self):
        """Test add_rule with dict."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        rule_dict = {
            "ID": "dict-rule",
            "Status": "Enabled",
            "Expiration": {"Days": 90},
            "Prefix": "data/",
        }
        bucket.add_rule(rule_dict)
        
        # Verify the rule was added
        config = bucket.get_lifecycle_configuration()
        assert any(rule.id == "dict-rule" for rule in config.rules.values())

    @mock_aws
    def test_add_rule_with_invalid_type_raises_error(self):
        """Test add_rule with invalid type raises ValueError."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        
        try:
            bucket.add_rule("invalid-rule")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "must be an instance of LifecycleRule or dict" in str(e)

    @mock_aws
    def test_remove_rule_with_lifecycle_rule_object(self):
        """Test remove_rule with LifecycleRule object."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        # Put initial configuration
        client.put_bucket_lifecycle_configuration(
            Bucket="test-bucket",
            LifecycleConfiguration={
                "Rules": [
                    {
                        "ID": "rule-to-remove",
                        "Status": "Enabled",
                        "Prefix": "logs/",
                        "Expiration": {"Days": 30}
                    }
                ]
            }
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        rule = LifecycleRule(id="rule-to-remove", status="Enabled", prefix="logs/", expiration={"days": 30})
        bucket.remove_rule(rule)
        
        # Verify the rule was removed
        config = bucket.get_lifecycle_configuration()
        assert not any(rule.id == "rule-to-remove" for rule in config.rules.values())

    @mock_aws
    def test_remove_rule_with_dict(self):
        """Test remove_rule with dict."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        # Put initial configuration
        client.put_bucket_lifecycle_configuration(
            Bucket="test-bucket",
            LifecycleConfiguration={
                "Rules": [
                    {
                        "ID": "dict-rule-remove",
                        "Status": "Enabled",
                        "Prefix": "logs/",
                        "Expiration": {"Days": 30}
                    }
                ]
            }
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        rule_dict = {
            "ID": "dict-rule-remove",
            "Status": "Enabled",
            "Prefix": "logs/",
            "Expiration": {"Days": 30},
        }
        bucket.remove_rule(rule_dict)
        
        # Verify the rule was removed
        config = bucket.get_lifecycle_configuration()
        assert not any(rule.id == "dict-rule-remove" for rule in config.rules.values())

    @mock_aws
    def test_remove_rule_with_invalid_type_raises_error(self):
        """Test remove_rule with invalid type raises ValueError."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        
        try:
            bucket.remove_rule(12345)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "must be an instance of LifecycleRule or dict" in str(e)

    @mock_aws
    def test_describe_returns_dict_with_name(self):
        """Test that describe returns dict with bucket name."""
        client = boto3.client("s3", region_name="ap-southeast-2")
        client.create_bucket(
            Bucket="describe-bucket",
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"}
        )
        
        bucket = Bucket(
            name="describe-bucket",
            account="123456789012",
            region="ap-southeast-2",
            client=client,
        )
        result = bucket.describe()
        assert isinstance(result, dict)
        assert result["name"] == "describe-bucket"
        assert result["account"] == "123456789012"
        assert result["region"] == "ap-southeast-2"

    @mock_aws
    def test_to_dict_returns_serializable_dict(self):
        """Test that to_dict returns a serializable dictionary."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        result = bucket.to_dict()
        assert isinstance(result, dict)
        assert "name" in result
        assert "account" in result
        assert "region" in result
        assert "lifecycle_configuration" in result
        assert result["name"] == "test-bucket"

    @mock_aws
    def test_bucket_inheritance_from_s3component(self):
        """Test that Bucket inherits from S3Component."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="test-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert hasattr(bucket, "describe")
        assert hasattr(bucket, "to_dict")
        assert hasattr(bucket, "resolve_date")

    @mock_aws
    def test_bucket_with_parent(self):
        """Test bucket with parent S3Component."""
        from app.model.resource.account import Account
        
        client = boto3.client("s3", region_name="us-east-1")
        account = Account(
            account="parent-account",
            region="us-east-1",
            client=client,
        )
        
        client.create_bucket(Bucket="child-bucket")
        
        bucket = Bucket(
            name="child-bucket",
            account=None,
            region=None,
            parent=account,
        )
        
        # Should inherit from parent
        assert bucket.account == "parent-account"
        assert bucket.region == "us-east-1"
        assert bucket.parent == account

    @mock_aws
    def test_add_and_remove_rule_workflow(self):
        """Test complete workflow of adding and removing rules."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="workflow-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket = Bucket(
            name="workflow-bucket",
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        
        # Add first rule
        rule1 = LifecycleRule(id="rule-1", status="Enabled", expiration={"days": 30}, prefix="logs/")
        bucket.add_rule(rule1)
        
        # Add second rule
        rule2 = LifecycleRule(id="rule-2", status="Enabled", expiration={"days": 60}, prefix="data/")
        bucket.add_rule(rule2)
        
        # Verify both rules exist
        config = bucket.get_lifecycle_configuration()
        assert any(rule.id == "rule-1" for rule in config.rules.values())
        assert any(rule.id == "rule-2" for rule in config.rules.values())
        
        # Remove first rule
        bucket.remove_rule(rule1)
        
        # Verify only second rule remains
        config = bucket.get_lifecycle_configuration()
        assert not any(rule.id == "rule-1" for rule in config.rules.values())
        assert any(rule.id == "rule-2" for rule in config.rules.values())

    @mock_aws
    def test_bucket_name_with_special_characters(self):
        """Test bucket with various naming formats."""
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="my-test-bucket-123")
        
        bucket = Bucket(
            name="my-test-bucket-123",
            account="123456789012",
            region="us-east-1",
            client=client,
        )
        assert bucket.name == "my-test-bucket-123"

    @mock_aws
    def test_multiple_buckets_different_configurations(self):
        """Test creating multiple Bucket objects with different configurations."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="bucket-1",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        client.create_bucket(
            Bucket="bucket-2",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        bucket1 = Bucket(name="bucket-1", account="111111111111", region="us-west-2", client=client)
        bucket2 = Bucket(name="bucket-2", account="222222222222", region="us-west-2", client=client)
        
        assert bucket1.name == "bucket-1"
        assert bucket2.name == "bucket-2"
        assert bucket1.account != bucket2.account
