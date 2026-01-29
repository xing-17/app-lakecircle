"""Unit tests for AbortIncompleteMultipartUpload class."""

from __future__ import annotations

from app.model.lifecycle.abortincompletemultipartupload import AbortIncompleteMultipartUpload


class TestAbortIncompleteMultipartUpload:
    """Test AbortIncompleteMultipartUpload configuration class."""

    def test_init_with_daysafterinitiation(self):
        """Test initialization with days after initiation."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=7)
        assert aimu.daysafterinitiation == 7

    def test_init_with_daysafterinitiation_as_string(self):
        """Test initialization with days after initiation as string."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation="14")
        assert aimu.daysafterinitiation == 14
        assert isinstance(aimu.daysafterinitiation, int)

    def test_init_with_no_parameters(self):
        """Test initialization with no parameters."""
        aimu = AbortIncompleteMultipartUpload()
        assert aimu.daysafterinitiation is None

    def test_init_with_zero_days(self):
        """Test initialization with zero days."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=0)
        assert aimu.daysafterinitiation == 0

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {"DaysAfterInitiation": 7}
        aimu = AbortIncompleteMultipartUpload.from_dict(data)
        assert aimu.daysafterinitiation == 7

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {"daysafterinitiation": 14}
        aimu = AbortIncompleteMultipartUpload.from_dict(data)
        assert aimu.daysafterinitiation == 14

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        aimu = AbortIncompleteMultipartUpload.from_dict({})
        assert aimu.daysafterinitiation is None

    def test_describe_with_daysafterinitiation(self):
        """Test describe method with days after initiation."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=7)
        result = aimu.describe()
        assert result == {"daysafterinitiation": 7}

    def test_describe_with_no_fields(self):
        """Test describe method with no fields set."""
        aimu = AbortIncompleteMultipartUpload()
        result = aimu.describe()
        assert result == {}

    def test_describe_with_zero_days(self):
        """Test describe method with zero days."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=0)
        result = aimu.describe()
        assert result == {"daysafterinitiation": 0}

    def test_to_payload_with_daysafterinitiation(self):
        """Test to_payload method with days after initiation."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=7)
        result = aimu.to_payload()
        assert result == {"DaysAfterInitiation": 7}

    def test_to_payload_with_no_fields(self):
        """Test to_payload method with no fields set."""
        aimu = AbortIncompleteMultipartUpload()
        result = aimu.to_payload()
        assert result == {}

    def test_to_dict_with_daysafterinitiation(self):
        """Test to_dict method with days after initiation."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=7)
        result = aimu.to_dict()
        assert result == {"daysafterinitiation": 7}

    def test_to_dict_with_no_fields(self):
        """Test to_dict method with no fields set."""
        aimu = AbortIncompleteMultipartUpload()
        result = aimu.to_dict()
        assert result == {"daysafterinitiation": None}

    def test_typical_values(self):
        """Test with typical values (1, 7, 30 days)."""
        for days in [1, 7, 30]:
            aimu = AbortIncompleteMultipartUpload(daysafterinitiation=days)
            assert aimu.daysafterinitiation == days
            assert aimu.describe() == {"daysafterinitiation": days}
            assert aimu.to_payload() == {"DaysAfterInitiation": days}
