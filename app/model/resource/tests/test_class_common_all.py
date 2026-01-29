"""Unit tests for S3Component base class."""

from __future__ import annotations

from datetime import date, datetime

import boto3
from moto import mock_aws

from app.model.resource.common import S3Component


class TestS3Component:
    """Test S3Component base class."""

    @mock_aws
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        client = boto3.client("s3", region_name="us-west-2")
        component = S3Component(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert component.account == "123456789012"
        assert component.region == "us-west-2"
        assert component.client == client

    @mock_aws
    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        component = S3Component(
            account="123456789012",
            region="us-east-1",
        )
        assert component.account == "123456789012"
        assert component.region == "us-east-1"
        assert component.client is not None

    @mock_aws
    def test_resolve_account_from_parent(self):
        """Test that account is resolved from parent."""
        parent = S3Component(
            account="parent-account",
            region="us-west-2",
        )
        child = S3Component(
            account=None,
            region="us-west-2",
            parent=parent,
        )
        assert child.account == "parent-account"

    @mock_aws
    def test_resolve_region_from_parent(self):
        """Test that region is resolved from parent."""
        parent = S3Component(
            account="123456789012",
            region="parent-region",
        )
        child = S3Component(
            account="123456789012",
            region=None,
            parent=parent,
        )
        assert child.region == "parent-region"

    @mock_aws
    def test_resolve_client_from_parent(self):
        """Test that client is resolved from parent."""
        client = boto3.client("s3", region_name="us-west-2")
        parent = S3Component(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        child = S3Component(
            account="123456789012",
            region="us-west-2",
            parent=parent,
        )
        assert child.client == parent.client

    @mock_aws
    def test_resolve_client_creates_default(self):
        """Test that client is created if not provided."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        assert component.client is not None

    @mock_aws
    def test_resolve_date_with_date_object(self):
        """Test resolve_date with date object."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        test_date = date(2025, 1, 15)
        result = component.resolve_date(test_date)
        assert result == test_date
        assert isinstance(result, date)

    @mock_aws
    def test_resolve_date_with_datetime_object(self):
        """Test resolve_date with datetime object."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        test_datetime = datetime(2025, 1, 15, 10, 30, 0)
        result = component.resolve_date(test_datetime)
        assert result == test_datetime.date()
        assert isinstance(result, date)

    @mock_aws
    def test_resolve_date_with_string(self):
        """Test resolve_date with string."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        result = component.resolve_date("2025-01-15")
        assert result == date(2025, 1, 15)
        assert isinstance(result, date)

    @mock_aws
    def test_resolve_date_with_none(self):
        """Test resolve_date with None."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        result = component.resolve_date(None)
        assert result is None

    @mock_aws
    def test_describe_returns_dict(self):
        """Test that describe returns a dictionary."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        result = component.describe()
        assert isinstance(result, dict)
        assert "account" in result
        assert "region" in result
        assert result["account"] == "123456789012"
        assert result["region"] == "us-west-2"

    @mock_aws
    def test_to_dict_returns_dict(self):
        """Test that to_dict returns a dictionary."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        result = component.to_dict()
        assert isinstance(result, dict)
        assert "account" in result
        assert "region" in result

    @mock_aws
    def test_parent_child_hierarchy(self):
        """Test parent-child hierarchy."""
        parent = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        child = S3Component(
            account=None,
            region=None,
            parent=parent,
        )
        assert child.parent == parent
        assert child.account == parent.account
        assert child.region == parent.region

    @mock_aws
    def test_component_inherits_from_component(self):
        """Test that S3Component inherits from Component."""
        component = S3Component(
            account="123456789012",
            region="us-west-2",
        )
        # Check for Component methods
        assert hasattr(component, "describe")
        assert hasattr(component, "to_dict")

    @mock_aws
    def test_invalid_account_raises_error(self):
        """Test that invalid account raises ValueError."""
        try:
            S3Component(
                account=None,
                region="us-west-2",
            )
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "invalid" in str(e).lower()

    @mock_aws
    def test_invalid_region_raises_error(self):
        """Test that invalid region raises ValueError."""
        try:
            S3Component(
                account="123456789012",
                region=None,
            )
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "invalid" in str(e).lower()
