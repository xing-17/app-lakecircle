"""Unit tests for StorageClass class."""

from __future__ import annotations

from app.model.lifecycle.storageclass import StorageClass


class TestStorageClass:
    """Test StorageClass enumeration."""

    def test_from_str_case_insensitive(self):
        """Test case-insensitive string conversion."""
        assert StorageClass.from_str("glacier") == StorageClass.GLACIER
        assert StorageClass.from_str("GLACIER") == StorageClass.GLACIER
        assert StorageClass.from_str("Glacier") == StorageClass.GLACIER

    def test_from_str_all_valid_classes(self):
        """Test all valid storage classes."""
        assert StorageClass.from_str("STANDARD") == StorageClass.STANDARD
        assert StorageClass.from_str("GLACIER") == StorageClass.GLACIER
        assert StorageClass.from_str("STANDARD_IA") == StorageClass.STANDARD_IA
        assert StorageClass.from_str("ONEZONE_IA") == StorageClass.ONEZONE_IA
        assert StorageClass.from_str("INTELLIGENT_TIERING") == StorageClass.INTELLIGENT_TIERING
        assert StorageClass.from_str("DEEP_ARCHIVE") == StorageClass.DEEP_ARCHIVE
        assert StorageClass.from_str("GLACIER_IR") == StorageClass.GLACIER_IR

    def test_from_str_defaults_to_standard(self):
        """Test unknown strings default to STANDARD."""
        assert StorageClass.from_str("unknown") == StorageClass.STANDARD
        assert StorageClass.from_str("") == StorageClass.STANDARD

    def test_from_any_with_storageclass(self):
        """Test from_any with StorageClass instance."""
        assert StorageClass.from_any(StorageClass.GLACIER) == StorageClass.GLACIER

    def test_from_any_with_string(self):
        """Test from_any with string."""
        assert StorageClass.from_any("STANDARD_IA") == StorageClass.STANDARD_IA
        assert StorageClass.from_any("glacier") == StorageClass.GLACIER

    def test_from_any_defaults_to_standard(self):
        """Test from_any with invalid type defaults to STANDARD."""
        assert StorageClass.from_any(123) == StorageClass.STANDARD
        assert StorageClass.from_any(None) == StorageClass.STANDARD

    def test_str_representation(self):
        """Test string representation."""
        assert str(StorageClass.GLACIER) == "GLACIER"
        assert str(StorageClass.STANDARD_IA) == "STANDARD_IA"

    def test_repr_representation(self):
        """Test repr representation."""
        assert repr(StorageClass.GLACIER) == "StorageClass.GLACIER"
        assert repr(StorageClass.DEEP_ARCHIVE) == "StorageClass.DEEP_ARCHIVE"

    def test_equality_with_string(self):
        """Test equality comparison with strings."""
        assert StorageClass.GLACIER == "glacier"
        assert StorageClass.GLACIER == "GLACIER"
        assert StorageClass.GLACIER == "Glacier"

    def test_inequality_with_string(self):
        """Test inequality comparison with strings."""
        assert StorageClass.GLACIER != "standard_ia"
        assert StorageClass.STANDARD != "glacier"

    def test_all_enum_values(self):
        """Test all enum values are defined."""
        assert StorageClass.STANDARD.value == "STANDARD"
        assert StorageClass.GLACIER.value == "GLACIER"
        assert StorageClass.STANDARD_IA.value == "STANDARD_IA"
        assert StorageClass.ONEZONE_IA.value == "ONEZONE_IA"
        assert StorageClass.INTELLIGENT_TIERING.value == "INTELLIGENT_TIERING"
        assert StorageClass.DEEP_ARCHIVE.value == "DEEP_ARCHIVE"
        assert StorageClass.GLACIER_IR.value == "GLACIER_IR"

    def test_is_transitable_for_transitable_classes(self):
        """Test is_transitable returns True for transitable classes."""
        assert StorageClass.GLACIER.is_transitable() is True
        assert StorageClass.STANDARD_IA.is_transitable() is True
        assert StorageClass.ONEZONE_IA.is_transitable() is True
        assert StorageClass.INTELLIGENT_TIERING.is_transitable() is True
        assert StorageClass.DEEP_ARCHIVE.is_transitable() is True
        assert StorageClass.GLACIER_IR.is_transitable() is True

    def test_is_transitable_for_non_transitable_classes(self):
        """Test is_transitable returns False for non-transitable classes."""
        assert StorageClass.STANDARD.is_transitable() is False

    def test_is_non_transitable_for_standard(self):
        """Test is_non_transitable returns True for STANDARD."""
        assert StorageClass.STANDARD.is_non_transitable() is True

    def test_is_non_transitable_for_transitable_classes(self):
        """Test is_non_transitable returns False for transitable classes."""
        assert StorageClass.GLACIER.is_non_transitable() is False
        assert StorageClass.STANDARD_IA.is_non_transitable() is False
        assert StorageClass.ONEZONE_IA.is_non_transitable() is False
