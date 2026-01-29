"""Unit tests for LifecycleConfiguration class."""

from __future__ import annotations

from app.model.lifecycle.lifecycleconfiguration import LifecycleConfiguration
from app.model.lifecycle.lifecyclerule import LifecycleRule


class TestLifecycleConfiguration:
    """Test LifecycleConfiguration configuration class."""

    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        config = LifecycleConfiguration(bucket="my-bucket")
        assert config.bucket == "my-bucket"
        assert config.checksumalgorithm is None
        assert config.rules == {}
        assert config.expectedbucketowner is None
        assert config.transitiondefaultminimumobjectsize is None

    def test_init_with_bucket_and_rules(self):
        """Test initialization with bucket and rules."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule])
        assert config.bucket == "my-bucket"
        assert len(config.rules) == 1
        assert list(config.rules.values())[0].id == "test-rule"

    def test_init_with_checksum_algorithm(self):
        """Test initialization with checksum algorithm."""
        config = LifecycleConfiguration(bucket="my-bucket", checksumalgorithm="SHA256")
        assert config.checksumalgorithm == "SHA256"

    def test_init_with_all_checksum_algorithms(self):
        """Test initialization with all checksum algorithms."""
        algorithms = ["CRC32", "CRC32C", "SHA1", "SHA256"]
        for algo in algorithms:
            config = LifecycleConfiguration(bucket="my-bucket", checksumalgorithm=algo)
            assert config.checksumalgorithm == algo

    def test_init_with_expected_bucket_owner(self):
        """Test initialization with expected bucket owner."""
        config = LifecycleConfiguration(bucket="my-bucket", expectedbucketowner="123456789012")
        assert config.expectedbucketowner == "123456789012"

    def test_init_with_transition_default_minimum_object_size(self):
        """Test initialization with transition default minimum object size."""
        config = LifecycleConfiguration(
            bucket="my-bucket", transitiondefaultminimumobjectsize="all_storage_classes_128K"
        )
        assert config.transitiondefaultminimumobjectsize == "all_storage_classes_128K"

    def test_init_with_all_transition_default_options(self):
        """Test initialization with all transition default options."""
        options = ["varies_by_storage_class", "all_storage_classes_128K"]
        for option in options:
            config = LifecycleConfiguration(bucket="my-bucket", transitiondefaultminimumobjectsize=option)
            assert config.transitiondefaultminimumobjectsize == option

    def test_init_with_rules_as_objects(self):
        """Test initialization with rules as LifecycleRule objects."""
        rule1 = LifecycleRule(id="rule-1", status="Enabled")
        rule2 = LifecycleRule(id="rule-2", status="Disabled")
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule1, rule2])
        assert len(config.rules) == 2
        assert list(config.rules.values())[0].id == "rule-1"
        assert list(config.rules.values())[1].id == "rule-2"

    def test_init_with_rules_as_dicts(self):
        """Test initialization with rules as dicts."""
        rules = [{"id": "rule-1", "status": "Enabled"}, {"id": "rule-2", "status": "Disabled"}]
        config = LifecycleConfiguration(bucket="my-bucket", rules=rules)
        assert len(config.rules) == 2
        assert all(isinstance(rule, LifecycleRule) for rule in config.rules.values())
        assert list(config.rules.values())[0].id == "rule-1"
        assert list(config.rules.values())[1].id == "rule-2"

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(
            bucket="my-bucket",
            checksumalgorithm="SHA256",
            rules=[rule],
            expectedbucketowner="123456789012",
            transitiondefaultminimumobjectsize="varies_by_storage_class",
        )
        assert config.bucket == "my-bucket"
        assert config.checksumalgorithm == "SHA256"
        assert len(config.rules) == 1
        assert config.expectedbucketowner == "123456789012"
        assert config.transitiondefaultminimumobjectsize == "varies_by_storage_class"

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {
            "Bucket": "my-bucket",
            "ChecksumAlgorithm": "SHA256",
            "LifecycleConfiguration": {"Rules": [{"ID": "test-rule", "Status": "Enabled"}]},
            "ExpectedBucketOwner": "123456789012",
            "TransitionDefaultMinimumObjectSize": "varies_by_storage_class",
        }
        config = LifecycleConfiguration.from_dict(data)
        assert config.bucket == "my-bucket"
        assert config.checksumalgorithm == "SHA256"
        assert len(config.rules) == 1
        assert list(config.rules.values())[0].id == "test-rule"
        assert config.expectedbucketowner == "123456789012"
        assert config.transitiondefaultminimumobjectsize == "varies_by_storage_class"

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {
            "bucket": "my-bucket",
            "checksumalgorithm": "SHA1",
            "lifecycleconfiguration": {"rules": [{"id": "test-rule", "status": "Enabled"}]},
            "expectedbucketowner": "123456789012",
            "transitiondefaultminimumobjectsize": "all_storage_classes_128K",
        }
        config = LifecycleConfiguration.from_dict(data)
        assert config.bucket == "my-bucket"
        assert config.checksumalgorithm == "SHA1"
        assert len(config.rules) == 1
        assert list(config.rules.values())[0].id == "test-rule"
        assert config.expectedbucketowner == "123456789012"
        assert config.transitiondefaultminimumobjectsize == "all_storage_classes_128K"

    def test_from_dict_with_minimal_data(self):
        """Test from_dict with minimal data."""
        data = {"Bucket": "my-bucket"}
        config = LifecycleConfiguration.from_dict(data)
        assert config.bucket == "my-bucket"
        assert config.checksumalgorithm is None
        assert config.rules == {}
        assert config.expectedbucketowner is None
        assert config.transitiondefaultminimumobjectsize is None

    def test_from_dict_with_empty_lifecycle_configuration(self):
        """Test from_dict with empty lifecycle configuration."""
        data = {"Bucket": "my-bucket", "LifecycleConfiguration": {}}
        config = LifecycleConfiguration.from_dict(data)
        assert config.bucket == "my-bucket"
        assert config.rules == {}

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        config = LifecycleConfiguration.from_dict({})
        assert config.bucket is None
        assert config.checksumalgorithm is None
        assert config.rules == {}

    def test_describe_with_minimal_fields(self):
        """Test describe method with minimal fields."""
        config = LifecycleConfiguration(bucket="my-bucket")
        result = config.describe()
        assert result["bucket"] == "my-bucket"
        assert "checksumalgorithm" not in result
        assert "lifecycleconfiguration" not in result
        assert "expectedbucketowner" not in result
        assert "transitiondefaultminimumobjectsize" not in result

    def test_describe_with_rules(self):
        """Test describe method with rules."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule])
        result = config.describe()
        assert result["bucket"] == "my-bucket"
        assert "lifecycleconfiguration" in result
        assert "rules" in result["lifecycleconfiguration"]
        assert len(result["lifecycleconfiguration"]["rules"]) == 1

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(
            bucket="my-bucket",
            checksumalgorithm="SHA256",
            rules=[rule],
            expectedbucketowner="123456789012",
            transitiondefaultminimumobjectsize="varies_by_storage_class",
        )
        result = config.describe()
        assert result["bucket"] == "my-bucket"
        assert result["checksumalgorithm"] == "SHA256"
        assert "lifecycleconfiguration" in result
        assert result["expectedbucketowner"] == "123456789012"
        assert result["transitiondefaultminimumobjectsize"] == "varies_by_storage_class"

    def test_to_payload_with_minimal_fields(self):
        """Test to_payload method with minimal fields."""
        config = LifecycleConfiguration(bucket="my-bucket")
        result = config.to_payload()
        assert result["Bucket"] == "my-bucket"
        assert "ChecksumAlgorithm" not in result
        assert "LifecycleConfiguration" not in result
        assert "ExpectedBucketOwner" not in result
        assert "TransitionDefaultMinimumObjectSize" not in result

    def test_to_payload_with_rules(self):
        """Test to_payload method with rules."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule])
        result = config.to_payload()
        assert result["Bucket"] == "my-bucket"
        assert "LifecycleConfiguration" in result
        assert "Rules" in result["LifecycleConfiguration"]
        assert len(result["LifecycleConfiguration"]["Rules"]) == 1
        assert result["LifecycleConfiguration"]["Rules"][0]["ID"] == "test-rule"

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(
            bucket="my-bucket",
            checksumalgorithm="SHA256",
            rules=[rule],
            expectedbucketowner="123456789012",
            transitiondefaultminimumobjectsize="varies_by_storage_class",
        )
        result = config.to_payload()
        assert result["Bucket"] == "my-bucket"
        assert result["ChecksumAlgorithm"] == "SHA256"
        assert "LifecycleConfiguration" in result
        assert result["ExpectedBucketOwner"] == "123456789012"
        assert result["TransitionDefaultMinimumObjectSize"] == "varies_by_storage_class"

    def test_to_dict_with_minimal_fields(self):
        """Test to_dict method with minimal fields."""
        config = LifecycleConfiguration(bucket="my-bucket")
        result = config.to_dict()
        assert result["bucket"] == "my-bucket"
        assert result["checksumalgorithm"] is None
        assert "lifecycleconfiguration" in result
        assert result["lifecycleconfiguration"]["rules"] == []
        assert result["expectedbucketowner"] is None
        assert result["transitiondefaultminimumobjectsize"] is None

    def test_to_dict_with_rules(self):
        """Test to_dict method with rules."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule])
        result = config.to_dict()
        assert result["bucket"] == "my-bucket"
        assert "lifecycleconfiguration" in result
        assert len(result["lifecycleconfiguration"]["rules"]) == 1
        assert result["lifecycleconfiguration"]["rules"][0]["id"] == "test-rule"

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        config = LifecycleConfiguration(
            bucket="my-bucket",
            checksumalgorithm="SHA256",
            rules=[rule],
            expectedbucketowner="123456789012",
            transitiondefaultminimumobjectsize="varies_by_storage_class",
        )
        result = config.to_dict()
        assert result["bucket"] == "my-bucket"
        assert result["checksumalgorithm"] == "SHA256"
        assert len(result["lifecycleconfiguration"]["rules"]) == 1
        assert result["expectedbucketowner"] == "123456789012"
        assert result["transitiondefaultminimumobjectsize"] == "varies_by_storage_class"

    def test_resolve_rules_with_none(self):
        """Test _resolve_rules with None."""
        config = LifecycleConfiguration(bucket="my-bucket", rules=None)
        assert config.rules == {}

    def test_resolve_rules_with_mixed_types(self):
        """Test _resolve_rules with mixed object and dict types."""
        rule_obj = LifecycleRule(id="rule-1", status="Enabled")
        rule_dict = {"id": "rule-2", "status": "Disabled"}
        config = LifecycleConfiguration(bucket="my-bucket", rules=[rule_obj, rule_dict])
        assert len(config.rules) == 2
        assert all(isinstance(rule, LifecycleRule) for rule in config.rules.values())
        assert list(config.rules.values())[0].id == "rule-1"
        assert list(config.rules.values())[1].id == "rule-2"

    def test_complex_configuration_with_multiple_rules(self):
        """Test complex configuration with multiple rules."""
        rules = [
            {"ID": "rule-1", "Status": "Enabled", "Expiration": {"Days": 30}},
            {"ID": "rule-2", "Status": "Enabled", "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}]},
            {
                "ID": "rule-3",
                "Status": "Disabled",
                "NoncurrentVersionExpiration": {"NoncurrentDays": 30},
            },
        ]
        config = LifecycleConfiguration(
            bucket="my-bucket",
            checksumalgorithm="SHA256",
            rules=rules,
            expectedbucketowner="123456789012",
            transitiondefaultminimumobjectsize="varies_by_storage_class",
        )
        assert len(config.rules) == 3
        assert list(config.rules.values())[0].id == "rule-1"
        assert list(config.rules.values())[0].expiration.days == 30
        assert list(config.rules.values())[1].id == "rule-2"
        assert len(list(config.rules.values())[1].transitions) == 1
        assert list(config.rules.values())[2].id == "rule-3"
        assert list(config.rules.values())[2].noncurrent_expiration.noncurrentdays == 30

    def test_bucket_name_variations(self):
        """Test with various bucket name patterns."""
        bucket_names = ["my-bucket", "my.bucket", "my-bucket-123", "bucket123"]
        for bucket_name in bucket_names:
            config = LifecycleConfiguration(bucket=bucket_name)
            assert config.bucket == bucket_name
            result = config.to_payload()
            assert result["Bucket"] == bucket_name

    def test_empty_rules_list(self):
        """Test with empty rules list."""
        config = LifecycleConfiguration(bucket="my-bucket", rules=[])
        assert config.rules == {}
        result = config.describe()
        assert "lifecycleconfiguration" not in result
        result_payload = config.to_payload()
        assert "LifecycleConfiguration" not in result_payload
