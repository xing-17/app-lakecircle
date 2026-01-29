"""Unit tests for Expiration class."""

from __future__ import annotations

from datetime import date

from app.model.lifecycle.expiration import Expiration


class TestExpiration:
    """Test Expiration configuration class."""

    def test_init_with_days(self):
        """Test initialization with days."""
        exp = Expiration(days=30)
        assert exp.days == 30
        assert exp.date is None
        assert exp.expired_object_delete_marker is None

    def test_init_with_date(self):
        """Test initialization with date."""
        test_date = date(2026, 12, 31)
        exp = Expiration(date=test_date)
        assert exp.date == test_date
        assert exp.days is None

    def test_init_with_date_string(self):
        """Test initialization with date string."""
        exp = Expiration(date="2026-12-31")
        assert exp.date == date(2026, 12, 31)
        assert exp.days is None

    def test_init_with_expired_object_delete_marker(self):
        """Test initialization with expired_object_delete_marker."""
        exp = Expiration(expired_object_delete_marker=True)
        assert exp.expired_object_delete_marker is True
        assert exp.days is None
        assert exp.date is None

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        exp = Expiration(date="2026-12-31", days=30, expired_object_delete_marker=True)
        assert exp.date == date(2026, 12, 31)
        assert exp.days == 30
        assert exp.expired_object_delete_marker is True

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {"Date": "2026-12-31", "Days": 30, "ExpiredObjectDeleteMarker": True}
        exp = Expiration.from_dict(data)
        assert exp.date == date(2026, 12, 31)
        assert exp.days == 30
        assert exp.expired_object_delete_marker is True

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {"date": "2026-12-31", "days": 30, "expiredobjectdeletemarker": False}
        exp = Expiration.from_dict(data)
        assert exp.date == date(2026, 12, 31)
        assert exp.days == 30
        assert exp.expired_object_delete_marker is False

    def test_from_dict_with_partial_data(self):
        """Test from_dict with partial data."""
        data = {"Days": 90}
        exp = Expiration.from_dict(data)
        assert exp.days == 90
        assert exp.date is None
        assert exp.expired_object_delete_marker is None

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        exp = Expiration.from_dict({})
        assert exp.date is None
        assert exp.days is None
        assert exp.expired_object_delete_marker is None

    def test_describe_with_days(self):
        """Test describe method with days."""
        exp = Expiration(days=30)
        result = exp.describe()
        assert result == {"days": 30}

    def test_describe_with_date(self):
        """Test describe method with date."""
        exp = Expiration(date="2026-12-31")
        result = exp.describe()
        assert result == {"date": "2026-12-31"}

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        exp = Expiration(date="2026-12-31", days=30, expired_object_delete_marker=True)
        result = exp.describe()
        assert result["date"] == "2026-12-31"
        assert result["days"] == 30
        assert result["expired_object_delete_marker"] is True

    def test_describe_with_no_fields(self):
        """Test describe method with no fields set."""
        exp = Expiration()
        result = exp.describe()
        assert result == {}

    def test_to_payload_with_days(self):
        """Test to_payload method with days."""
        exp = Expiration(days=30)
        result = exp.to_payload()
        assert result == {"Days": 30}

    def test_to_payload_with_date(self):
        """Test to_payload method with date."""
        test_date = date(2026, 12, 31)
        exp = Expiration(date=test_date)
        result = exp.to_payload()
        assert result == {"Date": test_date}

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        test_date = date(2026, 12, 31)
        exp = Expiration(date=test_date, days=30, expired_object_delete_marker=True)
        result = exp.to_payload()
        assert result["Date"] == test_date
        assert result["Days"] == 30
        assert result["ExpiredObjectDeleteMarker"] is True

    def test_to_dict_with_days(self):
        """Test to_dict method with days."""
        exp = Expiration(days=30)
        result = exp.to_dict()
        assert result["days"] == 30
        assert result["date"] is None
        assert result["expired_object_delete_marker"] is None

    def test_to_dict_with_date(self):
        """Test to_dict method with date."""
        exp = Expiration(date="2026-12-31")
        result = exp.to_dict()
        assert result["date"] == "2026-12-31"
        assert result["days"] is None

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        exp = Expiration(date="2026-12-31", days=30, expired_object_delete_marker=False)
        result = exp.to_dict()
        assert result["date"] == "2026-12-31"
        assert result["days"] == 30
        assert result["expired_object_delete_marker"] is False

    def test_days_as_string(self):
        """Test initialization with days as string."""
        exp = Expiration(days="30")
        assert exp.days == 30
        assert isinstance(exp.days, int)
