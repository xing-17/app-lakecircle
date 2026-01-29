"""Unit tests for Transition class."""

from __future__ import annotations

from datetime import date

from app.model.lifecycle.storageclass import StorageClass
from app.model.lifecycle.transition import Transition


class TestTransition:
    """Test Transition configuration class."""

    def test_init_with_days_and_storageclass(self):
        """Test initialization with days and storage class."""
        trans = Transition(days=30, storageclass="GLACIER")
        assert trans.days == 30
        assert trans.storageclass == StorageClass.GLACIER
        assert trans.date is None

    def test_init_with_date_and_storageclass(self):
        """Test initialization with date and storage class."""
        test_date = date(2026, 12, 31)
        trans = Transition(date=test_date, storageclass="STANDARD_IA")
        assert trans.date == test_date
        assert trans.storageclass == StorageClass.STANDARD_IA
        assert trans.days is None

    def test_init_with_date_string(self):
        """Test initialization with date string."""
        trans = Transition(date="2026-12-31", storageclass="DEEP_ARCHIVE")
        assert trans.date == date(2026, 12, 31)
        assert trans.storageclass == StorageClass.DEEP_ARCHIVE

    def test_init_with_storageclass_enum(self):
        """Test initialization with StorageClass enum."""
        trans = Transition(days=90, storageclass=StorageClass.GLACIER_IR)
        assert trans.storageclass == StorageClass.GLACIER_IR

    def test_init_with_days_as_string(self):
        """Test initialization with days as string."""
        trans = Transition(days="30", storageclass="GLACIER")
        assert trans.days == 30
        assert isinstance(trans.days, int)

    def test_init_with_no_parameters(self):
        """Test initialization with no parameters."""
        trans = Transition()
        assert trans.date is None
        assert trans.days is None
        assert trans.storageclass is None

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {"Date": "2026-12-31", "Days": 30, "StorageClass": "GLACIER"}
        trans = Transition.from_dict(data)
        assert trans.date == date(2026, 12, 31)
        assert trans.days == 30
        assert trans.storageclass == StorageClass.GLACIER

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {"date": "2026-12-31", "days": 90, "storageclass": "STANDARD_IA"}
        trans = Transition.from_dict(data)
        assert trans.date == date(2026, 12, 31)
        assert trans.days == 90
        assert trans.storageclass == StorageClass.STANDARD_IA

    def test_from_dict_with_partial_data(self):
        """Test from_dict with partial data."""
        data = {"Days": 180, "StorageClass": "DEEP_ARCHIVE"}
        trans = Transition.from_dict(data)
        assert trans.days == 180
        assert trans.storageclass == StorageClass.DEEP_ARCHIVE
        assert trans.date is None

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        trans = Transition.from_dict({})
        assert trans.date is None
        assert trans.days is None
        assert trans.storageclass is None

    def test_describe_with_days(self):
        """Test describe method with days."""
        trans = Transition(days=30, storageclass="GLACIER")
        result = trans.describe()
        assert result["days"] == 30
        assert result["storageclass"] == "GLACIER"
        assert "date" not in result

    def test_describe_with_date(self):
        """Test describe method with date."""
        trans = Transition(date="2026-12-31", storageclass="STANDARD_IA")
        result = trans.describe()
        assert result["date"] == "2026-12-31"
        assert result["storageclass"] == "STANDARD_IA"
        assert "days" not in result

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        trans = Transition(date="2026-12-31", days=30, storageclass="GLACIER_IR")
        result = trans.describe()
        assert result["date"] == "2026-12-31"
        assert result["days"] == 30
        assert result["storageclass"] == "GLACIER_IR"

    def test_describe_with_no_storageclass(self):
        """Test describe method with no storage class."""
        trans = Transition(days=30)
        result = trans.describe()
        assert result == {"days": 30}

    def test_to_payload_with_days(self):
        """Test to_payload method with days."""
        trans = Transition(days=30, storageclass="GLACIER")
        result = trans.to_payload()
        assert result["Days"] == 30
        assert result["StorageClass"] == "GLACIER"

    def test_to_payload_with_date(self):
        """Test to_payload method with date."""
        test_date = date(2026, 12, 31)
        trans = Transition(date=test_date, storageclass="ONEZONE_IA")
        result = trans.to_payload()
        assert result["Date"] == test_date
        assert result["StorageClass"] == "ONEZONE_IA"

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        test_date = date(2026, 12, 31)
        trans = Transition(date=test_date, days=60, storageclass="INTELLIGENT_TIERING")
        result = trans.to_payload()
        assert result["Date"] == test_date
        assert result["Days"] == 60
        assert result["StorageClass"] == "INTELLIGENT_TIERING"

    def test_to_dict_with_days(self):
        """Test to_dict method with days."""
        trans = Transition(days=30, storageclass="GLACIER")
        result = trans.to_dict()
        assert result["days"] == 30
        assert result["storageclass"] == "GLACIER"
        assert result["date"] is None

    def test_to_dict_with_date(self):
        """Test to_dict method with date."""
        trans = Transition(date="2026-12-31", storageclass="STANDARD_IA")
        result = trans.to_dict()
        assert result["date"] == "2026-12-31"
        assert result["storageclass"] == "STANDARD_IA"
        assert result["days"] is None

    def test_all_storage_classes(self):
        """Test with all valid storage classes."""
        storage_classes = ["GLACIER", "STANDARD_IA", "ONEZONE_IA", "INTELLIGENT_TIERING", "DEEP_ARCHIVE", "GLACIER_IR"]
        for sc in storage_classes:
            trans = Transition(days=30, storageclass=sc)
            assert trans.storageclass.value == sc
