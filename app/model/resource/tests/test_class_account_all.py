"""Unit tests for Account class."""

from __future__ import annotations

import boto3
from moto import mock_aws

from app.model.resource.account import Account
from app.model.resource.bucket import Bucket


class TestAccount:
    """Test Account configuration class."""

    @mock_aws
    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        client = boto3.client("s3", region_name="us-west-2")
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert account.account == "123456789012"
        assert account.region == "us-west-2"
        assert account.client == client
        assert isinstance(account.buckets, dict)
        assert len(account.buckets) == 0

    @mock_aws
    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        account = Account(
            account="123456789012",
            region="us-east-1",
        )
        assert account.account == "123456789012"
        assert account.region == "us-east-1"
        assert isinstance(account.buckets, dict)

    @mock_aws
    def test_list_buckets_empty(self):
        """Test list_buckets with no buckets."""
        client = boto3.client("s3", region_name="us-west-2")
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        buckets = account.list_buckets()
        assert isinstance(buckets, list)
        assert len(buckets) == 0

    @mock_aws
    def test_list_buckets_with_buckets(self):
        """Test list_buckets with existing buckets."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="bucket-1",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        client.create_bucket(
            Bucket="bucket-2",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        buckets = account.list_buckets()
        assert isinstance(buckets, list)
        assert len(buckets) == 2
        bucket_names = [b.name for b in buckets]
        assert "bucket-1" in bucket_names
        assert "bucket-2" in bucket_names

    @mock_aws
    def test_list_buckets_returns_bucket_objects(self):
        """Test that list_buckets returns Bucket objects."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        buckets = account.list_buckets()
        assert all(isinstance(b, Bucket) for b in buckets)

    @mock_aws
    def test_load_populates_buckets_dict(self):
        """Test that load() populates the buckets dictionary."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="bucket-1",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        client.create_bucket(
            Bucket="bucket-2",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        account.load()
        
        assert len(account.buckets) == 2
        assert "bucket-1" in account.buckets
        assert "bucket-2" in account.buckets
        assert isinstance(account.buckets["bucket-1"], Bucket)

    @mock_aws
    def test_list_bucketnames(self):
        """Test list_bucketnames returns list of bucket names."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="bucket-a",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        client.create_bucket(
            Bucket="bucket-b",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        account.load()
        
        bucket_names = account.list_bucketnames()
        assert isinstance(bucket_names, list)
        assert len(bucket_names) == 2
        assert "bucket-a" in bucket_names
        assert "bucket-b" in bucket_names

    @mock_aws
    def test_describe_returns_dict(self):
        """Test that describe returns a dictionary."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        account.load()
        
        result = account.describe()
        assert isinstance(result, dict)
        assert "account" in result
        assert "region" in result
        assert "buckets_count" in result
        assert "bucket_names" in result
        assert result["account"] == "123456789012"
        assert result["region"] == "us-west-2"
        assert result["buckets_count"] == 1
        assert "test-bucket" in result["bucket_names"]

    @mock_aws
    def test_to_dict_returns_serializable_dict(self):
        """Test that to_dict returns a serializable dictionary."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        account.load()
        
        result = account.to_dict()
        assert isinstance(result, dict)
        assert "account" in result
        assert "region" in result
        assert "buckets" in result
        assert result["account"] == "123456789012"
        assert result["region"] == "us-west-2"
        assert isinstance(result["buckets"], list)
        assert len(result["buckets"]) == 1

    @mock_aws
    def test_account_inherits_from_s3component(self):
        """Test that Account inherits from S3Component."""
        client = boto3.client("s3", region_name="us-west-2")
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        assert hasattr(account, "describe")
        assert hasattr(account, "to_dict")
        assert hasattr(account, "resolve_date")

    @mock_aws
    def test_empty_buckets_dict_on_init(self):
        """Test that buckets dict is empty on initialization."""
        account = Account(
            account="123456789012",
            region="us-west-2",
        )
        assert account.buckets == {}
        assert len(account.buckets) == 0

    @mock_aws
    def test_list_buckets_filters_none_names(self):
        """Test that list_buckets handles buckets without names."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="valid-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        buckets = account.list_buckets()
        
        # All returned buckets should have names
        assert all(bucket.name for bucket in buckets)

    @mock_aws
    def test_bucket_inherits_account_and_region(self):
        """Test that buckets created by Account inherit account and region."""
        client = boto3.client("s3", region_name="us-west-2")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )
        
        account = Account(
            account="123456789012",
            region="us-west-2",
            client=client,
        )
        buckets = account.list_buckets()
        
        bucket = buckets[0]
        assert bucket.account == "123456789012"
        assert bucket.region == "us-west-2"
        assert bucket.parent == account

    @mock_aws
    def test_multiple_accounts_different_regions(self):
        """Test creating multiple Account objects with different regions."""
        client1 = boto3.client("s3", region_name="us-west-2")
        client2 = boto3.client("s3", region_name="us-east-1")
        
        account1 = Account(account="111111111111", region="us-west-2", client=client1)
        account2 = Account(account="222222222222", region="us-east-1", client=client2)
        
        assert account1.account != account2.account
        assert account1.region != account2.region
