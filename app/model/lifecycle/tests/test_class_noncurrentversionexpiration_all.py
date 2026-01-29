"""Unit tests for NoncurrentVersionExpiration class."""

from __future__ import annotations

from app.model.lifecycle.noncurrentversionexpiration import NoncurrentVersionExpiration


class TestNoncurrentVersionExpiration:
    """Test NoncurrentVersionExpiration configuration class."""

    def test_init_with_noncurrentdays(self):
        """Test initialization with noncurrent days."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30)
        assert nve.noncurrentdays == 30
        assert nve.newernoncurrentversions is None

    def test_init_with_newernoncurrentversions(self):
        """Test initialization with newer noncurrent versions."""
        nve = NoncurrentVersionExpiration(newernoncurrentversions=5)
        assert nve.newernoncurrentversions == 5
        assert nve.noncurrentdays is None

    def test_init_with_both_parameters(self):
        """Test initialization with both parameters."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30, newernoncurrentversions=3)
        assert nve.noncurrentdays == 30
        assert nve.newernoncurrentversions == 3

    def test_init_with_string_values(self):
        """Test initialization with string values."""
        nve = NoncurrentVersionExpiration(noncurrentdays="30", newernoncurrentversions="5")
        assert nve.noncurrentdays == 30
        assert nve.newernoncurrentversions == 5
        assert isinstance(nve.noncurrentdays, int)
        assert isinstance(nve.newernoncurrentversions, int)

    def test_init_with_no_parameters(self):
        """Test initialization with no parameters."""
        nve = NoncurrentVersionExpiration()
        assert nve.noncurrentdays is None
        assert nve.newernoncurrentversions is None

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {"NoncurrentDays": 30, "NewerNoncurrentVersions": 5}
        nve = NoncurrentVersionExpiration.from_dict(data)
        assert nve.noncurrentdays == 30
        assert nve.newernoncurrentversions == 5

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {"noncurrentdays": 90, "newernoncurrentversions": 10}
        nve = NoncurrentVersionExpiration.from_dict(data)
        assert nve.noncurrentdays == 90
        assert nve.newernoncurrentversions == 10

    def test_from_dict_with_partial_data(self):
        """Test from_dict with partial data."""
        data = {"NoncurrentDays": 60}
        nve = NoncurrentVersionExpiration.from_dict(data)
        assert nve.noncurrentdays == 60
        assert nve.newernoncurrentversions is None

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        nve = NoncurrentVersionExpiration.from_dict({})
        assert nve.noncurrentdays is None
        assert nve.newernoncurrentversions is None

    def test_describe_with_noncurrentdays(self):
        """Test describe method with noncurrent days."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30)
        result = nve.describe()
        assert result == {"noncurrentdays": 30}

    def test_describe_with_newernoncurrentversions(self):
        """Test describe method with newer noncurrent versions."""
        nve = NoncurrentVersionExpiration(newernoncurrentversions=5)
        result = nve.describe()
        assert result == {"newernoncurrentversions": 5}

    def test_describe_with_both_fields(self):
        """Test describe method with both fields."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30, newernoncurrentversions=3)
        result = nve.describe()
        assert result["noncurrentdays"] == 30
        assert result["newernoncurrentversions"] == 3

    def test_describe_with_no_fields(self):
        """Test describe method with no fields set."""
        nve = NoncurrentVersionExpiration()
        result = nve.describe()
        assert result == {}

    def test_to_payload_with_noncurrentdays(self):
        """Test to_payload method with noncurrent days."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30)
        result = nve.to_payload()
        assert result == {"NoncurrentDays": 30}

    def test_to_payload_with_newernoncurrentversions(self):
        """Test to_payload method with newer noncurrent versions."""
        nve = NoncurrentVersionExpiration(newernoncurrentversions=5)
        result = nve.to_payload()
        assert result == {"NewerNoncurrentVersions": 5}

    def test_to_payload_with_both_fields(self):
        """Test to_payload method with both fields."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30, newernoncurrentversions=3)
        result = nve.to_payload()
        assert result["NoncurrentDays"] == 30
        assert result["NewerNoncurrentVersions"] == 3

    def test_to_payload_with_no_fields(self):
        """Test to_payload method with no fields set."""
        nve = NoncurrentVersionExpiration()
        result = nve.to_payload()
        assert result == {}

    def test_to_dict_with_noncurrentdays(self):
        """Test to_dict method with noncurrent days."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30)
        result = nve.to_dict()
        assert result["noncurrentdays"] == 30
        assert result["newernoncurrentversions"] is None

    def test_to_dict_with_both_fields(self):
        """Test to_dict method with both fields."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30, newernoncurrentversions=5)
        result = nve.to_dict()
        assert result["noncurrentdays"] == 30
        assert result["newernoncurrentversions"] == 5

    def test_zero_values(self):
        """Test with zero values."""
        nve = NoncurrentVersionExpiration(noncurrentdays=0, newernoncurrentversions=0)
        assert nve.noncurrentdays == 0
        assert nve.newernoncurrentversions == 0
