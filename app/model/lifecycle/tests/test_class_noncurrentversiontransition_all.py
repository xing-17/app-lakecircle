"""Unit tests for NoncurrentVersionTransition class."""

from __future__ import annotations

from app.model.lifecycle.noncurrentversiontransition import NoncurrentVersionTransition
from app.model.lifecycle.storageclass import StorageClass


class TestNoncurrentVersionTransition:
    """Test NoncurrentVersionTransition configuration class."""

    def test_init_with_noncurrentdays_and_storageclass(self):
        """Test initialization with noncurrent days and storage class."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass="GLACIER")
        assert nvt.noncurrentdays == 30
        assert nvt.storageclass == StorageClass.GLACIER
        assert nvt.newernoncurrentversions is None

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, newernoncurrentversions=5, storageclass="STANDARD_IA")
        assert nvt.noncurrentdays == 30
        assert nvt.newernoncurrentversions == 5
        assert nvt.storageclass == StorageClass.STANDARD_IA

    def test_init_with_string_values(self):
        """Test initialization with string values."""
        nvt = NoncurrentVersionTransition(noncurrentdays="30", newernoncurrentversions="5", storageclass="GLACIER")
        assert nvt.noncurrentdays == 30
        assert nvt.newernoncurrentversions == 5
        assert isinstance(nvt.noncurrentdays, int)
        assert isinstance(nvt.newernoncurrentversions, int)

    def test_init_with_storageclass_enum(self):
        """Test initialization with StorageClass enum."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass=StorageClass.DEEP_ARCHIVE)
        assert nvt.storageclass == StorageClass.DEEP_ARCHIVE

    def test_init_with_no_parameters(self):
        """Test initialization with no parameters."""
        nvt = NoncurrentVersionTransition()
        assert nvt.noncurrentdays is None
        assert nvt.newernoncurrentversions is None
        assert nvt.storageclass is None

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {"NoncurrentDays": 30, "NewerNoncurrentVersions": 5, "StorageClass": "GLACIER"}
        nvt = NoncurrentVersionTransition.from_dict(data)
        assert nvt.noncurrentdays == 30
        assert nvt.newernoncurrentversions == 5
        assert nvt.storageclass == StorageClass.GLACIER

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {"noncurrentdays": 90, "newernoncurrentversions": 10, "storageclass": "STANDARD_IA"}
        nvt = NoncurrentVersionTransition.from_dict(data)
        assert nvt.noncurrentdays == 90
        assert nvt.newernoncurrentversions == 10
        assert nvt.storageclass == StorageClass.STANDARD_IA

    def test_from_dict_with_partial_data(self):
        """Test from_dict with partial data."""
        data = {"NoncurrentDays": 60, "StorageClass": "GLACIER_IR"}
        nvt = NoncurrentVersionTransition.from_dict(data)
        assert nvt.noncurrentdays == 60
        assert nvt.storageclass == StorageClass.GLACIER_IR
        assert nvt.newernoncurrentversions is None

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        nvt = NoncurrentVersionTransition.from_dict({})
        assert nvt.noncurrentdays is None
        assert nvt.newernoncurrentversions is None
        assert nvt.storageclass is None

    def test_describe_with_noncurrentdays(self):
        """Test describe method with noncurrent days."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass="GLACIER")
        result = nvt.describe()
        assert result["noncurrentdays"] == 30
        assert result["storageclass"] == "GLACIER"
        assert "newernoncurrentversions" not in result

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, newernoncurrentversions=5, storageclass="ONEZONE_IA")
        result = nvt.describe()
        assert result["noncurrentdays"] == 30
        assert result["newernoncurrentversions"] == 5
        assert result["storageclass"] == "ONEZONE_IA"

    def test_describe_with_no_storageclass(self):
        """Test describe method with no storage class."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30)
        result = nvt.describe()
        assert result == {"noncurrentdays": 30}

    def test_to_payload_with_noncurrentdays(self):
        """Test to_payload method with noncurrent days."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass="GLACIER")
        result = nvt.to_payload()
        assert result["NoncurrentDays"] == 30
        assert result["StorageClass"] == "GLACIER"

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        nvt = NoncurrentVersionTransition(
            noncurrentdays=30, newernoncurrentversions=5, storageclass="INTELLIGENT_TIERING"
        )
        result = nvt.to_payload()
        assert result["NoncurrentDays"] == 30
        assert result["NewerNoncurrentVersions"] == 5
        assert result["StorageClass"] == "INTELLIGENT_TIERING"

    def test_to_payload_with_no_fields(self):
        """Test to_payload method with no fields set."""
        nvt = NoncurrentVersionTransition()
        result = nvt.to_payload()
        assert result == {}

    def test_to_dict_with_noncurrentdays(self):
        """Test to_dict method with noncurrent days."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass="GLACIER")
        result = nvt.to_dict()
        assert result["noncurrentdays"] == 30
        assert result["storageclass"] == "GLACIER"
        assert result["newernoncurrentversions"] is None

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        nvt = NoncurrentVersionTransition(noncurrentdays=30, newernoncurrentversions=5, storageclass="DEEP_ARCHIVE")
        result = nvt.to_dict()
        assert result["noncurrentdays"] == 30
        assert result["newernoncurrentversions"] == 5
        assert result["storageclass"] == "DEEP_ARCHIVE"

    def test_all_storage_classes(self):
        """Test with all valid storage classes."""
        storage_classes = ["GLACIER", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING", "DEEP_ARCHIVE", "GLACIER_IR"]
        for sc in storage_classes:
            nvt = NoncurrentVersionTransition(noncurrentdays=30, storageclass=sc)
            assert nvt.storageclass.value == sc
