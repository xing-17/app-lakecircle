"""Unit tests for LifecycleRule class."""

from __future__ import annotations

from app.model.lifecycle.abortincompletemultipartupload import AbortIncompleteMultipartUpload
from app.model.lifecycle.expiration import Expiration
from app.model.lifecycle.filter import Filter
from app.model.lifecycle.lifecyclerule import LifecycleRule
from app.model.lifecycle.noncurrentversionexpiration import NoncurrentVersionExpiration
from app.model.lifecycle.noncurrentversiontransition import NoncurrentVersionTransition
from app.model.lifecycle.transition import Transition


class TestLifecycleRule:
    """Test LifecycleRule configuration class."""

    def test_init_with_minimal_parameters(self):
        """Test initialization with minimal parameters."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        assert rule.id == "test-rule"
        assert rule.status == "Enabled"
        assert rule.prefix is None
        assert rule.filter is None
        assert rule.expiration is None
        assert rule.transitions == []
        assert rule.noncurrent_transitions == []
        assert rule.noncurrent_expiration is None
        assert rule.abort_incomplete_multipart_upload is None

    def test_init_with_prefix(self):
        """Test initialization with prefix."""
        rule = LifecycleRule(id="test-rule", prefix="logs/", status="Enabled")
        assert rule.prefix == "logs/"

    def test_init_with_filter_object(self):
        """Test initialization with Filter object."""
        filt = Filter(prefix="data/")
        rule = LifecycleRule(id="test-rule", filter=filt, status="Enabled")
        assert rule.filter == filt
        assert rule.filter.prefix == "data/"

    def test_init_with_filter_dict(self):
        """Test initialization with filter dict."""
        rule = LifecycleRule(id="test-rule", filter={"prefix": "logs/"}, status="Enabled")
        assert isinstance(rule.filter, Filter)
        assert rule.filter.prefix == "logs/"

    def test_init_with_expiration_object(self):
        """Test initialization with Expiration object."""
        exp = Expiration(days=30)
        rule = LifecycleRule(id="test-rule", expiration=exp, status="Enabled")
        assert rule.expiration == exp
        assert rule.expiration.days == 30

    def test_init_with_expiration_dict(self):
        """Test initialization with expiration dict."""
        rule = LifecycleRule(id="test-rule", expiration={"days": 30}, status="Enabled")
        assert isinstance(rule.expiration, Expiration)
        assert rule.expiration.days == 30

    def test_init_with_transitions_list_of_objects(self):
        """Test initialization with transitions list of objects."""
        trans1 = Transition(days=30, storageclass="STANDARD_IA")
        trans2 = Transition(days=90, storageclass="GLACIER")
        rule = LifecycleRule(id="test-rule", transitions=[trans1, trans2], status="Enabled")
        assert len(rule.transitions) == 2
        assert rule.transitions[0].days == 30
        assert rule.transitions[1].days == 90

    def test_init_with_transitions_list_of_dicts(self):
        """Test initialization with transitions list of dicts."""
        rule = LifecycleRule(
            id="test-rule",
            transitions=[{"days": 30, "storageclass": "STANDARD_IA"}, {"days": 90, "storageclass": "GLACIER"}],
            status="Enabled",
        )
        assert len(rule.transitions) == 2
        assert all(isinstance(t, Transition) for t in rule.transitions)
        assert rule.transitions[0].days == 30
        assert rule.transitions[1].days == 90

    def test_init_with_noncurrent_transitions(self):
        """Test initialization with noncurrent version transitions."""
        rule = LifecycleRule(
            id="test-rule",
            noncurrent_transitions=[{"noncurrentdays": 30, "storageclass": "STANDARD_IA"}],
            status="Enabled",
        )
        assert len(rule.noncurrent_transitions) == 1
        assert isinstance(rule.noncurrent_transitions[0], NoncurrentVersionTransition)
        assert rule.noncurrent_transitions[0].noncurrentdays == 30

    def test_init_with_noncurrent_expiration_object(self):
        """Test initialization with NoncurrentVersionExpiration object."""
        nve = NoncurrentVersionExpiration(noncurrentdays=30)
        rule = LifecycleRule(id="test-rule", noncurrent_expiration=nve, status="Enabled")
        assert rule.noncurrent_expiration == nve
        assert rule.noncurrent_expiration.noncurrentdays == 30

    def test_init_with_noncurrent_expiration_dict(self):
        """Test initialization with noncurrent expiration dict."""
        rule = LifecycleRule(id="test-rule", noncurrent_expiration={"noncurrentdays": 30}, status="Enabled")
        assert isinstance(rule.noncurrent_expiration, NoncurrentVersionExpiration)
        assert rule.noncurrent_expiration.noncurrentdays == 30

    def test_init_with_abort_incomplete_multipart_upload_object(self):
        """Test initialization with AbortIncompleteMultipartUpload object."""
        aimu = AbortIncompleteMultipartUpload(daysafterinitiation=7)
        rule = LifecycleRule(id="test-rule", abort_incomplete_multipart_upload=aimu, status="Enabled")
        assert rule.abort_incomplete_multipart_upload == aimu
        assert rule.abort_incomplete_multipart_upload.daysafterinitiation == 7

    def test_init_with_abort_incomplete_multipart_upload_dict(self):
        """Test initialization with abort incomplete multipart upload dict."""
        rule = LifecycleRule(
            id="test-rule", abort_incomplete_multipart_upload={"daysafterinitiation": 7}, status="Enabled"
        )
        assert isinstance(rule.abort_incomplete_multipart_upload, AbortIncompleteMultipartUpload)
        assert rule.abort_incomplete_multipart_upload.daysafterinitiation == 7

    def test_init_with_disabled_status(self):
        """Test initialization with disabled status."""
        rule = LifecycleRule(id="test-rule", status="Disabled")
        assert rule.status == "Disabled"

    def test_from_dict_with_aws_format(self):
        """Test from_dict with AWS format (PascalCase)."""
        data = {
            "ID": "test-rule",
            "Status": "Enabled",
            "Prefix": "logs/",
            "Filter": {"Prefix": "data/"},
            "Expiration": {"Days": 30},
            "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}],
            "NoncurrentVersionTransitions": [{"NoncurrentDays": 30, "StorageClass": "GLACIER"}],
            "NoncurrentVersionExpiration": {"NoncurrentDays": 90},
            "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 7},
        }
        rule = LifecycleRule.from_dict(data)
        assert rule.id == "test-rule"
        assert rule.status == "Enabled"
        assert rule.prefix == "logs/"
        assert isinstance(rule.filter, Filter)
        assert isinstance(rule.expiration, Expiration)
        assert len(rule.transitions) == 1
        assert len(rule.noncurrent_transitions) == 1
        assert isinstance(rule.noncurrent_expiration, NoncurrentVersionExpiration)
        assert isinstance(rule.abort_incomplete_multipart_upload, AbortIncompleteMultipartUpload)

    def test_from_dict_with_lowercase_format(self):
        """Test from_dict with lowercase format."""
        data = {
            "id": "test-rule",
            "status": "Enabled",
            "prefix": "logs/",
            "filter": {"prefix": "data/"},
            "expiration": {"days": 30},
            "transitions": [{"days": 30, "storageclass": "GLACIER"}],
            "noncurrent_transitions": [{"noncurrentdays": 30, "storageclass": "GLACIER"}],
            "noncurrent_expiration": {"noncurrentdays": 90},
            "abort_incomplete_multipart_upload": {"daysafterinitiation": 7},
        }
        rule = LifecycleRule.from_dict(data)
        assert rule.id == "test-rule"
        assert rule.status == "Enabled"
        assert rule.prefix == "logs/"
        assert isinstance(rule.filter, Filter)
        assert isinstance(rule.expiration, Expiration)
        assert len(rule.transitions) == 1
        assert len(rule.noncurrent_transitions) == 1
        assert isinstance(rule.noncurrent_expiration, NoncurrentVersionExpiration)
        assert isinstance(rule.abort_incomplete_multipart_upload, AbortIncompleteMultipartUpload)

    def test_from_dict_with_minimal_data(self):
        """Test from_dict with minimal data."""
        data = {"ID": "test-rule", "Status": "Enabled"}
        rule = LifecycleRule.from_dict(data)
        assert rule.id == "test-rule"
        assert rule.status == "Enabled"
        assert rule.prefix is None
        assert rule.filter is None
        assert rule.expiration is None
        assert rule.transitions == []

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dict."""
        rule = LifecycleRule.from_dict({})
        assert rule.status is None
        assert rule.prefix is None
        assert rule.filter is None

    def test_describe_with_minimal_fields(self):
        """Test describe method with minimal fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        result = rule.describe()
        assert result["status"] == "Enabled"
        assert "prefix" not in result
        assert "filter" not in result

    def test_describe_with_all_fields(self):
        """Test describe method with all fields."""
        rule = LifecycleRule(
            id="test-rule",
            prefix="logs/",
            filter={"prefix": "data/"},
            status="Enabled",
            expiration={"days": 30},
            transitions=[{"days": 30, "storageclass": "GLACIER"}],
            noncurrent_transitions=[{"noncurrentdays": 30, "storageclass": "GLACIER"}],
            noncurrent_expiration={"noncurrentdays": 90},
            abort_incomplete_multipart_upload={"daysafterinitiation": 7},
        )
        result = rule.describe()
        assert result["prefix"] == "logs/"
        assert "filter" in result
        assert result["status"] == "Enabled"
        assert "expiration" in result
        assert len(result["transitions"]) == 1
        assert len(result["noncurrent_transitions"]) == 1
        assert "noncurrent_expiration" in result
        assert "abort_incomplete_multipart_upload" in result

    def test_to_payload_with_minimal_fields(self):
        """Test to_payload method with minimal fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        result = rule.to_payload()
        assert result["ID"] == "test-rule"
        assert result["Status"] == "Enabled"
        assert "Filter" not in result

    def test_to_payload_with_all_fields(self):
        """Test to_payload method with all fields."""
        rule = LifecycleRule(
            id="test-rule",
            prefix="logs/",
            filter={"prefix": "data/"},
            status="Enabled",
            expiration={"days": 30},
            transitions=[{"days": 30, "storageclass": "GLACIER"}],
            noncurrent_transitions=[{"noncurrentdays": 30, "storageclass": "GLACIER"}],
            noncurrent_expiration={"noncurrentdays": 90},
            abort_incomplete_multipart_upload={"daysafterinitiation": 7},
        )
        result = rule.to_payload()
        assert result["ID"] == "test-rule"
        assert "Prefix" in result
        assert "Filter" in result
        assert result["Status"] == "Enabled"
        assert "Expiration" in result
        assert len(result["Transitions"]) == 1
        assert len(result["NoncurrentVersionTransitions"]) == 1
        assert "NoncurrentVersionExpiration" in result
        assert "AbortIncompleteMultipartUpload" in result

    def test_to_dict_with_minimal_fields(self):
        """Test to_dict method with minimal fields."""
        rule = LifecycleRule(id="test-rule", status="Enabled")
        result = rule.to_dict()
        assert result["id"] == "test-rule"
        assert result["status"] == "Enabled"

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        rule = LifecycleRule(
            id="test-rule",
            prefix="logs/",
            filter={"prefix": "data/"},
            status="Enabled",
            expiration={"days": 30},
            transitions=[{"days": 30, "storageclass": "GLACIER"}],
            noncurrent_transitions=[{"noncurrentdays": 30, "storageclass": "GLACIER"}],
            noncurrent_expiration={"noncurrentdays": 90},
            abort_incomplete_multipart_upload={"daysafterinitiation": 7},
        )
        result = rule.to_dict()
        assert result["id"] == "test-rule"
        assert result["prefix"] == "logs/"
        assert "filter" in result
        assert result["status"] == "Enabled"
        assert "expiration" in result
        assert len(result["transitions"]) == 1
        assert len(result["noncurrent_transitions"]) == 1
        assert "noncurrent_expiration" in result
        assert "abort_incomplete_multipart_upload" in result

    def test_resolve_transitions_with_none(self):
        """Test _resolve_transitions with None."""
        rule = LifecycleRule(id="test-rule", transitions=None, status="Enabled")
        assert rule.transitions == []

    def test_resolve_noncurrent_transitions_with_none(self):
        """Test _resolve_noncurrent_transitions with None."""
        rule = LifecycleRule(id="test-rule", noncurrent_transitions=None, status="Enabled")
        assert rule.noncurrent_transitions == []

    def test_resolve_expiration_with_none(self):
        """Test _resolve_expiration with None."""
        rule = LifecycleRule(id="test-rule", expiration=None, status="Enabled")
        assert rule.expiration is None

    def test_resolve_filter_with_none(self):
        """Test _resolve_filter with None."""
        rule = LifecycleRule(id="test-rule", filter=None, status="Enabled")
        assert rule.filter is None

    def test_complex_rule_with_multiple_transitions(self):
        """Test complex rule with multiple transitions."""
        rule = LifecycleRule(
            id="complex-rule",
            prefix="archives/",
            status="Enabled",
            transitions=[
                {"days": 30, "storageclass": "STANDARD_IA"},
                {"days": 90, "storageclass": "GLACIER"},
                {"days": 365, "storageclass": "DEEP_ARCHIVE"},
            ],
            expiration={"days": 730},
        )
        assert len(rule.transitions) == 3
        assert rule.transitions[0].storageclass.value == "STANDARD_IA"
        assert rule.transitions[1].storageclass.value == "GLACIER"
        assert rule.transitions[2].storageclass.value == "DEEP_ARCHIVE"
        assert rule.expiration.days == 730
