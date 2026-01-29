"""Unit tests for Filter class."""

from __future__ import annotations

from app.model.lifecycle.filter import Filter


class TestFilter:
    """Test Filter configuration class."""

    def test_init_with_prefix(self):
        """Test initialization with prefix."""
        filt = Filter(prefix="logs/")
        assert filt.prefix == "logs/"
        assert filt.tag_key is None
        assert filt.tag_value is None
        assert filt.object_size_greater_than is None
        assert filt.object_size_less_than is None

    def test_init_with_tag(self):
        """Test initialization with tag."""
        filt = Filter(tag_key="Environment", tag_value="Production")
        assert filt.tag_key == "Environment"
        assert filt.tag_value == "Production"
        assert filt.prefix is None

    def test_init_with_object_size_greater_than(self):
        """Test initialization with object size greater than."""
        filt = Filter(object_size_greater_than=1024)
        assert filt.object_size_greater_than == 1024
        assert filt.object_size_less_than is None

    def test_init_with_object_size_less_than(self):
        """Test initialization with object size less than."""
        filt = Filter(object_size_less_than=10485760)
        assert filt.object_size_less_than == 10485760
        assert filt.object_size_greater_than is None

    def test_init_with_size_range(self):
        """Test initialization with size range."""
        filt = Filter(object_size_greater_than=1024, object_size_less_than=10485760)
        assert filt.object_size_greater_than == 1024
        assert filt.object_size_less_than == 10485760

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        filt = Filter(
            prefix="data/",
            tag_key="Type",
            tag_value="Archive",
            object_size_greater_than=1024,
            object_size_less_than=10485760,
        )
        assert filt.prefix == "data/"
        assert filt.tag_key == "Type"
        assert filt.tag_value == "Archive"
        assert filt.object_size_greater_than == 1024
        assert filt.object_size_less_than == 10485760

    def test_init_with_no_parameters(self):
        """Test initialization with no parameters."""
        filt = Filter()
        assert filt.prefix is None
        assert filt.tag_key is None
        assert filt.tag_value is None
        assert filt.object_size_greater_than is None
        assert filt.object_size_less_than is None

    def test_from_dict_with_aws_format_prefix(self):
        """Test from_dict with AWS format prefix."""
        data = {"Prefix": "logs/"}
        filt = Filter.from_dict(data)
        assert filt.prefix == "logs/"

    def test_from_dict_with_aws_format_tag(self):
        """Test from_dict with AWS format tag."""
        data = {"Tag": {"Key": "Environment", "Value": "Production"}}
        filt = Filter.from_dict(data)
        assert filt.tag_key == "Environment"
        assert filt.tag_value == "Production"

    def test_from_dict_with_aws_format_object_sizes(self):
        """Test from_dict with AWS format object sizes."""
        data = {"ObjectSizeGreaterThan": 1024, "ObjectSizeLessThan": 10485760}
        filt = Filter.from_dict(data)
        assert filt.object_size_greater_than == 1024
        assert filt.object_size_less_than == 10485760

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {
            "prefix": "data/",
            "tag": {"key": "Type", "value": "Archive"},
            "object_size_greater_than": 2048,
            "object_size_less_than": 5242880,
        }
        filt = Filter.from_dict(data)
        assert filt.prefix == "data/"
        assert filt.tag_key == "Type"
        assert filt.tag_value == "Archive"
        assert filt.object_size_greater_than == 2048
        assert filt.object_size_less_than == 5242880

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        filt = Filter.from_dict({})
        assert filt.prefix is None
        assert filt.tag_key is None
        assert filt.tag_value is None

    def test_describe_with_prefix(self):
        """Test describe method with prefix."""
        filt = Filter(prefix="logs/")
        result = filt.describe()
        assert result == {"prefix": "logs/"}

    def test_describe_with_tag(self):
        """Test describe method with tag."""
        filt = Filter(tag_key="Environment", tag_value="Production")
        result = filt.describe()
        assert result == {"tag": {"key": "Environment", "value": "Production"}}

    def test_describe_with_object_sizes(self):
        """Test describe method with object sizes."""
        filt = Filter(object_size_greater_than=1024, object_size_less_than=10485760)
        result = filt.describe()
        assert result["object_size_greater_than"] == 1024
        assert result["object_size_less_than"] == 10485760

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        filt = Filter(
            prefix="data/",
            tag_key="Type",
            tag_value="Archive",
            object_size_greater_than=1024,
            object_size_less_than=10485760,
        )
        result = filt.describe()
        assert result["prefix"] == "data/"
        assert result["tag"]["key"] == "Type"
        assert result["tag"]["value"] == "Archive"
        assert result["object_size_greater_than"] == 1024
        assert result["object_size_less_than"] == 10485760

    def test_describe_with_no_tag_returns_no_tag(self):
        """Test describe method returns no tag if keys are None."""
        filt = Filter(prefix="logs/")
        result = filt.describe()
        assert "tag" not in result

    def test_to_payload_with_prefix(self):
        """Test to_payload method with prefix."""
        filt = Filter(prefix="logs/")
        result = filt.to_payload()
        assert result == {"Prefix": "logs/"}

    def test_to_payload_with_tag(self):
        """Test to_payload method with tag."""
        filt = Filter(tag_key="Environment", tag_value="Production")
        result = filt.to_payload()
        assert result == {"Tag": {"Key": "Environment", "Value": "Production"}}

    def test_to_payload_with_object_sizes(self):
        """Test to_payload method with object sizes."""
        filt = Filter(object_size_greater_than=1024, object_size_less_than=10485760)
        result = filt.to_payload()
        assert result["ObjectSizeGreaterThan"] == 1024
        assert result["ObjectSizeLessThan"] == 10485760

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        filt = Filter(
            prefix="data/",
            tag_key="Type",
            tag_value="Archive",
            object_size_greater_than=1024,
            object_size_less_than=10485760,
        )
        result = filt.to_payload()
        assert result["Prefix"] == "data/"
        assert result["Tag"]["Key"] == "Type"
        assert result["Tag"]["Value"] == "Archive"
        assert result["ObjectSizeGreaterThan"] == 1024
        assert result["ObjectSizeLessThan"] == 10485760

    def test_to_dict_with_prefix(self):
        """Test to_dict method with prefix."""
        filt = Filter(prefix="logs/")
        result = filt.to_dict()
        assert result["prefix"] == "logs/"
        assert result["tag"]["key"] is None
        assert result["tag"]["value"] is None

    def test_to_dict_with_tag(self):
        """Test to_dict method with tag."""
        filt = Filter(tag_key="Environment", tag_value="Production")
        result = filt.to_dict()
        assert result["tag"]["key"] == "Environment"
        assert result["tag"]["value"] == "Production"

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        filt = Filter(
            prefix="data/",
            tag_key="Type",
            tag_value="Archive",
            object_size_greater_than=1024,
            object_size_less_than=10485760,
        )
        result = filt.to_dict()
        assert result["prefix"] == "data/"
        assert result["tag"]["key"] == "Type"
        assert result["tag"]["value"] == "Archive"
        assert result["object_size_greater_than"] == 1024
        assert result["object_size_less_than"] == 10485760

    def test_empty_prefix(self):
        """Test with empty prefix string."""
        filt = Filter(prefix="")
        # Empty string is falsy, so it won't be included in describe
        result = filt.describe()
        assert result == {}
